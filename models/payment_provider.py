# -*- coding: utf-8 -*-
import requests
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('multisafepay', "MultiSafePay")],
                            ondelete={'multisafepay': 'set default'})
    multisafepay_merchant_account = fields.Char(string="Merchant Account", groups='base.group_system',
                                                required_if_provider='multisafepay')
    multisafepay_security_code = fields.Char(string="Security Code", groups='base.group_system',
                                             required_if_provider='multisafepay')
    multisafepay_api_key = fields.Char(string="API Key", groups='base.group_system',
                                       required_if_provider='multisafepay')

    def _multisafepay_get_api_url(self):
        """ Return the API URL according to the provider state. """
        self.ensure_one()

        if self.state == 'enabled':
            return 'https://api.multisafepay.com/v1/json/'
        else:
            return f'https://testapi.multisafepay.com/v1/json/orders?api_key={self.multisafepay_api_key}'

    def _multisafepay_make_request(self, json=None):
        """ Make a request to Multisafepay API at the specified endpoint. """
        url = self._multisafepay_get_api_url()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        try:
            response = requests.post(url, headers=headers, json=json, timeout=60)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ValidationError(
                    "MultiSafepay: " + _("The communication with the API failed. Details: %s")
                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise ValidationError("MultiSafepay: " + _("Could not establish the connection to the API."))
        return response.json()

