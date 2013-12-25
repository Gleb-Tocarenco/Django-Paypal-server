# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_UP

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from paypal.driver import PayPal
from paypal.models import PayPalResponse
from paypal.utils import process_payment_request, process_refund_request

def setcheckout(request, return_url, cancel_url, error_url, template = "paypal/setcheckout.html", currency = "USD"):
  
    itemprice = request.GET.get('price','17')
    itemname = request.GET.get('name','test')
    itemdesc = request.GET.get('desc','test')
    request.session['AMT'] = itemprice
   
    if request.POST:
        # normalize the given amount
        amount = itemprice
        
        try:
            amount = Decimal(amount)
            amount = str(amount.quantize(Decimal(".01"), rounding = ROUND_UP))
        except:
            if request.user.is_authenticated():
                request.user.message_set.create(message = _("No given valid amount. Please check the amount that will be charged."))
            return HttpResponseRedirect(error_url)
        kwargs = {
        "ItemName" : itemname,
        "ItemDesctription": itemdesc
        }
        # call the PayPal driver (2)
        driver = PayPal()
        # call the relevant API method (3)
        result = driver.SetExpressCheckout(amount, currency, return_url, cancel_url,**kwargs)
        # perform the response (4)
        if not result:
            print driver.apierror
            # show the error message (comes from PayPal API) to the user and redirect him/her to the error page
            if request.user.is_authenticated():
                request.user.message_set.create(message = _(driver.setexpresscheckouterror))
            return HttpResponseRedirect(error_url)
        
        # send him/her to the PayPal website to check his/her order details out
        redirect_url = driver.paypal_url()
        return HttpResponseRedirect(redirect_url)
    
    return render_to_response(template,
                              {'price': itemprice,
                              'name': itemname,
                              'currency': currency,
                              'desc': itemdesc,
                               'return_url': return_url,
                               'cancel_url': cancel_url,
                               'error_url' : error_url,
                               }, context_instance = RequestContext(request))


def docheckout(request, error_url, success_url, template = "paypal/docheckout.html", currency = "USD"):
   
    
    if request.POST:
        # normalize the given amount
        amount = itemprice
        try:
            amount = Decimal(amount)
            amount = str(amount.quantize(Decimal(".01"), rounding = ROUND_UP))
        except:
            if request.user.is_authenticated():
                request.user.message_set.create(message = _("No given valid amount. Please check the amount that will be charged."))
            return HttpResponseRedirect(error_url)

        # perform GET
        token   = request.GET.get("token")

        payerid = request.GET.get("PayerID")

        # charge from PayPal
        result, response = process_payment_request(amount, currency, token, payerid)
        # process the result
        if not result:
            # show the error message (comes from PayPal API) and redirect user to the error page
            if request.user.is_authenticated():
                request.user.message_set.create(message = _("Amount %s has been successfully charged, your transaction id is '%s'" % (amount, response.error)))
            return HttpResponseRedirect(error_url)

        # Now we are gone, redirect user to success page
        if request.user.is_authenticated():
            request.user.message_set.create(message = _("Amount %s has been successfully charged, your transaction id is '%s'" % (amount, response.trans_id)))
        
        return HttpResponseRedirect(success_url)

    return render_to_response(template,
                              {'price': itemprice,
                              'error_url': error_url,
                               'success_url': success_url,
                               }, context_instance = RequestContext(request))



def dorefund(request, error_url, success_url, template = "paypal/dorefund.html"):
    if request.POST:
        # normalize the given amount
        amount = request.POST.get("amount")
        trans_id = request.POST.get("transactionid")
        try:
            amount = Decimal(amount)
            amount = str(amount.quantize(Decimal(".01"), rounding = ROUND_UP))
        except:
            if request.user.is_authenticated():
                request.user.message_set.create(message = _("No given valid amount. Please check the amount that will be charged."))
            return HttpResponseRedirect(error_url)
        
        response_obj = get_object_or_404(PayPalResponse, trans_id = trans_id)
        
        # charge from PayPal
        result, response = process_refund_request(response_obj, amount)
        # process the result
        if not result:
            # show the error message (comes from PayPal API) and redirect user to the error page
            if request.user.is_authenticated():
                request.user.message_set.create(message = _("Amount %s has not been charged, server error is '%s'" % (amount, response.error)))
            return HttpResponseRedirect(error_url)
        
        # Now we are gone, redirect user to success page
        if request.user.is_authenticated():
            request.user.message_set.create(message = _("Amount %s has been successfully refunded, your transaction id is '%s'" % (amount, response.trans_id)))
        
        return HttpResponseRedirect(success_url)

    return render_to_response(template,
                              {'error_url': error_url,
                               'success_url': success_url,
                               }, context_instance = RequestContext(request))
