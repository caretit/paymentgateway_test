# -*- coding: utf-8 -*-
# Copyright (c) 2022-Present Mentis Consultancy Services. (<https://mcss.odoo.com>)

import json
import requests
from base64 import b64encode
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.addons.payment_mastercard_mpgs.controllers.main import MastercardController


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    @api.model
    def _get_user_currency(self):
        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
        return currency_id or self._get_euro()

    code = fields.Selection(selection_add=[('mastercard', 'Mastercard(MPGS)')], ondelete={'mastercard': 'set default'})
    merchant_id = fields.Char(string='Merchant ID', required_if_provider='mastercard')
    password = fields.Char(string='Password', required_if_provider='mastercard')
    payment_method = fields.Selection([('lightbox', 'Lightbox'), ('payment_page', 'Payment Page')], string='Method', required_if_provider='mastercard', default='lightbox')
    mpgs_region = fields.Selection([('na', 'Americas'), ('ap', 'Asia Pacific'), ('eu', 'Europe OR Middle East and Africa')], string='Region', required_if_provider='mastercard', default='ap')
    mpgs_currency = fields.Many2one('res.currency', required_if_provider='mastercard', groups='base.group_system', default=lambda self: self._get_user_currency())

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Mastercard(MPGS) providers when the currency is not as expected """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency:
            providers = providers.filtered(
                lambda a: a.code == 'mastercard' and currency in a.mpgs_currency
            )
            if not providers:
                providers = providers.filtered(
                    lambda a: a.code != 'mastercard'
                )

        return providers

    def _mastercard_get_api_url(self):
        self.ensure_one()
        if self.state == 'test':
            return 'https://test-gateway.mastercard.com/api/rest/version/62/merchant/%s/session' % self.sudo().merchant_id
        else:
            return "https://%s-gateway.mastercard.com/api/rest/version/62/merchant/%s/session" % (self.sudo().mpgs_region, self.sudo().merchant_id)

    def get_mastercard_checkout_session(self, values):
        currency = self.env['res.currency'].sudo().browse(values.get('currency_id'))
        session_data = {
            'merchant_id': self.sudo().merchant_id,
            'amount': '%.3f' % values.get('amount'),
            'currency': currency.name,
            'description': values.get('reference'),
            'reference': values.get('reference'),
            'partner_address': values.get('partner_address'),
            'partner_city': values.get('partner_city'),
            'partner_zip': values.get('partner_zip'),
            'partner_state': values.get('partner_state'),
            'email': values.get('partner_email'),
            'phone': values.get('partner_phone'),
            'name': self.sudo().company_id.display_name,
            'payment_method': self.sudo().payment_method
        }
        base_url = self.get_base_url()
        data = {
            'apiOperation': 'CREATE_CHECKOUT_SESSION',
            'order': {
                'id': values.get('reference'),
                'amount': '%.3f' % values.get('amount'),
                'currency': currency.name
            },
            'customer': {
                'email': values.get('partner_email'),
                'phone': values.get('partner_phone'),
            },
            'interaction': {
                'operation': 'PURCHASE',
                'cancelUrl': urls.url_join(base_url, MastercardController._cancel_url + "?reference=%s" % values['reference']),
                'returnUrl': urls.url_join(base_url, MastercardController._return_url + "?reference=%s" % values['reference']),
            }
        }
        if self.state == 'test':
            url = 'https://test-gateway.mastercard.com/api/rest/version/62/merchant/%s/session' % self.sudo().merchant_id
        else:
            url = "https://%s-gateway.mastercard.com/api/rest/version/62/merchant/%s/session" % (self.sudo().mpgs_region, self.sudo().merchant_id)
        headers = {
            'Authorization': 'Basic %s' % b64encode(('%s:%s' % ('merchant.' + self.sudo().merchant_id, self.sudo().password)).encode('utf-8')).decode("utf-8")
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        res = response.json()
        if res.get('error'):
            raise ValueError(_("MPGS giving the error as: %s" % res['error']['explanation']))
        if res.get('session'):
            if res.get('session').get('id'):
                session_data['id'] = res.get('session').get('id')
            if res.get('session').get('version'):
                session_data['version'] = res.get('session').get('version')
        return session_data
