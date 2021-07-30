/* Copyright 2018 Camptocamp
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define('web_odoo_send_notify.notification', function (require) {
    "use strict";

    var base_notification = require('web.Notification');
    var WebClient = require('web.WebClient');
        Notification = base_notification;

    var InteractiveNotification = Notification.extend({
        template: 'InteractiveNotification',
        events: _.extend(
            {},
            Notification.prototype.events,
            {'click .o_notification_reload_view': function(e){
                e.preventDefault();
                this.reload_active_view();
            },
             'click .o_notification_do_action': function(e){
                 e.preventDefault();
                 this.button_do_action();
             }
            }
        ),
        init: function(parent, title, text, options) {
            this.options = options || {};
            var sticky = this.options.sticky;
            this._super.apply(this, [parent, title, text, sticky]);
        },
        reload_active_view: function() {
            this.trigger_up('reload_active_view');
        },
        button_do_action: function() {
            this.getParent().do_action(this.options.action);
        },
        interactive_notify(title, text, options) { //Se elimino la clase NotificationManager. y ahora solo hay la funcion notify
            return this.display(new InteractiveNotification(this, title, text, options));
        },
    });
    Notification.include({
        icon_mapping: {
            'success': 'fa-thumbs-up',
            'danger': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation',
            'info': 'fa-info',
            'default': 'fa-lightbulb-o',
        },
        init: function () {
            this._super.apply(this, arguments);
            // Delete default classes
            this.className = this.className.replace(' o_error', '');
            // Add custom icon and custom class
            this.icon = (this.type in this.icon_mapping) ?
                this.icon_mapping[this.type] :
                this.icon_mapping['default'];
            this.className += ' o_' + this.type;
        },
    });

    return {
        InteractiveNotification: InteractiveNotification,
    };

});
