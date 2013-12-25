

import urllib, md5, datetime
from cgi import parse_qs
from django.conf import settings

# Exception messages

TOKEN_NOT_FOUND_ERROR = "PayPal error occured. There is no TOKEN info to finish performing PayPal payment process. We haven't charged your money yet."
NO_PAYERID_ERROR = "PayPal error occured. There is no PAYERID info to finish performing PayPal payment process. We haven't charged your money yet."
GENERIC_PAYPAL_ERROR = "There occured an error while performing PayPal checkout process. We apologize for the inconvenience. We haven't charged your money yet."
GENERIC_PAYMENT_ERROR = "Transaction failed. Check out your order details again."
GENERIC_REFUND_ERROR = "An error occured, we can not perform your refund request"

class PayPal(object):
  
    
    def __init__(self, debug = True):
       
        
        
        self.username  = "gleb.tocarenco-facilitator_api1.gmail.com"
        self.password  = "1369414581"
        self.sign = "ADpPBWe3W7hQC8qIihMtiGS8MOtrAivD0qTme-d.SrasU2XD9zm.TC9y"
        
        self.credientials = {
            "USER" : self.username,
            "PWD" : self.password,
            "SIGNATURE" : self.sign,
            "VERSION" : "53.0",
        }
        # Second step is to set the API end point and redirect urls correctly.
        
        self.NVP_API_ENDPOINT    = "https://api-3t.sandbox.paypal.com/nvp"
        self.PAYPAL_REDIRECT_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="
        

        # initialization
        self.signature = urllib.urlencode(self.credientials) + '&'
        self.setexpresscheckouterror = None
        self.getexpresscheckoutdetailserror = None
        self.doexpresscheckoutpaymenterror = None
        self.refundtransactionerror = None
        self.apierror = None
        self.api_response = None
        self.token = None
        self.response = None
        self.refund_response = None
        self.amount = None

    def _get_value_from_qs(self, qs, value):
        
        raw = qs.get(value)
        if type(raw) == list:
            try:
                return raw[0]
            except KeyError:
                return None
        else:
            return raw


    def paypal_url(self, token = None):
        
        token = token if token is not None else self.token
        
        if not token:
            return None
        
        return self.PAYPAL_REDIRECT_URL + token 



    def SetExpressCheckout(self, amount, currency, return_url, cancel_url, **kwargs):
       
        parameters = {
            'METHOD' : 'SetExpressCheckout',
            'NOSHIPPING' : 1,
            'PAYMENTACTION' : 'Sale',
            'RETURNURL' : return_url,
            'CANCELURL' : cancel_url,
            'AMT' : amount,
            'CURRENCYCODE' : currency,
        }
        
        parameters.update(kwargs)
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_dict = parse_qs(response)
        self.api_response = response_dict
        
        state = self._get_value_from_qs(response_dict, "ACK")
        if state in ["Success", "SuccessWithWarning"]:
            self.token = self._get_value_from_qs(response_dict, "TOKEN")
            return True

        self.setexpresscheckouterror = GENERIC_PAYPAL_ERROR
        self.apierror = self._get_value_from_qs(response_dict, "L_LONGMESSAGE0")
        return False





    





    def GetExpressCheckoutDetails(self, return_url, cancel_url, token = None):
       
        token = self.token if token is None else token
        if token is None:
            self.getexpresscheckoutdetails = TOKEN_NOT_FOUND_ERROR
            return False

        parameters = {
            'METHOD' : "GetExpressCheckoutDetails",
            'RETURNURL' : return_url,
            'CANCELURL' : cancel_url,
            'TOKEN' : token,
        }
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_dict = parse_qs(response)
        self.api_response = response_dict
        state = self._get_value_from_qs(response_dict, "ACK")
        if not state in ["Success", "SuccessWithWarning"]:
            self.getexpresscheckoutdetailserror = self._get_value_from_qs(response_dict, "L_SHORTMESSAGE0")
            self.apierror = self.getexpresscheckoutdetailserror
            return False

        return True




    def DoExpressCheckoutPayment(self, currency, amount, token = None, payerid = None):
     
        if token is None:
            self.doexpresscheckoutpaymenterror = TOKEN_NOT_FOUND_ERROR
            return False

        if payerid is None:
            self.doexpresscheckoutpaymenterror = NO_PAYERID_ERROR
            return False

        parameters = {
            'METHOD' : "DoExpressCheckoutPayment",
            'PAYMENTACTION' : 'Sale',
            'TOKEN' : token,
            'AMT' : amount,
            'CURRENCYCODE' : currency,
            'PAYERID' : payerid,
        }
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
                
        state = self._get_value_from_qs(response_tokens, "ACK")
        self.amount = self_get_value_from_qs(response_tokens,"PAYMENTREQUEST_0_AMT")
        self.response = response_tokens
        self.api_response = response_tokens
        if not state in ["Success", "SuccessWithWarning"]:
            self.doexpresscheckoutpaymenterror = GENERIC_PAYMENT_ERROR
            self.apierror = self._get_value_from_qs(response_tokens, "L_LONGMESSAGE0")
            return False
        return True




    def RefundTransaction(self, transid, refundtype, currency = None, amount = None, note = "Dummy note for refund"):
       
        if not refundtype in ["Full", "Partial"]:
            self.refundtransactionerror = "Wrong parameters given, We can not perform your refund request"
            return False
        
        parameters = {
            'METHOD' : "RefundTransaction",
            'TRANSACTIONID' : transid,
            'REFUNDTYPE' : refundtype,
        }
        
        if refundtype == "Partial":
            extra_values = {
                'AMT' : amount,
                'CURRENCYCODE' : currency,
                'NOTE' : note
            }
            parameters.update(extra_values)

        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
            
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])

        state = self._get_value_from_qs(response_tokens, "ACK")
        self.refund_response = response_tokens
        self.api_response = response_tokens
        if not state in ["Success", "SuccessWithWarning"]:
            self.refundtransactionerror = GENERIC_REFUND_ERROR
            return False
        return True


    def GetPaymentResponse(self):
        return self.response



    def GetRefundResponse(self):
        return self.refund_response

