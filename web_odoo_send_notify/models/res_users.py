# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# example use  self.env.user.notify_info('My information message')
from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action
from odoo.http import request
from odoo.modules.module import get_module_resource
from multiprocessing import Process, Queue
import requests
import base64
import json
import random
import odoo
import re
import time,  os
TAG_RE = re.compile(r'<[^>]+>')
def json_dump(v):
    return json.dumps(v, separators=(',', ':'))
class ResUsers(models.Model):
    _inherit = 'res.users'
    @api.multi
    @api.depends('create_date')
    def _compute_channel_names(self):
        for record in self:
            res_id = record.id
            record.notify_info_channel_name = 'notify_info_%s' % res_id
            record.notify_warning_channel_name = 'notify_warning_%s' % res_id
   
    notify_info_channel_name = fields.Char(compute='_compute_channel_names')
    notify_warning_channel_name = fields.Char(compute='_compute_channel_names')
    puerto_notify = fields.Char("Puerto para notificacion")
    ip_notify = fields.Char("IP para notificacion")
    
    @api.multi
    def notify_info(self, message, title=None, sticky=False,
                    show_reload=False, action=None,
                    action_link_name=None, **options):
        title = title or _('Information')
        self._notify_channel(
            'notify_info_channel_name', message, title,
            sticky=sticky, show_reload=show_reload, action=action,
            action_link_name=action_link_name, **options
        )

    @api.multi
    def notify_warning(self, message, title=None, sticky=False,
                       show_reload=False, action=None,
                       action_link_name=None, **options):
        title = title or _('Warning')
        self._notify_channel(
            'notify_warning_channel_name', message, title,
            sticky=sticky, show_reload=show_reload, action=action,
            action_link_name=action_link_name, **options
        )

    @api.multi
    def _notify_channel(self, channel_name_field, message, title, **options):
        if options.get('action'):
            options['action'] = clean_action(options['action'])
        bus_message = {
            'message': message,
            'title': title,
        }
        bus_message.update(options)
        notifications = [(getattr(record, channel_name_field), bus_message)
                         for record in self]
        self.env['bus.bus'].sendmany(notifications)

#example use
#image_path = get_module_resource('hr_fingerprint', 'static/src/img', 'correctoazul.png')
#self.env['res.user.notify']._notify_chrome("Bien!", "Se elimino con exito! numero=",  'hr_fingerprint', 'static/src/img', 'correctoazul.png' )
class SendNotifyResUsers(models.Model):
    _name = 'res.user.notify'
    _description = 'Notificaciones chrome para usuarios'
    _order = 'id'
    proccess_ids_parent = []
    status = fields.Char("Estado")
    @api.multi
    def _notify_chrome(self, puerto, title="", message="", modulo_imagen="", direc_imagen="", name_imagen=""):
        ip_user = request.httprequest #Obtiene la ip del cliente
        if  'REMOTE_ADDR' in ip_user.environ:
            ip_user_ip = ip_user.environ['REMOTE_ADDR']
            image_path = get_module_resource(modulo_imagen, direc_imagen, name_imagen)
            with open(image_path, "rb") as image_file:
                        new_url_64 = base64.b64encode(image_file.read())
            payload ={"command":"notification","data": {"type":"image", "title": title, "message":message, "iconUrl":"data:image/png;base64,"+new_url_64, "imageUrl":"data:image/png;base64,"+new_url_64}}
            # payload ={"command": "notification", "data":{"type":"basic", "title":"Bien venida Maricarmen", "message":"Hello!"}}
            response = requests.post("http://"+ip_user_ip+":"+puerto, json=payload)
    @api.multi
    def _notify_chrome_chat(self, ip, puerto, type_message, title="", message="", modulo_imagen="", direc_imagen="", name_imagen=""):
        ip_user_ip = ip
        payload ={}
        if type_message =="image":
            image_path = get_module_resource(modulo_imagen, direc_imagen, name_imagen)
            with open(image_path, "rb") as image_file:
                        new_url_64 = base64.b64encode(image_file.read())
            payload ={"command":"notification","data": {"type":"image", "title": title, "message":message, "iconUrl":"data:image/png;base64,"+new_url_64, "imageUrl":"data:image/png;base64,"+new_url_64}}
            # payload ={"command": "notification", "data":{"type":"basic", "title":"Bien venida Maricarmen", "message":"Hello!"}}
        if type_message =="basic":
            payload ={"command": "notification", "data":{"type":"basic", "title": title, "message":message}}
        try:
            #queue = Queue() #use multiproccess for no response ip
            p = Process(target=self.call_response, args=(ip_user_ip, puerto, payload))
            p.start()
            self.proccess_ids_parent.append(p.pid)
            response =""
        except requests.exceptions.RequestException as e:
            response = 'No se envio mensaje a destinatario '+str(ip_user_ip+":"+puerto)
            self.kill_subproccess()
        return response
    @api.multi  #Funcion multiproceso para cada usuario y asi si hay un error en la respuesta no frene el navegador
    def call_response(self, ip_user_ip, puerto, payload):
        try:
            k = requests.post("http://"+ip_user_ip+":"+puerto, json=payload)
        except requests.exceptions.RequestException as e:
            print (e)
            k = e
        return k
    @api.multi
    def kill_subproccess(self):
        time.sleep(2)
        for proceso_kill in self.proccess_ids_parent :
            os.system('sudo kill -9 '+str(proceso_kill))             

class Message_notify(models.Model):
    _inherit = 'mail.channel'
    @api.multi
    def _notify(self, message):
        super(Message_notify, self)._notify(message)
        b=""
        for chanel_id in message.channel_ids.channel_partner_ids:
            if chanel_id.id != message.author_id.id:
                for user_send in chanel_id.user_ids:
                    if (user_send.ip_notify!=False and user_send.puerto_notify!=False):
                        mesage_utf = u''.join((message.body)).encode('utf-8').strip()
                        message_no_html = TAG_RE.sub('', mesage_utf.decode("utf-8"))
                        b = self.env['res.user.notify']._notify_chrome_chat(user_send.ip_notify, user_send.puerto_notify, "basic", str(message.display_name), str(message_no_html))             
        return b
        