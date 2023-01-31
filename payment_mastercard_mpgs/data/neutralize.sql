-- disable mastercard(mpgs) payment provider
UPDATE payment_provider
   SET merchant_id = NULL,
       password = NULL,
       payment_method = NULL,
       mpgs_region = NULL,
       mpgs_currency = NULL;