# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning



class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('multisafepay', "MultiSafePay")], ondelete={'multisafepay': 'set default'})
    multisafepay_merchant_account = fields.Char(
        string="Merchant Account ID", help="The key solely used to identify the account with MultiSafePay",
        required_if_provider='multisafepay', groups='base.group_system')
    multisafepay_security_code = fields.Char(
        string="Security Code", required_if_provider='multisafepay', groups='base.group_system')
    multisafepay_api_key = fields.Char(
        string="API Key", required_if_provider='multisafepay', groups='base.group_system')

