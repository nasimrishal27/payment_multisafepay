# -*- coding: utf-8 -*-
from odoo import _, http
from odoo.http import request
from odoo.addons.payment import utils as payment_utils


class MultisafepayController(http.Controller):
    _redirect_url = '/payment/multisafepay/redirect'
    _webhook_url = '/payment/multisafepay/webhook/'

    @http.route(
        _redirect_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False,
        save_session=False
    )
    def multisafepay_return_from_checkout(self, **data):
        """ Process the notification data sent by MultiSafepay after redirection from checkout."""
        print(data)
        print('rrrrrrrrrrr')
        request.env['payment.transaction'].sudo()._handle_notification_data('multisafepay', data)
        return request.redirect('/payment/status')

