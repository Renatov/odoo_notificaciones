odoo.define('web_odoo_send_notify.WebClient', function (require) {
"use strict";

var core = require('web.core');
var WebClient = require('web.WebClient');
var base_bus = require('bus.BusService');
var Widget = require('web.Widget');
var Session = require('web.session');


Widget.include({
    do_interactive_notify: function(title, message, options) {
        this.trigger_up(
            'interactive_notification',
            {title: title, message: message, options: options});
    },
    do_interactive_warn: function(title, message, options) {
        this.trigger_up(
            'interactive_warning',
            {title: title, message: message, options: options});
    },
});


WebClient.include({
    custom_events: _.extend(
        {},
        WebClient.prototype.custom_events,
        {reload_active_view: 'reload_active_view',
         interactive_notification: function (e) {
             if(this.notification_manager) {
                 this.notification_manager.interactive_notify(
                     e.data.title, e.data.message, e.data.options
                 );
             }
         },
         interactive_warning: function (e) {
             if(this.notification_manager) {
                 this.notification_manager.interactive_warn(
                     e.data.title, e.data.message, e.data.options
                 );
             }
         }
        }
    ),
    init: function(parent, client_options){
        this._super(parent, client_options);
    },
    reload_active_view: function(){
        var action_manager = this.action_manager;
        if(!action_manager){
            return;
        }
        var active_view = action_manager.inner_widget.active_view;
        if(active_view) {
            active_view.controller.reload();
        }
    },
    show_application: function() {
        var res = this._super();
        this.start_polling();
        return res
    },
    on_logout: function() {
        var self = this;
        base_bus.bus.off('notification', this, this.bus_notification);
        this._super();
    },
    start_polling: function () {
        this.channel_success = 'notify_success_' + Session.uid;
        this.channel_danger = 'notify_danger_' + Session.uid;
        this.channel_warning = 'notify_warning_' + Session.uid;
        this.channel_info = 'notify_info_' + Session.uid;
        this.channel_default = 'notify_default_' + Session.uid;
        this.all_channels = [
            this.channel_success,
            this.channel_danger,
            this.channel_warning,
            this.channel_info,
            this.channel_default,
        ];
        this.call('bus_service', 'addChannel', this.channel_success);
        this.call('bus_service', 'addChannel', this.channel_danger);
        this.call('bus_service', 'addChannel', this.channel_warning);
        this.call('bus_service', 'addChannel', this.channel_info);
        this.call('bus_service', 'addChannel', this.channel_default);
        this.call(
            'bus_service', 'on', 'notification',
            this, this.bus_notification);
        this.call('bus_service', 'startPolling');
    },
   
    bus_notification: function(notifications) {
        var self = this;
        _.each(notifications, function (notification) { 
            var channel = notification[0];
            var message = notification[1];
            if (channel === self.channel_warning) {
                self.on_message_warning(message);
            } else if (channel == self.channel_info) {
                self.on_message_info(message);
            }
            if (
                self.all_channels != null &&
                self.all_channels.indexOf(channel) > -1
            ) {
                self.on_message(message);
            }
        });
       this._super(notifications);
    },
    on_message_warning: function(message){
        if(this.notification_manager) {
            this.notification_manager.do_interactive_warn(
                message.title, message.message, message
            );
        }
    },
    on_message_info: function(message){
        if(this.notification_manager) {
            this.notification_manager.do_interactive_notify(
                message.title, message.message, message
            );
        }
    },
    on_message: function (message) {
        return this.call(
            'notification', 'notify', {
                type: message.type,
                title: message.title,
                message: message.message,
                sticky: message.sticky,
                className: message.className,
            }
        );
    },
});

});
