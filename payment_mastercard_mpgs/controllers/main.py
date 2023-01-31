# -*- coding: utf-8 -*-
# Copyright (c) 2022-Present Mentis Consultancy Services. (<https://mcss.odoo.com>)

import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MastercardController(http.Controller):
    _return_url = '/payment/mastercard/return/'
    _cancel_url = '/payment/mastercard/cancel/'

    @http.route(_return_url, type='http', auth='public', csrf=False)
    def mastercard_form_return_feedback(self, **post):
        _logger.info('Mastercard(MPGS): entering form_feedback with post return data %s', pprint.pformat(post))
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'mastercard', post
        )
        tx_sudo._handle_notification_data('mastercard', post)
        return request.redirect('/payment/status')

    @http.route(_cancel_url, type='http', auth='public', csrf=False)
    def mastercard_form_cancel_feedback(self, **post):
        post.update({'status': 'CANCELLED'})
        _logger.info('Mastercard(MPGS): entering form_feedback with post cancelled data %s', pprint.pformat(post))
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'mastercard', post
        )
        tx_sudo._handle_notification_data('mastercard', post)
        return request.redirect('/payment/status')

    @http.route('/get/payment/mpgs/sessiondata', type='json', auth='public')
    def get_mpgs_session_data(self, **post):
        provider = request.env['payment.provider'].sudo().browse(int(post['values']['provider_id']))
        return provider.sudo().get_mastercard_checkout_session(post['values'])
