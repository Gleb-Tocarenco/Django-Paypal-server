


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
    
    """
    Pluggable Python PayPal Driver that implements NVP (Name Value Pair) API methods.
    There are simply 3 main methods to be executed in order to finish the PayPal payment process.
    You explicitly need to define PayPal username, password and signature in your project's settings file.
    
    Those are:
    1) SetExpressCheckout
    2) GetExpressCheckoutDetails (optional)
    3) DoExpressCheckoutPayment
    """
    
    def __init__(self, debug = False):
        # PayPal Credientials
        
        # You can use the following api credientials for DEBUGGING. (in shell)

        # First step is to get the correct credientials.
        if debug or getattr(settings, "PAYPAL_DEBUG", False):
            self.username  = "seller_1261519973_biz_api1.akinon.com"
            self.password  = "1261519978"
            self.sign = "A1.OnfcjaBVTgV6Yt.oT2VavxcyOA5FGVe-MrNf.1R1zNVAD6.MDOKZO"
        else:
            self.username  = getattr(settings, "PAYPAL_USER", None)
            self.password  = getattr(settings, "PAYPAL_PASSWORD", None)
            self.sign      = getattr(settings, "PAYPAL_SIGNATURE", None)

        self.credientials = {
            "USER" : self.username,
            "PWD" : self.password,
            "SIGNATURE" : self.sign,
            "VERSION" : "53.0",
        }
        # Second step is to set the API end point and redirect urls correctly.
        if debug or getattr(settings, "PAYPAL_DEBUG", False):
            self.NVP_API_ENDPOINT    = "https://api-3t.sandbox.paypal.com/nvp"
            self.PAYPAL_REDIRECT_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="
        else:
            self.NVP_API_ENDPOINT    = "https://api-3t.paypal.com/nvp"
            self.PAYPAL_REDIRECT_URL = "https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="

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

