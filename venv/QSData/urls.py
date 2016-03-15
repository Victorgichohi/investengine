"""getpaid URL Configuration

"""
from django.conf.urls import patterns, include, url
from app.views import *
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.models import User, Group
from django.contrib.auth import views as auth_views
from registration.backends.default.views import RegistrationView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static

from django.conf.urls import url
import app.views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('registration.backends.default.urls')),
    url('^$','app.views.index'), 
	url('^features/$','app.views.features'), 
    url('^test/$','app.views.test'), 
	url('^index/$','app.views.index'), 
	url('^wallet/$','app.views.wallet'), 
	url('^pricing/$','app.views.pricing'), 
    url('^home/$','app.views.home'),    
    url('^ipn/$','app.views.mpesaIPN'), 
    url('^paypal/done/$','app.views.paypalDone'), 
    url('^mpesa/ipn/$','app.views.mpesa'), 
    url('^stripe/ipn/$','app.views.stripeIPN'), 
    url('^simulate/ipn/$','app.views.simulateIPN'), 
    url('^choose/payment/method/$','app.views.choosePayment'),
    url('^pay/$','app.views.pay'),    

    url('^withdraw/from/getpaid/$','app.views.getPaidWithdrawal'),
    url('^withdraw/to/mpesa/$','app.views.mpesaWithdrawal'),
    url('^withdraw/to/bank/$','app.views.bankWithdrawal'),

    url('^withdraw/from/paypal/$','app.views.paypalWithdrawal'),
    url('^create/paypal/withdrawal/$','app.views.createPaypalWithdrawal'),
    url('^deposit/to/paypal/$','app.views.paypalDeposit'),
    url('^confirm/paypal/deposit/$','app.views.confirmPaypalDeposit'),
    url('^create/paypal/deposit/$','app.views.createPaypalPayment'),
    url('^pay/with/getpaid/$','app.views.payWithGetPaid'),
    url('^getpaid/payments/$','app.views.getPaidPayments'),
    url('^pay/using/getpaid/$','app.views.getPaidPayments'),
    url('^pay/order/logged/$','app.views.payOrderLogged'),
    url('^pay/order/mpesa/$','app.views.payOrderUnlogged'),
    url('^pay/with/mpesa/$','app.views.payWithMpesa'),
    url('^mpesa/payments/$','app.views.mpesaPayments'), 
    url('^confirm/mpesa/payment/$','app.views.mpesaPaymentsConfirmation'),     
    url('^pay/with/card/$','app.views.payWithCard'),
    url(r'^processpay/', 'app.views.processpay'),
    url('^check/mpesa/$','app.views.checkMpesa'),    
    url('^merchants/$','app.views.merchants'), 
    url('^deposits/$','app.views.deposits'), 
    url('^payments/$','app.views.customerPayments'),         
    url('^orders/$','app.views.orders'),
    url('^my/account/$','app.views.home'),
    ########## API ######################
    #url('^api/getpaid/payment/$','app.views.getPaidAPI'),
    url('^api/http/payment/$','app.views.httpAPI'),
    url('^choose/api/payment/method/$','app.views.chooseApiPayment'), 
    url('^pay/api/with/card/$','app.views.payApiWithCard'),
    url('^pay/api/with/mpesa/$','app.views.payApiWithMpesa'),
    url('^pay/api/with/mpesa/confirm/$','app.views.payApiWithMpesaConfirm'),    
    #url('^pay/api/with/getpaid/$','app.views.payApiWithGetPaid'),
    url('^pay/api/with/getpaid/confirm/$','app.views.payApiWithGetPaidConfirm'),

    #url(r'pay/api/with/getpaid/(?P<amount>\d+)/(?P<order>\w+)/(?P<merchantkey>\w+)/(?P<gpreturn>.*)/$',
    # 'app.views.payApiWithGetPaid', name='payApiWithGetPaid'),
    url(r'pay/api/with/getpaid/(?P<amount>.*)/(?P<order>.*)/(?P<merchantkey>.*)/(?P<gpreturn>.*)/$',
    'app.views.payApiWithGetPaid', name='payApiWithGetPaid'),

    url('^api/getpaid/payment/$','app.views.mpesaAPI'),
    url('^api/mpesa/payment/$','app.views.mpesaAPI'),    
    url('^api/card/payment/$','app.views.cardAPI'),
    ########### customers #######################
    url('^client/account/$','app.views.home'), 
    url('^dashboard/$','app.views.dashboard'),    
    url('^customers/$','app.views.customers'),    
    url('^customer/deposits/$','app.views.deposits'), 
    url('^customer/orders/$','app.views.orders'), 
    url('^customer/payments/$','app.views.customerPayments'), 
    url('^customer/withdrawals/$','app.views.withdrawals'), 
    ########## merchant ######################
    url('^merchant/account/$','app.views.merchantAccount'),  
    url('^merchant/payments/$','app.views.merchantPayments'),  
    url('^merchant/orders/$','app.views.merchantOrders'), 
    url('^merchant/withdrawals/$','app.views.merchantWithdrawals'), 
    url('^merchant/customers/$','app.views.merchantCustomers'),     
    #sessions
    url(r'session_security/', include('session_security.urls')),    
    #passwords management
    url(r'^passresetcomplete/$',auth_views.password_reset_complete,
        name='forgot_password4'),
	url(r'^password/change/$', auth_views.password_change, name='auth_password_change'),
	url(r'^password/change/done/$', auth_views.password_change_done,
        name='auth_password_change_done'), 
	#Stripe
	url(r'^payments/', include('payments.urls')),
	url(r'^stripe/','app.views.payWithCard'), 
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
