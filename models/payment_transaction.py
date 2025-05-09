# -*- coding: utf-8 -*-
import requests
from werkzeug import urls
from odoo.addons.payment_multisafepay.controller.main import MultisafepayController
from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.addons.payment.const import CURRENCY_MINOR_UNITS
from odoo.addons.payment_multisafepay import const
from odoo.addons.payment import utils as payment_utils


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return MultiSafePay-specific rendering values."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'multisafepay':
            return res
        payload = self._multisafepay_prepare_payment_request_payload()
        payment_data = self.provider_id._multisafepay_make_request( json=payload)
        self.provider_reference = payment_data.get('id')
        checkout_url = payment_data['data'].get('payment_url')
        return {'api_url': checkout_url}

    def _multisafepay_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values."""
        base_url = self.provider_id.get_base_url()
        redirect_url = urls.url_join(base_url, MultisafepayController._redirect_url)
        partner_first_name, partner_last_name = payment_utils.split_partner_name(self.partner_name)
        print(self.reference)

        return {
            "type": "redirect",
            "order_id": self.reference,
            "gateway": "",
            "currency": "EUR",
            "amount": self.amount,
            "description": self.reference,
            "payment_options": {
                "notification_url": "https://www.example.com/client/notification?type=notification",
                "notification_method": "POST",
                "redirect_url": redirect_url,
                "cancel_url": "https://www.example.com/client/notification?type=cancel",
                "close_window": True
            },
            "customer": {
                "locale": "en_US",
                "ip_address": "10.0.20.93",
                "first_name": partner_first_name,
                "last_name": partner_last_name,
                "company_name": self.provider_id.company_id.name,
                "address1": self.partner_address,
                "zip_code": self.partner_zip,
                "city": self.partner_city,
                "country": self.partner_country_id.name,
                "email": self.partner_email,
                "referrer": "https://example.com",
                "user_agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
            }
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on MultiSafePay data."""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'multisafepay' or len(tx) == 1:
            return tx
        tx = self.search([('reference', '=', notification_data.get('transactionid'))])
        if not tx:
            raise ValidationError("MultiSafepay: " + _(
                "No transaction found matching reference %s.", notification_data.get('transactionid')
            ))
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on MultiSafePay data."""
        res = super()._process_notification_data(notification_data)
        if self.provider_code != 'multisafepay':
            return res

        url = f'https://testapi.multisafepay.com/v1/json/orders/{notification_data.get('transactionid')}?api_key={self.provider_id.multisafepay_api_key}'
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        response = response.json()
        payment_status = response['data']['status']

        if payment_status == 'uncleared':
            self._set_pending()
        elif payment_status == 'initialized':
            self._set_authorized()
        elif payment_status == 'completed':
            self._set_done()
        elif payment_status in ['expired', 'canceled', 'failed']:
            self._set_canceled("MultiSafepay: " + _("Cancelled payment with status: %s", payment_status))
        else:
            self._set_error(
                "MultiSafepay: " + _("Received data with invalid payment status: %s", payment_status)
            )
