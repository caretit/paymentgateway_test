# -*- coding: utf-8 -*-
# Copyright (c) 2022-Present Mentis Consultancy Services. (<https://mcss.odoo.com>)

from . import models
from . import controllers
from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(cr, registry):
    setup_provider(cr, registry, 'mastercard')


def uninstall_hook(cr, registry):
    reset_payment_provider(cr, registry, 'mastercard')
