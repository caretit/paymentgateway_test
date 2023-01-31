# -*- coding: utf-8 -*-
# Copyright (c) 2022-Present Mentis Consultancy Services. (<https://mcss.odoo.com>)

import logging
import requests
from base64 import b64encode

from odoo import _, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_processing_values(self):
        self.ensure_one()
        processing_values = super(PaymentTransaction, self.sudo())._get_processing_values()
        processing_values.update({
            'state': self.provider_id.state,
            'partner_address': self.partner_address or None,
            'partner_city': self.partner_city or None,
            'partner_zip': self.partner_zip or None,
            'partner_state': self.partner_state_id and self.partner_state_id.name or None,
            'partner_email': self.partner_email or None,
            'partner_phone': self.partner_phone or None,
        })
        return processing_values

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Mastercard(MPGS)-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'mastercard':
            return res
        return {}

    def _get_mpgs_retrieve_order(self, order_id):
        if self.provider_id.state == 'test':
            url = 'https://test-gateway.mastercard.com/api/rest/version/62/merchant/%s/order/%s' % (self.sudo().provider_id.merchant_id, order_id)
        else:
            url = "https://%s-gateway.mastercard.com/api/rest/version/62/merchant/%s/order/%s" % (self.sudo().provider_id.mpgs_region, self.sudo().provider_id.merchant_id, order_id)
        headers = {
            'Authorization': 'Basic %s' % b64encode(('%s:%s' % ('merchant.' + self.sudo().provider_id.merchant_id, self.sudo().provider_id.password)).encode('utf-8')).decode("utf-8")
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Mastercrd(MPGS) data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'mastercard' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if not reference:
            raise ValidationError(
                "Mastercard(MPGS): " + _(
                    "Received data with missing reference %(r)s.",
                    r=reference
                )
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', provider_code)])
        if not tx:
            raise ValidationError(
                "Mastercard(MPGS): " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment' to process the transaction based on PayPlug data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data are received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'mastercard':
            return

        # if notification_data.get('status') != 'CANCELLED':
        #     print(">>>>>>>>>>>>>>>>>>>>")
        #     notification_data = self._get_mpgs_retrieve_order(self.reference)
        #     print("22222222222")

        # status = notification_data.get('status')
        self.provider_reference = self.reference
        self._set_done()
        # if status == "CAPTURED":
        #     _logger.info('Validated Mastercard(MPGS) payment for tx %s: set as done' % (self.reference))
        # elif status == "AUTHORIZED":
        #     self._set_authorized()
        #     _logger.info('Authorized Mastercard(MPGS) payment for tx %s: set as authorized' % (self.reference))
        # elif status == 'CANCELLED':
        #     self._set_canceled()
        #     _logger.info('Canclled Mastercard(MPGS) payment for tx %s: set as cancelled' % (self.reference))
        # elif status == 'FAILED':
        #     self._set_error()
        #     _logger.info('Error with Mastercard(MPGS) payment for tx %s: set as error' % (self.reference))
        # else:
        #     error = 'Received unrecognized status for Mastercard(MPGS) payment %s, set as error' % self.reference
        #     self._set_error(error)
        #     _logger.info(error)
