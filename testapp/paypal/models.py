# -*- coding: utf-8 -*-

from django.db import models
from decimal import Decimal

from django.utils.translation import ugettext as _

class PayPalResponseStatus(models.Model):
    summary = models.CharField(max_length = 32)
    
    class Meta:
        verbose_name = _("PayPal Response Status")
        verbose_name_plural = _("PayPal Response Statuses")
    
    def __unicode__(self):
        return self.summary


class PayPalResponse(models.Model):
    token = models.CharField(max_length = 256, null = True, blank = True, db_index = True)
    trans_id = models.CharField(max_length = 256, null = True, blank = True, db_index = True)
    correlation_id = models.CharField(max_length = 256, null = True, blank = True)
    response = models.CharField(max_length = 32)
    error_msg = models.CharField(max_length = 256, null = True, blank = True)
    error = models.CharField(max_length = 512, null = True, blank = True)
    currencycode = models.CharField(max_length = 32, null = True, blank = True)
    raw_response = models.TextField()
    charged = models.DecimalField(decimal_places = 2, max_digits = 7, null = True, blank = True)
    status = models.ForeignKey(PayPalResponseStatus)
    payment_received = models.BooleanField(default = False)

    class Meta:
        verbose_name = _("PayPal Response")
        verbose_name_plural = _("PayPal Responses")
        
    @staticmethod
    def get_default_status():
        ps, created = PayPalResponseStatus.objects.get_or_create(summary = _("Sale"))
        return ps


    @staticmethod
    def get_cancel_status():
        ps, created = PayPalResponseStatus.objects.get_or_create(summary = _("Refund"))
        return ps


    def fill_from_response(self, response, action = "Sale"):
       
        def get_value_from_qs(qs, value):
            raw = qs.get(value)
            if type(raw) == list:
                try:
                    return raw[0]
                except KeyError:
                    return None
            else:
                return raw

        if action == "Sale":
            self.token = get_value_from_qs(response, "TOKEN")
            self.trans_id = get_value_from_qs(response, "TRANSACTIONID")
            self.response = get_value_from_qs(response, "ACK")
            self.raw_response = str(response)
            amount = get_value_from_qs(response, "AMT")
            self.charged = Decimal(amount) if amount is not None else None
            self.correlation_id = get_value_from_qs(response, "CORRELATIONID")
            self.currencycode = get_value_from_qs(response, "CURRENCYCODE")
            self.error_msg = get_value_from_qs(response, "L_SHORTMESSAGE0")
        elif action == "Refund":
            self.trans_id = get_value_from_qs(response, "REFUNDTRANSACTIONID")
            self.response = get_value_from_qs(response, "ACK")
            amount = get_value_from_qs(response, "GROSSREFUNDAMT")
            self.charged = Decimal(amount) if amount is not None else None
            self.correlation_id = get_value_from_qs(response, "CORRELATIONID")
            self.error_msg = get_value_from_qs(response, "L_SHORTMESSAGE0")
            self.currencycode = get_value_from_qs(response, "CURRENCYCODE")
            self.raw_response = str(response)
