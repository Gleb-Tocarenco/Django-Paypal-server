# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from paypal.driver import PayPal
from paypal.models import PayPalResponse, PayPalResponseStatus

def process_payment_request(amount, currency, token, payerid):
   
    driver = PayPal()
    result = driver.DoExpressCheckoutPayment(currency = currency, amount = str(amount), token = token, payerid = payerid)

    
    paypal_response = PayPalResponse()
    paypal_response.fill_from_response(driver.GetPaymentResponse())
    paypal_response.status = PayPalResponse.get_default_status()

    if result == True:
       
        paypal_response.payment_received = True
        paypal_response.save()
        return True, paypal_response
    else:
       
        paypal_response.error = _(driver.doexpresscheckoutpaymenterror)
        paypal_response.save()
        return False, paypal_response
   


def process_refund_request(response, amount):
   
    driver = PayPal()
    result = driver.RefundTransaction(response.trans_id, refundtype = "Partial", amount = str(amount), currency = response.currencycode)
    
    # persist the response to the db with PayPalResponse instance
    paypal_response = PayPalResponse()
    paypal_response.fill_from_response(driver.GetRefundResponse(), action = "Refund")
    paypal_response.status = PayPalResponse.get_cancel_status()
    
    if result == True:
        
        paypal_response.payment_received = True
        paypal_response.save()
        return True, paypal_response
    else:
       
        paypal_response.error = _(driver.refundtransactionerror)
        paypal_response.save()
        return False, paypal_response
  
