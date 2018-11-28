# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Web odoo send notifications',
    'summary': """Send notification messages to desktop user""",
    'version': '11.0',
    'description': 'Web send Notify',
    'license': 'AGPL-3',
    'author': 'PROSEBOL',
    'website': 'https://www.prosebol.com/',
    'depends': ['base','web','bus', 'mail'],
    'data': [
        'views/web_notify.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
}
