odoo.define('payment_mastercard_mpgs.payment_form', require => {
    'use strict';

    var ajax = require('web.ajax');
    const core = require('web.core');
    const { loadJS } = require('@web/core/assets');

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const _t = core._t;

    const mastercardMixin = {

        _processMastercardPayment: function(provider, paymentOptionId, processingValues) {
            ajax.jsonRpc('/get/payment/mpgs/sessiondata', 'call', {'values': processingValues}).then(session_data => {
                Checkout.configure({
                    merchant: session_data.merchant_id,
                    order: {
                        amount: parseFloat(session_data.amount),
                        currency: session_data.currency,
                        description: session_data.reference,
                        id: session_data.reference,
                        reference: session_data.reference,
                    },
                    transaction: {
                        reference: session_data.reference,
                    },
                    billing: {
                        address: {
                            street: session_data.partner_address,
                            city: session_data.partner_city,
                            postcodeZip: session_data.partner_zip,
                            stateProvince: session_data.partner_state
                        }
                    },
                    customer: {
                        email: session_data.partner_email,
                        phone: session_data.partner_phone,
                    },
                    interaction: {
                        merchant: {
                            name: session_data.name,
                        },
                    },
                    session: {
                        id: session_data.id,
                        version: session_data.version
                    },
                });
                if (session_data.payment_method == 'payment_page') {
                    Checkout.showPaymentPage();
                } else {
                    Checkout.showLightbox();
                }
            }).guardedCatch(error => {
                this._displayError(
                    _t("Server Error"),
                    _t("We are not able to process your payment."),
                    error.message.data.message
                );
            });

        },

        /**
         * Redirect the customer to Mastercard(MPGS) payment page OR via Mastercard(MPGS) POPUP.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} provider - The provider of the payment option's provider
         * @param {number} paymentOptionId - The id of the payment option handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {undefined}
         */
        _processRedirectPayment: function(provider, paymentOptionId, processingValues) {
            if (provider !== 'mastercard') {
                return this._super(...arguments);
            }
            var url = 'https://ap-gateway.mastercard.com/checkout/version/62/checkout.js';
            if (processingValues.state == 'test') {
                var url = 'https://test-gateway.mastercard.com/checkout/version/62/checkout.js'
            }
            loadJS(url);
            this._processMastercardPayment(provider, paymentOptionId, processingValues);
        }
    };

    checkoutForm.include(mastercardMixin);
    manageForm.include(mastercardMixin);

});