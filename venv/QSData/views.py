# VK Maraba
# March 2015
# @ Copyright -  vincentmaraba@gmail.com
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.shortcuts import render_to_response,redirect
from django.core.urlresolvers import reverse
#from django.utils.simplejson import JSONEncoder
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core import serializers
from django.template import Context
from django.core.cache import cache
from django.forms import ModelForm
from django.db import transaction
from django.db import connection
from decimal import Decimal
from reconcile import *
from models import *
import datetime
import time
import json, ast
import stripe
from django.utils import timezone
import paypalrestsdk
from paypalrestsdk import Payout, ResourceNotFound
import random
import string
import logging
from suds.client import Client
from datetime import date
import pycurl
from StringIO import StringIO
from django.core.urlresolvers import reverse
from urllib import urlencode
from django.db.models import Avg, Max, Min,Sum,Count
from django.db import connection


logging.basicConfig(level=logging.INFO)

paypalrestsdk.configure({
  "mode": "sandbox", # live
  "client_id": "ARIciJubbNP1XDGIxAZlgFwtFPKqcqYNxUvfkcKnyk5o9gL2by5bDh2IHjai7dTdOVApi8E5lSe9DGLM",
  "client_secret": "EBKindIIc2TBRR58RBhHTEaNyB5vVKLjs7Gr5Y6vhUc9tfc7INzyVNPoAHk6wwOVo5uzkx1a2pMqJy3v"})
  #"client_id": "AcTAWB2JterafBAjX78GZCppuKMuTktXx4iDG5g5TC4rNude_ed1-nxCDiZnS0Nq_rnfaHChAS4rS_rA",
  #"client_secret": "EEO0vpmwrF1efRRp9KT_5n8zJkiLqpG1vJ-QeLxQFQ18mS8n8d0gxMcRWqg_thewVGcKhL8T6cpzA-Aeq"})


headers = dict( SOAPAction = 'https://www.safaricom.co.ke/IPN/IpnWebRetrieval/' )
host = "https://www.safaricom.co.ke/ipn/IpnWebRetrieval"
url_service = 'https://www.safaricom.co.ke/ipn/IpnWebRetrieval?wsdl'
#There is a bug here
#client = Client(url_service,headers=headers,location=host)

from django.views.generic import DetailView
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.models import User

'''
from .models import UserProfile, assure_user_profile_exists

class UserProfileDetail(DetailView):
    model = UserProfile

class UserProfileUpdate(UpdateView):
    model = UserProfile
    fields = ('homepage',)

    def get(self, request, *args, **kwargs):
        assure_user_profile_exists(kwargs['pk'])
        return (super(UserProfileUpdate, self).
                get(self, request, *args, **kwargs))
'''

def login(request):
	return HttpResponseRedirect('/accounts/register/')


def index(request):	
	return render_to_response('Home.html', locals(), RequestContext(request))

def wallet(request):	
	return render_to_response('Wallet.html', locals(), RequestContext(request))

def pricing(request):	
	return render_to_response('Pricing.html', locals(), RequestContext(request))

def features(request):	
	return render_to_response('Features.html', locals(), RequestContext(request))


@csrf_exempt	
def test(request):
	return render_to_response('test.html', locals(), RequestContext(request))	

@csrf_exempt	
def signup(request):
	a = True
	if a:
	#try:
		if request.method == 'POST':
			username = request.POST['username']	
			email = request.POST['email']	
			#number = request.POST['number']	
			password = request.POST['password']	
			#url = request.POST['url']

			user = User.objects.create_user(username=username,password=password)
				
			#user = User.objects.create_user(username=username,password=password,
			#	first_name=username,email=email)
			'''
			customer = Customer()
			customer.name = username
			customer.phone_number = number
			customer.user = user
			customer.date_added = timezone.now()			
			customer.save()	
			'''
			
		else:		
			print 'a'
	#except:
	#	print 'Error'
	return render_to_response('signup.html', locals(), RequestContext(request))	
	
	
def home(request):
	a=True	
	value = render_to_response('deposits.html', locals(), RequestContext(request))	
	#if a:
	try:
		ismerchant = False
		isstaff = False
		iscustomer = True
		client_account = False
		request.session['user'] = request.user.id
		request.session['iscustomer'] = iscustomer
		request.session['isstaff'] = isstaff
		request.session['ismerchant'] = ismerchant
		request.session['client_account'] = client_account
		
		myuser = request.session['user']
		customerprofile = Customer.objects.get(user=myuser)		
		#customerprofile = Customer.objects.filter(user=user)[0]
		#deposits = Transaction.objects.filter(transaction_type='1',credit=True,
		#	customer=customerprofile)
		print customerprofile.client_account
		request.session['customerprofile'] = customerprofile.id
		if request.user.is_staff:
			isstaff = 1
			request.session['isstaff'] = isstaff
			isstaff = request.session['isstaff']
			#value = render_to_response('index.html', locals(), RequestContext(request))
		if customerprofile.merchant_account == True:
			ismerchant = True
			request.session['ismerchant'] = ismerchant
			ismerchant = request.session['ismerchant'] 
			#Orders = Order.objects.all()
			#value = render_to_response('orders.html', locals(), RequestContext(request))
		if customerprofile.client_account == True:
			client_account = True
			request.session['client_account'] = client_account
			iscustomer = request.session['client_account'] 
			print 'client'
			#value = render_to_response('deposits.html', locals(), RequestContext(request))	
		value = render_to_response('dashboard.html', locals(), RequestContext(request))			
	#else:						
	except:
		error = "You have not created a profile"
		value = HttpResponseRedirect('/choose/payment/method/')			
	return value


@csrf_exempt
def choosePayment(request):
	a = True
	print '1'
	if a:
	#try:
		print '2'
		if request.method == 'POST':
			a = True
			print '3'
			#if a:
			try:
				print 'a'
				method = request.POST['method']	
				Ordernumber = request.POST['Ordernumber']
				amount = request.POST['amount']	
				websitekey = request.POST['websitekey']
				currency = request.POST['currency']				
				merchant = Merchant.objects.get(website_key=websitekey)
				merchant_name = merchant.name
				merchant_id = merchant.id
				request.session['amount'] = amount
				request.session['websitekey'] = websitekey				
				request.session['Ordernumber'] = Ordernumber
				request.session['currency'] = currency			
				if method == 'mpesa':
					print 'a'
					#return HttpResponseRedirect('/pay/order/mpesa/')
					return render_to_response('pay_order_mpesa.html', locals(), 
						RequestContext(request))	
				elif method == 'card':
					return HttpResponseRedirect('/pay/with/card/')
					#return render_to_response('stripe.html', locals(), RequestContext(request))
				elif method == 'getpaid':										
					return HttpResponseRedirect('/pay/with/getpaid/')	
				else:
					#return HttpResponseRedirect('/pay/')	
					return render_to_response('choose_checkout.html', locals(), 
						RequestContext(request))	
			except:	
			#else:
				method = request.POST['method']	
				if method == 'mpesa':
					print 'a'
					#return HttpResponseRedirect('/pay/order/mpesa/')
					merchants = Merchant.objects.all()
					return render_to_response('pay_order_mpesa_new.html', locals(), 
						RequestContext(request))	
				elif method == 'card':
					return HttpResponseRedirect('/pay/with/card/')
					#return render_to_response('stripe.html', locals(), RequestContext(request))
				elif method == 'getpaid':	
					return HttpResponseRedirect('/getpaid/payments/')	
				else:
					#return HttpResponseRedirect('/pay/')	
					return render_to_response('choose_checkout.html', locals(), 
						RequestContext(request))	
				return render_to_response('choose_checkout.html', locals(), 
					RequestContext(request))	
		else:
			return render_to_response('choose_checkout.html', locals(), 
				RequestContext(request))
	#except:	
	else:
		#try:
		if a:
			websitekey = request.POST['websitekey']
			request.session['websitekey'] = websitekey
			amount = request.POST['amount']
			request.session['amount'] = amount
			currency = request.POST['currency']
			request.session['currency'] = currency
			Ordernumber = request.POST['Ordernumber']
			request.session['Ordernumber'] = Ordernumber
			signature = request.POST['signature']
			request.session['signature'] = signature
			test = request.POST['test']
			request.session['test'] = test
			culture = request.POST['culture']
			request.session['culture'] = culture
			Brq_return = request.POST['Brq_return']
			request.session['Brq_return'] = Brq_return
			Brq_returncancel = request.POST['Brq_returncancel']
			request.session['Brq_returncancel'] = Brq_returncancel
			Brq_returnerror = request.POST['Brq_returnerror']
			request.session['Brq_returnerror'] = Brq_returnerror
			Brq_returnreject = request.POST['Brq_returnreject']
			request.session['Brq_returnreject'] = Brq_returnreject
		#except:
		else:
			print 'error'
			if method == 'mpesa':
				#return HttpResponseRedirect('/pay/order/mpesa/')
				return render_to_response('pay_order_mpesa.html', locals(), 
					RequestContext(request))	
			elif method == 'card':
				return HttpResponseRedirect('/pay/with/card/')
				#return render_to_response('stripe.html', locals(), RequestContext(request))
			elif method == 'getpaid':										
				return HttpResponseRedirect('/getpaid/payments/')	
			else:
				#return HttpResponseRedirect('/pay/')	
				return render_to_response('choose_checkout.html', locals(), 
					RequestContext(request))	
		return render_to_response('choose_checkout.html', locals(), 
			RequestContext(request))


@csrf_exempt
def choosePayment3(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	if request.method == 'POST':
		method = request.POST['method']
		if method == 'mpesa':
			return HttpResponseRedirect('/pay/order/mpesa/')			
		else:
			return HttpResponseRedirect('/pay/')			
	else:		
		return render_to_response('choose_payment.html', locals(), 
			RequestContext(request))

		
def choosePayment2(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass 
	if request.method == 'POST':

		method = request.POST['method']
		websitekey = str(websitekey.strip())
		merchant = Merchant.objects.filter(website_key=websitekey)[0]		
		if method == 'mpesa':			
			return render_to_response('pay_order_mpesa2.html', locals(),
			 RequestContext(request))	
			#return HttpResponseRedirect('/pay/order/mpesa/')			
		else:
			#return HttpResponseRedirect('/pay/')
			return render_to_response('pay_order_getpaid.html', locals(), 
				RequestContext(request))				
	else:		
		return render_to_response('choose_payment.html', locals(), 
			RequestContext(request))		
				
######### General ###############

######### Staff User ###############		
@login_required	
def merchants(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass 
	merchants = Merchant.objects.all()
	return render_to_response('merchants.html', locals(), RequestContext(request))	

@login_required		
def deposits(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	deposits = Transaction.objects.filter(transaction_type='1',credit=True)
	return render_to_response('deposits.html', locals(), RequestContext(request))		
	
@login_required	
def customerPayments(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	payments = Transaction.objects.filter(transaction_type='4',debit=True)
	return render_to_response('payments.html', locals(), RequestContext(request))		

	
@login_required		
def withdrawals(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
		withdrawals = Transaction.objects.filter(transaction_type='3',debit=True)
	except:
		print 'Error'
	return render_to_response('merchant_withdrawals.html', locals(), 
		RequestContext(request))			

@login_required		
def orders(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass 
	orders = Order.objects.all()
	return render_to_response('orders.html', locals(), RequestContext(request))		


@login_required		
def dashboard(request):	
	a = True
	if a:
	#try:
		

		total_transactions = Transaction.objects.count()
		average = Transaction.objects.filter(transaction_type='4').aggregate(Avg('amount'))
		payment_received =  Transaction.objects.filter(transaction_type='4',credit=True).aggregate(Sum('amount'))
		payment_made =  Transaction.objects.filter(transaction_type='4',debit=True).aggregate(Sum('amount'))
		all_payment =  Transaction.objects.filter(transaction_type='4').aggregate(Sum('amount'))

		average = average['amount__avg']

		average = round(average,2)
		print payment_received
		print payment_made
		print total_transactions
		print average
		print all_payment

		print 'Stats'
		DEFAULT_VALUE = Decimal(0.00)

		mpesa_deposit = Transaction.objects.filter(transaction_type='1').aggregate(Sum('amount'))['amount__sum']
		mpesa_withdrawal = Transaction.objects.filter(transaction_type='3').aggregate(Sum('amount'))['amount__sum']
		bank_withdrawal = Transaction.objects.filter(transaction_type='8').aggregate(Sum('amount'))['amount__sum']
		bill_payment = Transaction.objects.filter(transaction_type='4').aggregate(Sum('amount'))['amount__sum']
		paypal_withdrawal = Transaction.objects.filter(transaction_type='9').aggregate(Sum('amount'))['amount__sum']
		paypal_deposit = Transaction.objects.filter(transaction_type='7').aggregate(Sum('amount'))['amount__sum']

		if mpesa_deposit is None:
			mpesa_deposit = DEFAULT_VALUE
		if mpesa_withdrawal is None:
			mpesa_withdrawal = DEFAULT_VALUE
		if bank_withdrawal is None:
			bank_withdrawal = DEFAULT_VALUE
		if bill_payment is None:
			bill_payment = DEFAULT_VALUE
		if paypal_withdrawal is None:
			paypal_withdrawal = DEFAULT_VALUE
		if paypal_deposit is None:
			paypal_deposit = DEFAULT_VALUE
			
		print mpesa_deposit
		print mpesa_withdrawal
		print bank_withdrawal
		print bill_payment
		print paypal_withdrawal
		print paypal_deposit

		total_stats = mpesa_deposit + mpesa_withdrawal + bank_withdrawal + bill_payment + paypal_withdrawal + paypal_deposit

		per_mpesa_deposit = round(float((mpesa_deposit/total_stats) * 100 ),2)
		per_mpesa_withdrawal = round(float((mpesa_withdrawal/total_stats) * 100 ),2)
		per_bank_withdrawal = round(float((bank_withdrawal/total_stats) * 100 ),2)
		per_bill_payment = round(float((bill_payment/total_stats) * 100 ),2)
		per_paypal_withdrawal = round(float((paypal_withdrawal/total_stats) * 100 ),2)
		per_paypal_deposit = round(float((paypal_deposit/total_stats) * 100 ),2)

		print per_mpesa_deposit
		print per_mpesa_withdrawal
		print per_bank_withdrawal
		print per_bill_payment
		print per_paypal_withdrawal
		print per_paypal_deposit

		# Data for Piechart
		pie_mpesa_deposit = round(float((mpesa_deposit/total_stats) * 360 ),2)
		pie_mpesa_withdrawal = round(float((mpesa_withdrawal/total_stats) * 360 ),2)
		pie_bank_withdrawal = round(float((bank_withdrawal/total_stats) * 360 ),2)
		pie_bill_payment = round(float((bill_payment/total_stats) * 360 ),2)
		pie_paypal_withdrawal = round(float((paypal_withdrawal/total_stats) * 100 ),2)
		pie_paypal_deposit = round(float((paypal_deposit/total_stats) * 360 ),2)

		#Monthly reports
		truncate_date = connection.ops.date_trunc_sql('month', 'date_added')
		qs = Transaction.objects.filter(debit=True).extra({'month':truncate_date})
		debit_report = qs.values('month').annotate(Sum('amount'), Count('pk')).order_by('month')
		qs = Transaction.objects.filter(credit=True).extra({'month':truncate_date})
		credit_report = qs.values('month').annotate(Sum('amount'), Count('pk')).order_by('month')


		#print debit_report
		#print credit_report

		dbt = []
		amount = 0.00
		for i in  debit_report:
			#print i['amount__sum']
			#print i['month']
			amount = float(i['amount__sum'])
			month = str(i['month'])
			
			month = month.split('-', 2 )

			#print amount
			#print month
			year = int(month[0])
			mnth = int(month[1])
			day = int(month[2])

			import datetime

			month = datetime.datetime(year,mnth,day)

			#month = int(time.mktime(month.timetuple()) * 1000)

			epoch = datetime.datetime.utcfromtimestamp(0)

			def unix_time_millis(dt):
			    return (dt - epoch).total_seconds() * 1000.0

			month = unix_time_millis(month)


			print month

			dt = [month,amount]

			dbt.append(dt)

		print 'dbt'
		print dbt
		crdt = []
		amount = 0.00
		for i in  credit_report:
			#print i['amount__sum']
			#print i['month']
			amount = float(i['amount__sum'])
			month = str(i['month'])
			
			month = month.split('-', 2 )

			#print amount
			#print month
			year = int(month[0])
			mnth = int(month[1])
			day = int(month[2])

			import datetime

			month = datetime.datetime(year,mnth,day)

			#month = month.time() * 1000
			#month = int(time.mktime(month.timetuple()) * 1000)

			epoch = datetime.datetime.utcfromtimestamp(0)

			def unix_time_millis(dt):
			    return (dt - epoch).total_seconds() * 1000.0

			month = unix_time_millis(month)


			print month

			crt = [month,amount]

			crdt.append(crt)

		print 'crdt'
		print crdt



		#myuser = request.session['user']
		#iscustomer = request.session['iscustomer'] 
		#isstaff = request.session['isstaff']  
		#ismerchant = request.session['ismerchant'] 
		#except:
	else:
		pass
	return render_to_response('dash.html', locals(), RequestContext(request))
			

@login_required		
def customers(request):	
	try:
		ismerchant = False
		
		myuser = request.session['user']
		customerprofile = Customer.objects.get(user=myuser)	

		print customerprofile.client_account
		request.session['customerprofile'] = customerprofile.id
		
		if customerprofile.merchant_account == True:
			ismerchant = True

		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
	except:
		pass
	texts = Customer.objects.all()
	return render_to_response('customers.html', locals(), RequestContext(request))
			
######### Staff User ###############		


############### MPESA User ###########################	
def payOrderUnlogged(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
	except:
		pass		
	merchants = Merchant.objects.all()
	if request.method == 'POST':
		merchant = request.POST['merchant']
		order = request.POST['order']
		myamount = request.POST['amount']
		email = request.POST['email']
		name = request.POST['name']
		phone = request.POST['phone']
		return render_to_response('confirm_pay.html', locals(), 
			RequestContext(request))
	else:
		print 'get'
		merchants = Merchant.objects.all()
		return render_to_response('pay_order_mpesa.html', locals(), 
			RequestContext(request))

def payWithMpesa(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff = request.session['isstaff']  
		ismerchant = request.session['ismerchant'] 
	 
		merchants = Merchant.objects.all()
		websitekey = request.session['websitekey'] 
		amount = request.session['amount'] 
		currency = request.session['currency']
		Ordernumber = request.session['Ordernumber'] 
		signature = request.session['signature'] 
		test = request.session['test'] 
		culture = request.session['culture'] 
		Brq_return = request.session['Brq_return'] 
		Brq_returncancel = request.session['Brq_returncancel'] 
		Brq_returnerror = request.session['Brq_returnerror'] 
		Brq_returnreject = request.session['Brq_returnreject'] 
		if request.method == 'POST':		
			merchant = request.POST['merchant']
			order = request.POST['order']
			myamount = request.POST['amount']
			email = request.POST['email']
			name = request.POST['name']
			phone = request.POST['phone']
			return render_to_response('confirm_pay.html', locals(), 
				RequestContext(request))
		else:
			print 'get'
			merchants = Merchant.objects.all()
	except:
		pass
	return render_to_response('payWithMpesa.html', locals(), RequestContext(request))

'''
# Set your secret key: remember to change this to your live secret key in production
		# See your keys here https://dashboard.stripe.com/account/apikeys
		stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"
		# Get the credit card details submitted by the form
		token = request.POST['stripeToken']
		# Create the charge on Stripe's servers - this will charge the user's card			
		charge = stripe.Charge.create(
			  amount=1000, # amount in cents, again
			  currency="usd",
			  source=token,
			  description="Example charge"
		)
		except stripe.error.CardError, e:
		  # The card has been declined
		  pass
'''	
'''
def payWithCard(request):
	msg = ''
	error = ''
	a= True
	if a:
	#try:	
		if request.method == 'POST':
			# Set your secret key: remember to change this to your live secret key in production
			# See your keys here https://dashboard.stripe.com/account/apikeys
			stripe.api_key = "sk_test_Rk6cp5XvZAku0dJjLaBox0yt"
			# Get the credit card details submitted by the form
			token = request.POST['stripeToken']
			#try:
			if a:
				# Create the charge on Stripe's servers - this will charge the user's card			
				charge = stripe.Charge.create(
					  amount=10, # amount in cents, again
					  currency="kes",
					  source=token,
					  description="Example charge on GetPaid"
				)
				msg = '200'
			#except stripe.error.CardError, e:
			else:
				# The card has been declined
				error = '400'
				pass
	#except:
	else:
		error = 'unexpected request type'
		pass
	print 'error'
	print error
	print 'msg'
	print msg
	return render_to_response('stripe.html', locals(), RequestContext(request))
'''


def cardAPI(request):
	mimetype = "text/plain"
	post_request = json.loads(request.body)
	a = True
	if a:
	#try:	
		#stripe.api_key = "sk_test_Rk6cp5XvZAku0dJjLaBox0yt"
		stripe.api_key = "sk_live_Y7lFlI9OYrzQE2ozjAPKj3ww"
		merchantkey = post_request['merchantkey'] 
		amount = post_request['amount'] 
		currency = post_request['currency']
		order = post_request['order']
		name = post_request['name']
		postal_code = post_request['postal_code']
		email = post_request['email']
		country = post_request['country']
		card_number = post_request['card_number']
		cvv = post_request['cvv']
		expiry = post_request['expiry']
		token = post_request['stripeToken']

		print request.POST
		print 'request.POST'
		print 'request.POST'
		print 'request.POST'
		
		log = SystemLog()
		log.activity = token
		log.save() 
		print token
		#if a:
		try:
			# Create the charge on Stripe's servers - this will charge the user's card			
			charge = stripe.Charge.create(
				  amount=140000, # amount in cents, again
				  currency="kes",
				  source=token,
				  description="Sample GetPaid charge"
			)
			log = SystemLog()
  			log.activity = 'Stripe Feedback :' + str(charge)
  			log.save()
			reply = '200'
		#else:
		except stripe.error.CardError, e:
			# The card has been declined
			reply = '400'
			#pass
	#except:
	else:
		error = 'unexpected request type'
		pass
	return HttpResponse(reply,mimetype)
	#return render_to_response('pay_with_card.html', locals(), RequestContext(request))


def payWithCard(request):
	msg = ''
	error = ''
	response_dict = {}
	a = True
	value = 'pay_with_card.html'
	if a:
	#try:	
		if request.method == 'POST':
			# Set your secret key: remember to change this to your live secret key in production
			# See your keys here https://dashboard.stripe.com/account/apikeys
			#stripe.api_key = "sk_test_Rk6cp5XvZAku0dJjLaBox0yt"
			stripe.api_key = "sk_live_Y7lFlI9OYrzQE2ozjAPKj3ww"
			# Get the credit card details submitted by the form
			'''
			amount = request.session['amount'] 
			currency = request.session['currency']
			Ordernumber = request.session['Ordernumber']
			'''
			print request.POST
			print 'request.POST'
			print 'request.POST'
			print 'request.POST'
			token = request.POST['stripeToken']
			amount = request.POST['amount']
			amount = Decimal(amount) * 100
			log = SystemLog()
  			log.activity = token
  			log.save() 
			print token
			#if a:
			try:
				# Create the charge on Stripe's servers - this will charge the user's card			
				charge = stripe.Charge.create(
					  amount=amount, # amount in cents, again
					  currency="kes",
					  source=token,
					  description="GetPaid charge"
				)
				log = SystemLog()
	  			log.activity = 'Stripe Feedback :' + str(charge)
	  			log.save()
				msg = 'You have successfully paid your order using your card. Thank you'	
				value = 'pay_with_card_complete.html'
			#else:
			except stripe.error.CardError, e:
				# The card has been declined
				response_dict.update({'error': e.message})
				print 'response_dict'
				print response_dict
				error = str(e.message)
				pass
	#except:
	else:
		error = 'Sorry your card has been declined. Please try again'
		pass
	return render_to_response(value, locals(), RequestContext(request)) 

@csrf_exempt
def stripeIPN(request):
	msg = ''
	error = ''
	reply = '200'
	status=200
	mimetype = 'text/plain'
	#try:	
	a=True
	if a:
		if request.method == 'POST':
			# Retrieve the request's body and parse it as JSON
  			#event_json = json.load(request.body)
  			event_json = request.body
  			# Do something with event_json    						
  			log = SystemLog()
  			log.activity = event_json
  			log.save()  			
	#except:
	else:
		error = 'unexpected request type'
		pass
	return HttpResponse(status)


@csrf_exempt
def paypalDone(request):
	msg = ''
	error = ''
	reply = '200'
	status= 'Thank you for doing business with us'
	mimetype = 'text/plain'
	#try:	
	a=True
	if a:
		if request.method == 'POST':
			# Retrieve the request's body and parse it as JSON
  			#event_json = json.load(request.body)
  			event_json = request.body
  			# Do something with event_json    						
  			log = SystemLog()
  			log.activity = event_json
  			log.save()  			
	#except:
	else:
		error = 'unexpected request type'
		pass
	return HttpResponse(status)

@csrf_exempt	
def checkMpesa(request):
	a = True
	if a:
	#try:
		trx = ''
		phone = ''
		merchants = Merchant.objects.all()
		if request.method == 'POST':
			merchant = request.POST['merchant']
			order = request.POST['order']
			myamount = request.POST['myamount']
			email = request.POST['email']
			name = request.POST['name']
			phone = request.POST['phone']
			mpesaphone = request.POST['mpesaphone']
			simu = '254'+ mpesaphone[1:]
			transaction = request.POST['transaction']
			trx = Transaction.objects.filter(transaction_code=transaction,
				phone_number=simu,successful=False,transaction_type=1)	
			if trx:		
				trxid = transactionCode()
				customer = Customer.objects.filter(phone_number=simu)
				customer = customer[0]
				customer_ref = customer.id	
				try:
					result = recon(order,myamount,trxid,customer_ref,trxid,name)
					Transaction.objects.filter(transaction_code=transaction,
						phone_number=simu,\
					successful=False,transaction_type=1).update(successful=True)	
					trans = Transaction()
					trans.transaction_id = trxid
					trans.customer = customer
					#trans.phone_number = phone_number #mpesa_msisdn
					trans.successful = True
					trans.requested = True
					trans.amount = myamount 
					trans.transaction_type = '4'
					trans.debit = True
					trans.transaction_code = trxid
					trans.business_number = BusinessNumber.objects.get(id=1)
					trans.account = order #mpesa_acc
					trans.date_added = timezone.now()
					trans.transaction_date = timezone.now() #mpesa_trx_date
					trans.save()						
								
					result = result.content
					if result == '404':
						merchant = Merchant.objects.filter(id=merchant)
						error = 'The Order '+order+ ' for mechant ' 
						+ merchant[0].name +' has been settled, kindly check and' 
						+ 'confirm the intended order'
					else:
						#msg = "Congratulations! You have successfully paid your order!"	
						msg = 'You have successfully paid Order No '+ order 
						+' using M-Pesa deposit '+ transaction + ' made by '+ mpesaphone
				except:
					error = 'Error encountered'
					print error
				return render_to_response('complete_pay_unlogged.html', locals(), 
					RequestContext(request))
			else:
				error = "M-Pesa deposit of transaction number "+transaction + \
				" and phone number "+mpesaphone +" does not exist or has been \
				used to pay another order. Kindly try again with correct details"
				return render_to_response('confirm_pay.html', locals(), 
					RequestContext(request))
		else:
			return render_to_response('confirm_pay.html', locals(), 
				RequestContext(request))
	#except:
	else:
		  return render_to_response('confirm_pay.html', locals(), RequestContext(request))		
	
############### MPESA User ###########################
	
	
@login_required		
def pay(request):
	merchants = Merchant.objects.all()
	return render_to_response('pay_order_logged.html', locals(), RequestContext(request))		
	
	
############### GETPAID User ###########################

@login_required		
def payWithGetPaid(request):
	try:
		amount = request.session['amount'] 
		websitekey = request.session['websitekey'] 				
		Ordernumber = request.session['Ordernumber'] 
		merchant = Merchant.objects.get(website_key=websitekey)
		merchant_name = merchant.name
		merchant_id = merchant.id
	except:
		print 'a'
	return render_to_response('pay_with_getpaid.html', locals(), RequestContext(request))

@login_required		
def getPaidPayments(request):
	if request.method == 'POST':
	#try:
		amount = request.POST['amount'] 
		merchant = request.POST['merchant'] 				
		order = request.POST['order'] 
		merchant = Merchant.objects.get(id=merchant)
		user = request.user
		user = User.objects.get(username=user)
		print 'user'
		print user
		customer = Customer.objects.filter(user=user)[0]
		print 'customer customer customer'
		print request.user
		print request
		print customer
		amount = Decimal(amount)
		currency = 'KES'
		balance = Decimal(customer.balance)
		if amount < balance or amount == balance:
			order = Order(number=order,currency=currency,amount=amount,
					merchant=merchant,settled=True,date_added=timezone.now(),
					date_settled=timezone.now())
			order.save()
			trxid = transactionCode()
			trxcode = transactionCode()
			name = user
			trans = Transaction()
			trans.transaction_id = trxid
			trans.customer = customer
			trans.successful = True
			trans.requested = True
			trans.amount = amount 
			trans.transaction_type = '4'
			trans.debit = True
			trans.order = order
			trans.currency=currency	
			trans.merchant = merchant		
			trans.transaction_code = trxcode
			trans.date_added = timezone.now()
			trans.transaction_date = timezone.now() 
			trans.save()
			trans = Transaction()
			trxid = transactionCode()
			trans.transaction_id = trxid
			trans.customer = customer
			trans.successful = True
			trans.requested = True
			trans.amount = amount 
			trans.currency=currency
			trans.transaction_type = '4'
			trans.credit = True		
			trans.transaction_code = trxcode
			trans.date_added = timezone.now()
			trans.transaction_date = timezone.now() 
			trans.save()
			merchant.balance = merchant.balance + Decimal(amount) 
			merchant.save()	
			customer.balance = customer.balance - Decimal(amount) 
			customer.save()					
			msg = 'You have successfully paid your order using your GetPaid deposits. Thank you'	
			return render_to_response('pay_using_getpaid_complete.html', locals(), RequestContext(request))
				
		else:
			error = "Oops! Transaction failed, make sure you have  \
			sufficient funds in your GetPaid Account"
			#error = "Oops! Transaction failed, error encountered. Please try again later"
	#except:
	else:
		print 'a'
		#getPaidPayments		
		merchants = Merchant.objects.all()			
	return render_to_response('pay_using_getpaid.html', locals(), 
		RequestContext(request))

@login_required		
def getPaidWithdrawal(request):
	if request.method == 'POST':
		method = request.POST['method']	
		if method == 'mpesa':
			print 'a'
			#return HttpResponseRedirect('/pay/order/mpesa/')
			return render_to_response('withdraw_to_mpesa.html', locals(), 
				RequestContext(request))	
		elif method == 'bank':
			return render_to_response('withdraw_to_bank.html', locals(), 
				RequestContext(request))
		else:
			return render_to_response('choose_withdrawal.html', locals(), 
				RequestContext(request))
	#except:
	else:
		print 'a'
		#getPaidPayments		
		exchange = CurrencyExchange.objects.get(id=1)			
		return render_to_response('choose_withdrawal.html', locals(), 
			RequestContext(request))


@login_required		
def mpesaWithdrawal(request):
	if request.method == 'POST':
		mode = request.POST['mode']	
		if mode == 'self':
			print 'self'
			phone = request.POST['phone']
			amount = request.POST['amount']
			msg = 'Success! You have sent Ksh '+amount +' to your M-Pesa Account of phone number ' + phone 
			return render_to_response('withdraw_to_mpesa_success.html', locals(), 
				RequestContext(request))	
		elif mode == 'others':
			print 'others'
			phone = request.POST['phone']
			amount = request.POST['amount']
			name = request.POST['name']
			msg = 'Success! You have sent Ksh '+amount + ' to the M-Pesa Account \
			of ' + name + ' of number ' + phone 
			return render_to_response('withdraw_to_mpesa_success.html', locals(), 
				RequestContext(request))
		elif mode == 'list':
			print 'list'
			mylist = request.POST['list']
			msg = 'Success! You have scheduled payments to your list of recipients and \
			you will be notified in the reports about their status. Kindly check after a shortwhile' 
			return render_to_response('withdraw_to_mpesa_success.html', locals(), 
				RequestContext(request))
		else:
			return render_to_response('withdraw_to_mpesa.html', locals(), 
				RequestContext(request))
	#except:
	else:	
		exchange = CurrencyExchange.objects.get(id=1)			
		return render_to_response('withdraw_to_mpesa.html', locals(), 
			RequestContext(request))

@login_required		
def bankWithdrawal(request):
	if request.method == 'POST':
		mode = request.POST['mode']	
		if mode == 'self':
			print 'self'
			account = request.POST['account']
			amount = request.POST['amount']
			msg = 'Success! You have sent Ksh '+amount +' to your Bank Account number ' + account 
			return render_to_response('withdraw_to_bank_success.html', locals(), 
				RequestContext(request))	
		elif mode == 'others':
			print 'others'
			account = request.POST['account']
			amount = request.POST['amount']
			name = request.POST['account_name']
			msg = 'Success! You have sent Ksh '+amount + ' to the Bank Account \
			of ' + name + ' , account number ' + account 
			return render_to_response('withdraw_to_bank_success.html', locals(), 
				RequestContext(request))
		elif mode == 'list':
			print 'list'
			mylist = request.POST['list']
			msg = 'Success! You have scheduled payments to your list of recipients and \
			you will be notified in the reports about their status. Kindly check after 3 days' 
			return render_to_response('withdraw_to_mpesa_success.html', locals(), 
				RequestContext(request))
		else:
			return render_to_response('withdraw_to_bank_success.html', locals(), 
				RequestContext(request))
	#except:
	else:	
		exchange = CurrencyExchange.objects.get(id=1)			
		return render_to_response('withdraw_to_bank.html', locals(), 
			RequestContext(request))


@login_required		
def paypalWithdrawal(request):
	if request.method == 'POST':
	#try:
		amount = request.POST['amount'] 
		email = request.POST['email']
		rate = request.POST['rate']
		exchange = CurrencyExchange.objects.get(id=1)
		return render_to_response('paypal_withdraw_confirm.html', locals(), 
			RequestContext(request))		
	#except:
	else:
		print 'a'
		#getPaidPayments		
		exchange = CurrencyExchange.objects.get(id=1)			
		return render_to_response('paypal_withdraw.html', locals(), 
			RequestContext(request))

@login_required		
def paypalWithdrawal2(request):
	if request.method == 'POST':
	#try:
		amount = request.POST['amount'] 
		email = request.POST['email']
		rate = request.POST['rate']
		exchange = CurrencyExchange.objects.get(id=1)
		return render_to_response('paypal_withdraw_confirm.html', locals(), 
			RequestContext(request))		
	#except:
	else:
		print 'a'
		#getPaidPayments		
		exchange = CurrencyExchange.objects.get(id=1)			
		return render_to_response('paypal_withdraw.html', locals(), 
			RequestContext(request))

def createPaypalWithdrawal(request):
	if request.method == 'GET':
		amount = request.POST['amount'] 
		print amount
		email = request.POST['email']
		rate = request.POST['rate']
		#option = request.POST['option']
		#if option == 'mpesa':
		#	phone = request.POST['phone']

		amount = Decimal(amount) 
		print amount
		print 'print amount'
		paypal_fee = round(((Decimal(0.029) * amount ) + Decimal(0.30)) , 2)
		fee = round((Decimal(0.05) * amount) ,2)
		final_amount = round((Decimal(amount) - Decimal(paypal_fee)) - Decimal(fee),2)
		currency = 'KES'
		#balance = Decimal(customer.balance)
		kes_amount = round((Decimal(final_amount) * Decimal(rate)),2)
		'''
		
		final_amount = request.POST['final_amount']
		local_amount = round((Decimal(final_amount) * Decimal(rate)),2)
		user = request.session['user']
		customer = Customer.objects.get(user=user)	
		currency = 'KSH'
		a=True
		if a:

			pypal = Paypal()
			pypal.email = email
			pypal.customer = customer
			pypal.currency = 'KES'
			pypal.actual_amount = actual_amount
			pypal.exchange_rate = rate 
			pypal.transaction_type = '1'
			pypal.status = status 
			pypal.error = err 	
			pypal.payout_batch_id = payout_batch_id
			pypal.batch_status = batch_status
			pypal.actual_paypal_fees = actual_paypal_fees
			pypal.sender_batch_id = sender_batch_id
			pypal.final_amount = local_amount
			pypal.transaction_fee = fee
			pypal.paypal_fee = paypal_fee
			pypal.date_added = timezone.now()
			pypal.save()

			trans = Transaction()
			trans.transaction_id = 'PAYPAL' + str(pypal.id)
			trans.customer = customer
			trans.successful = True
			trans.requested = True
			trans.amount = local_amount 
			trans.transaction_type = '7'
			trans.debit = True
			trans.transaction_code = payout_batch_id
			trans.account = email 
			trans.date_added = timezone.now()
			trans.transaction_date = timezone.now() 
			trans.save()				
		else:
			print(payout.error)
			msg = 'Error!'
		if state =='FAILED':
			error = "Error encountered, Please try again later"
			exchange = CurrencyExchange.objects.get(id=1)	
			return render_to_response('paypal_deposit.html', locals(), RequestContext(request))    
		else:
			status = '1'
			msg2 = 'Congratulations. You have sent ' + str(currency) + ' '
			msg3 = str(actual_amount) + ' to Paypal account ' + str(email)
			msg = msg2 + msg3
			return render_to_response('paypal_deposit_final.html', locals(), RequestContext(request))
		'''
		exchange = CurrencyExchange.objects.get(id=1)
		return render_to_response('paypal_withdraw_final.html', locals(), RequestContext(request))    
	else:
		exchange = CurrencyExchange.objects.get(id=1)	
		return render_to_response('paypal_withdraw_final.html', locals(), RequestContext(request))    

@login_required		
def paypalDeposit(request):
	if request.method == 'POST':
	#try:
		amount = request.POST['amount'] 
		email = request.POST['email']
		rate = request.POST['rate']
		user = request.user
		user = User.objects.get(username=user)
		print 'user'
		print user
		customer = Customer.objects.get(user=user)
		print 'customer customer customer'
		print request.user
		print request
		print customer		
		print 'rate rate'
		print rate
		newamount = Decimal(amount) / Decimal(rate) 
		paypal_fee = (Decimal(0.029) * newamount ) + Decimal(0.30)
		fee = Decimal(0.05) * Decimal(newamount) 
		final_amount = round((newamount - paypal_fee - fee),2)
		currency = 'KES'
		balance = Decimal(customer.balance)
		kes_amount = round((Decimal(final_amount) * Decimal(rate)),2)
		final_amount = round(final_amount,2)
		fee = round(fee,2)
		paypal_fee = round(paypal_fee,2)
		if kes_amount < balance or kes_amount == balance:
			exchange = CurrencyExchange.objects.get(id=1)		
			return render_to_response('paypal_deposit_confirm.html', locals(), RequestContext(request))		
		else:
			error = "Oops! Transaction failed, make sure you have sufficient funds in your GetPaid Account"
			#error = "Oops! Transaction failed, error encountered. Please try again later"
	#except:
	else:
		print 'a'
		#getPaidPayments		
		exchange = CurrencyExchange.objects.get(id=1)			
	return render_to_response('paypal_deposit.html', locals(), RequestContext(request))

@login_required
def createPaypalPayment(request):
	if request.method == 'POST':
		amount = request.POST['amount'] 
		email = request.POST['email']
		rate = request.POST['rate']
		paypal_fee = request.POST['paypal_fee']
		fee = request.POST['fee']
		final_amount = request.POST['final_amount']
		local_amount = round((Decimal(final_amount) * Decimal(rate)),2)
		user = request.user
		customer = Customer.objects.get(user=user)	
		currency = 'KSH'
		sender_batch_id = ''.join(random.choice(string.ascii_uppercase) for i in range(12))
		payout = Payout({
		  "sender_batch_header": {
		      "sender_batch_id": sender_batch_id,
		      "email_subject": "You have a payment"
		  },
		  "items": [
		      {
		          "recipient_type": "EMAIL",
		          "amount": {
		              "value": amount,
		              "currency": "USD"
		          },
		          "receiver": email,
		          "note": "Thank you.",
		          "sender_item_id": "3734"
		      }
		  ]
		})
		state = 'FAILED'
		if payout.create(sync_mode=True):
			print("payout[%s] created successfully" % (payout.batch_header.payout_batch_id))
			#msg = 'Success!'
			print 'payout payout payout'
			print payout
			'''
			print payout.sender_batch_header
			print payout.batch_header		
			print payout.items
			'''

			payout_batch_id = payout.batch_header.payout_batch_id
			batch_status = payout.batch_header.batch_status
			actual_paypal_fees = payout.batch_header.fees.value
			sender_batch_id = payout.batch_header.sender_batch_header.sender_batch_id
			
			state = '0'
			err = '0'
			for i in payout.items:
				print i['payout_item_fee']['currency']
				state = i['transaction_status']
				if state =='FAILED':
					err = i['errors']['name']
			print payout.batch_header.batch_status

			if state =='FAILED':
				status = '0'
			else:
				status = '1'		

			actual_amount = round((Decimal(amount) * Decimal(rate)),2)
			fee = round((Decimal(fee) * Decimal(rate)),2)

			pypal = Paypal()
			pypal.email = email
			pypal.customer = customer
			pypal.currency = 'KES'
			pypal.actual_amount = actual_amount
			pypal.exchange_rate = rate 
			pypal.transaction_type = '1'
			pypal.status = status 
			pypal.error = err 	
			pypal.payout_batch_id = payout_batch_id
			pypal.batch_status = batch_status
			pypal.actual_paypal_fees = actual_paypal_fees
			pypal.sender_batch_id = sender_batch_id
			pypal.final_amount = local_amount
			pypal.transaction_fee = fee
			pypal.paypal_fee = paypal_fee
			pypal.date_added = timezone.now()
			pypal.save()
																								
			if status == '1':
				trans = Transaction()
				trans.transaction_id = 'PAYPAL' + str(pypal.id)
				trans.customer = customer
				trans.successful = True
				trans.requested = True
				trans.amount = local_amount 
				trans.transaction_type = '7'
				trans.debit = True
				trans.transaction_code = payout_batch_id
				trans.account = email 
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()
			else:	
				trans = Transaction()
				trans.transaction_id = 'PAYPAL' + str(pypal.id)
				trans.customer = customer
				trans.successful = True
				trans.requested = True
				trans.amount = local_amount 
				trans.transaction_type = '7'
				trans.debit = True
				trans.credit = True
				trans.transaction_code = payout_batch_id
				trans.account = email 
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()			
		else:
			print(payout.error)
			msg = 'Error!'
		if state =='Success':
			error = "Error encountered, Please try again later"
			exchange = CurrencyExchange.objects.get(id=1)	
			return render_to_response('paypal_deposit.html', locals(), RequestContext(request))    
		else:
			status = '1'
			msg2 = 'Congratulations. You have sent USD '
			msg3 = str(amount) + ' to Paypal account ' + str(email)
			msg = msg2 + msg3
			return render_to_response('paypal_deposit_final.html', locals(), RequestContext(request))
	else:
		exchange = CurrencyExchange.objects.get(id=1)	
		return render_to_response('paypal_deposit.html', locals(), RequestContext(request))    


@login_required		
def confirmPaypalDeposit(request):
	if request.method == 'POST':
	#try:
		amount = request.POST['amount'] 
		email = request.POST['email']
		rate = request.POST['rate']
		final_amount = request.POST['final_amount']
		fee = request.POST['fee']
		paypal_fee = request.POST['paypal_fee']
		amount = request.POST['amount']
		user = request.user
		user = User.objects.get(username=user)
		print 'user'
		print user
		customer = Customer.objects.get(user=user)
		print 'customer customer customer'
		print request.user
		print request
		print customer		
		print 'rate rate'
		print rate
		amount = Decimal(amount) / Decimal(rate)
		paypal_fee = (Decimal(0.029) * amount ) + Decimal(0.30)
		fee = Decimal(0.05) * amount
		final_amount = amount + paypal_fee + fee
		currency = 'KES'
		balance = Decimal(customer.balance)
		kes_amount = Decimal(final_amount) * Decimal(rate)
		if kes_amount < balance or kes_amount == balance:
			exchange = CurrencyExchange.objects.get(id=1)		
			return render_to_response('paypal_deposit_confirm.html', locals(), RequestContext(request))		
		else:
			error = "Oops! Transaction failed, make sure you have \
			sufficient funds in your GetPaid Account"
			#error = "Oops! Transaction failed, error encountered. Please try again later"
	#except:
	else:
		print 'a'
		#getPaidPayments		
		exchange = CurrencyExchange.objects.get(id=1)			
	return render_to_response('paypal_deposit.html', locals(), RequestContext(request))



@login_required	
def payOrderLogged(request):
	#try:
	a=True
	if a:
		if request.method == 'POST':
			merchant = request.POST['merchant']
			order = request.POST['order']
			myamount = request.POST['amount']
			#user = request.session['user'] 
			user = request.user
			customer = Customer.objects.get(user=user)
			amt = Decimal(myamount)
			bal = Decimal(customer.balance)
			if Decimal(myamount) < Decimal(customer.balance) or Decimal(myamount) == Decimal(customer.balance):
				customer = Customer.objects.filter(user=user)[0]
				customer_ref = customer.id
				#user = User.objects.get(id=user)
				#name = user.first_name + " " + user.last_name
				trxid = transactionCode()
				name = user
				trans = Transaction()
				trans.transaction_id = trxid
				trans.customer = customer
				#trans.phone_number = phone_number #mpesa_msisdn
				trans.successful = True
				trans.requested = True
				trans.amount = myamount #mpesa_amt
				trans.transaction_type = '4'
				trans.credit = True
				trans.transaction_code = trxid
				trans.account = order #mpesa_acc
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() #mpesa_trx_date
				trans.save()
				amount = customer.balance - Decimal(myamount) #mpesa_amt
				customer.balance =  amount
				customer.save()					
				result = recon(order,myamount,trxid,customer_ref,trxid,name)	
				result = result.content
				if result == '404':
					#error = 'This Order has been setlled, kindly check and confirm the intended order'
					merchant = Merchant.objects.filter(id=merchant)
					error = 'The Order '+order+ ' for mechant ' 
					+ merchant[0].name +' has been settled, '
					+ 'kindly check and confirm the intended order'
				else:
					#msg = "Congratulations! You have successfully paid your order!"
					msg = 'You have successfully paid Order No '+order
					+ ' using your GetPaid deposits. Thank you'
			else:
				error = "Oops! Transaction failed, make sure you have \
				sufficient funds in your GetPaid Account"
	#except:
	else:
		error = "Your profile is not fully filled"
	return render_to_response('confirm_pay_logged.html', locals(), 
		RequestContext(request))
	
############### GETPAID User ###########################

############### GETPAID API Payments ###########################
@csrf_exempt 
def payWithAPI(request): 
	mylist = []
	mimetype = "application/javascript"
	if request.method == 'POST': 
		method = request.POST['method']
		if method == 'getpaid':
			merchant = request.POST['merchant']
			result = getPaidAPI(request)
		elif method == 'card':
			merchant = request.POST['merchant']
			result = cardAPI(request)
		elif method == 'mpesa':
			merchant = request.POST['merchant']
			result = mpesaAPI(request)
		else:				
			reply = json.dumps({'Result':result})	
	else:  
		reply = json.dumps({'Failed':'Only POST accepted'})	
	return HttpResponse(reply,mimetype)

@csrf_exempt
def getPaidAPI(request):
	mimetype = "text/plain"
	post_request = json.loads(request.body)
	print post_request
	order = post_request['order']
	amount = post_request['amount']
	merchantkey = post_request['merchantkey']
	currency = post_request['currency']
	#Ordernumber = post_request['Ordernumber']
	signature = post_request['signature']
	envmt = post_request['envmt']
	#culture = request.POST['culture']
	gp_return = post_request['gp_return']
	gp_returnerror = post_request['gp_returnerror']
	user = User.objects.get(id=1) #testing to change
	#user = request.user
	customer = Customer.objects.get(user=user)
	amt = Decimal(amount)
	bal = Decimal(customer.balance)
	if Decimal(amount) < Decimal(customer.balance):
		customer = Customer.objects.filter(user=user)[0]
		customer_ref = customer.id
		#user = User.objects.get(id=user)
		#name = user.first_name + " " + user.last_name
		merchant = Merchant.objects.get(website_key=merchantkey)
		trxid = transactionCode()
		name = user
		trans = Transaction()
		trans.transaction_id = trxid
		trans.customer = customer
		#trans.phone_number = phone_number #mpesa_msisdn
		trans.successful = True
		trans.requested = True
		trans.amount = amount 
		trans.transaction_type = '4'
		trans.credit = True
		trans.transaction_code = trxid
		trans.account = order 	
		trans.date_added = timezone.now()
		trans.transaction_date = timezone.now() 
		trans.save()
		trans = Transaction()
		trans.transaction_id = trxid
		trans.customer = customer
		#trans.phone_number = phone_number #mpesa_msisdn
		trans.successful = True
		trans.requested = True
		trans.amount = amount 
		trans.transaction_type = '4'
		trans.debit = True
		trans.transaction_code = trxid
		trans.account = order 
		trans.merchant = merchant		
		trans.date_added = timezone.now()
		trans.transaction_date = timezone.now() 
		trans.save()
		balAmount = customer.balance - Decimal(amount) 
		customer.balance =  balAmount
		customer.save()
		merchant.balance = merchant.balance + Decimal(amount) 
		merchant.save()
		msg2 = {"Data":merchantkey + '  '+ currency + '  '+ amount  + ' ' + \
		signature +  '  ' + envmt +  ' ' + gp_return +  '  ' + gp_returnerror  }
		print msg2			
		Order = Order(number=order,currency=currency,amount=amount,
			merchant=merchant,settled=True,date_added=timezone.now(),
			date_settled=timezone.now())
		Order.save()
		reply = 200
	else:
		reply = 300
	return HttpResponse(reply,mimetype)

@csrf_exempt
def mpesaAPI(request):
	mimetype = "text/json"
	post_request = json.loads(request.body)
	print post_request
	order = post_request['order']
	phone_number = post_request['phone_number']
	mpesa_code = post_request['mpesa_code']
	currency = post_request['currency']
	amount = post_request['amount']
	merchantkey = post_request['merchantkey']	
	signature = post_request['signature']
	envmt = post_request['envmt']
	gp_return = post_request['gp_return']
	#gp_returnerror = post_request['gp_returnerror']
	customer = Customer.objects.filter(phone_number=phone_number)
	data = {}			
	if not customer: #opposite in prod; if customer, login  first
		reply = 500
	else:
		mpesa = Transaction.objects.filter(phone_number=phone_number,
			transaction_code=mpesa_code,transaction_type=1,
			successful=False) | Transaction.objects.filter(phone_number=phone_number,
			transaction_code=mpesa_code,transaction_type=6,successful=False)
		if mpesa:
			mpesa = mpesa[0]
			print 'mpesa.amount mpesa.amount mpesa.amount'
			print mpesa.amount
			print mpesa
			if (Decimal(amount) == Decimal(mpesa.amount) or Decimal(amount)
			 < Decimal(mpesa.amount)):
				merchant = Merchant.objects.get(website_key=merchantkey)
				order = Order(number=order,currency=currency,amount=amount,
					merchant=merchant,settled=True,date_added=timezone.now(),
					date_settled=timezone.now())
				order.save()
				trxid = transactionCode()
				trans = Transaction()
				trans.transaction_id = trxid
				trans.successful = True
				trans.requested = True
				trans.phone_number = phone_number 
				trans.amount = amount 	
				trans.currency = currency			
				trans.order = order 
				trans.transaction_type = '4'
				trans.debit = True
				trans.transaction_code = mpesa_code
				trans.account = order 
				trans.merchant = merchant		
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()
				mpesa.successful=True
				merchant.balance = merchant.balance + Decimal(amount) 
				merchant.save()					
				if Decimal(amount) < Decimal(mpesa.amount):
					trxid = transactionCode()
					new_amount = Decimal(mpesa.amount) - Decimal(amount) 
					trans = Transaction()
					trans.transaction_id = trxid
					trans.requested = True
	 				trans.successful = False 
					trans.debit = True
					trans.amount = new_amount 
					trans.currency = currency
					trans.transaction_code = mpesa_code
					trans.phone_number = phone_number 
					trans.transaction_type = '6'
					trans.date_added = timezone.now()
					trans.transaction_date = timezone.now() 
					trans.save()
				#reply = 200 #success
				data['code'] = 200
				data['message'] = 'success'
			else:
				#reply = 300 #insufficent funds in the account
				data['code'] = 300
				data['message'] = 'Insufficent funds in the account'
		else:
			#reply = 600 #no such transaction
			data['code'] = 600
			data['message'] = 'No such transaction'
	reply = json.dumps({'result':data})
	return HttpResponse(reply,mimetype)


############## for woo commerce plugins ############################
@csrf_exempt
def httpAPI(request):
	imetype = "text/json"
	data = {}
	gp_return = 'http://sandbox.getpaid.co.ke/api/http/payment/'
	code = ""
	trans = 0
	d_key = 0
	d_amount = 0
	d_status = 0
	d_txnid = 0
	d_mihpayid = 0
	a = True
	if request.method == 'POST':
		post_request = request.POST
		log = SystemLog()
		log.activity = post_request
		log.save()
		print post_request
		phone = post_request['phone']
		email = post_request['email']
		order_id = post_request['txnid']
		transaction_id = post_request['txnid'] #plan to store this in the order
		productinfo = post_request['productinfo']
		firstname = post_request['firstname']
		lastname = post_request['lastname']
		address1 = post_request['address1']
		address2 = post_request['address2']
		city = post_request['city']
		country = post_request['country']
		mpesa_code = 'JAGDHJKL'
		currency = 'KES'
		#mpesa_code = post_request['mpesa_code']
		#currency = post_request['currency']		
		amount = post_request['amount']
		merchantkey = post_request['key']	
		signature = post_request['hash']
		envmt = post_request['envmt']
		furl = post_request['furl']
		surl = post_request['surl']
		curl = post_request['curl']
		gp_return = post_request['furl']
		d_key = merchantkey
		d_amount = amount
		d_status = 'Success'		
	else:
		post_request = request.GET
		phone = post_request['phone']
		email = post_request['email']
		order_id = post_request['txnid']
		transaction_id = post_request['txnid'] #plan to store this in the order
		productinfo = post_request['productinfo']
		firstname = post_request['firstname']
		lastname = post_request['lastname']
		address1 = post_request['address1']
		address2 = post_request['address2']
		city = post_request['city']
		country = post_request['country']
		mpesa_code = 'JAGDHJKL'
		currency = 'KES'
		#mpesa_code = post_request['mpesa_code']
		#currency = post_request['currency']		
		amount = post_request['amount']
		merchantkey = post_request['key']	
		signature = post_request['hash']
		envmt = post_request['envmt']
		furl = post_request['furl']
		surl = post_request['surl']
		curl = post_request['curl']
		gp_return = post_request['furl']
		#gp_returnerror = post_request['gp_returnerror']

		d_key = merchantkey
		d_amount = amount
		d_status = 'Success'
	return render_to_response('apichoose_checkout.html', locals(), 
		RequestContext(request))

@csrf_exempt
def chooseApiPayment(request):
	if request.method == 'POST':
		post_request = request.POST
		print post_request
		phone = request.POST.get('phone')
		email = request.POST.get('email')
		order_id = request.POST.get('order_id')
		#transaction_id = post_request['txnid'] #plan to store this in the order
		productinfo = request.POST.get('productinfo')
		firstname = request.POST.get('firstname')
		lastname = request.POST.get('lastname')
		address1 = request.POST.get('address1')
		address2 = request.POST.get('address2')
		city = request.POST.get('city')
		country = request.POST.get('country')
		mpesa_code = 'JAGDHJKL'
		currency = 'KES'
		#mpesa_code = post_request['mpesa_code']
		#currency = post_request['currency']		
		amount = request.POST.get('amount')
		merchantkey = request.POST.get('merchantkey')	
		signature = request.POST.get('signature')
		envmt = request.POST.get('envmt')
		gp_return = request.POST.get('gp_return')
		method = request.POST['method']
		merchant = Merchant.objects.get(website_key=merchantkey)
		if method == 'mpesa':
			return render_to_response('pay_api_with_mpesa.html', locals(), 
				RequestContext(request))	
		elif method == 'card':
			return render_to_response('pay_api_with_card.html', locals(), RequestContext(request))
		elif method == 'getpaid':
			return redirect('payApiWithGetPaid',amount=amount,
				order=order_id,merchantkey=merchantkey,gpreturn=gp_return)
		else:
			return render_to_response('choose_checkout.html', locals(), 
				RequestContext(request))	
	else:
		return render_to_response('choose_checkout.html', locals(), 
					RequestContext(request))

@login_required
def payApiWithGetPaid(request,amount,order,merchantkey,gpreturn):
	data = request.GET
	print data
   	amount = amount
   	merchantkey = merchantkey			
 	order_id = order
 	gp_return = gpreturn
 	print 'URL :'
 	print gp_return
	merchant = Merchant.objects.get(website_key=merchantkey)
	merchant_name = merchant.name
	merchant_id = merchant.id
   	print data
   	return render_to_response('pay_api_with_getpaid.html', locals(),
   		RequestContext(request))


@login_required	
def	payApiWithGetPaidConfirm(request):
	trans = 0
	d_key = 0
	d_amount = 0
	d_status = 0
	d_txnid = 0
	d_mihpayid = 0
	d_status = 'Failed'
	if request.method == 'POST':
	#try:		
		amount = request.POST['amount'] 
		merchant = request.POST['merchant'] 
		merchantkey = request.POST['merchantkey'] 				
		order = request.POST['order'] 
		gp_return = request.POST['gp_return']
		#***********
		d_key = merchantkey
		d_amount = amount
		#***********
		merchant = Merchant.objects.get(id=merchant)
		user = request.user
		user = User.objects.get(username=user)
		print 'user'
		print user
		customer = Customer.objects.filter(user=user)[0]
		print 'customer customer customer'
		print request.user
		print request
		print customer
		amount = Decimal(amount)
		currency = 'KES'
		balance = Decimal(customer.balance)
		if amount < balance or amount == balance:
			order = Order(number=order,currency=currency,amount=amount,
					merchant=merchant,settled=True,date_added=timezone.now(),
					date_settled=timezone.now())
			order.save()
			trxid = transactionCode()
			d_txnid = trxid
			d_mihpayid = trxid
			trxcode = transactionCode()
			name = user
			trans = Transaction()
			trans.transaction_id = trxid
			trans.customer = customer
			trans.successful = True
			trans.requested = True
			trans.amount = amount 
			trans.transaction_type = '4'
			trans.debit = True
			trans.order = order
			trans.currency=currency	
			trans.merchant = merchant		
			trans.transaction_code = trxcode
			trans.date_added = timezone.now()
			trans.transaction_date = timezone.now() 
			trans.save()
			trans = Transaction()
			trxid = transactionCode()
			trans.transaction_id = trxid
			trans.customer = customer
			trans.successful = True
			trans.requested = True
			trans.amount = amount 
			trans.currency=currency
			trans.transaction_type = '4'
			trans.credit = True		
			trans.transaction_code = trxcode
			trans.date_added = timezone.now()
			trans.transaction_date = timezone.now() 
			trans.save()
			merchant.balance = merchant.balance + Decimal(amount) 
			merchant.save()	
			customer.balance = customer.balance - Decimal(amount) 
			customer.save()	
			d_status = 'Success'				
			msg = 'You have successfully paid your order using your GetPaid deposits. Thank you'	
			#return render_to_response('pay_using_getpaid_complete.html', locals(), RequestContext(request))
				
		else:
			error = "Oops! Transaction failed, make sure you have \
			sufficient funds in your GetPaid Account"
			#error = "Oops! Transaction failed, error encountered. Please try again later"
		c = pycurl.Curl()
		c.setopt(c.URL, gp_return)
		post_data = {'key': d_key,'amount': d_amount,'status': d_status,'txnid': d_txnid,'mihpayid' : d_mihpayid}
		# Form data must be provided already urlencoded.
		postfields = urlencode(post_data)
		# Sets request method to POST,
		# Content-Type header to application/x-www-form-urlencoded
		# and data to send in request body.
		c.setopt(c.POSTFIELDS, postfields)
		c.perform()
		c.close()
		print postfields
		return HttpResponseRedirect(gp_return,data)

	#except:
	else:
		order_id = order_id
		transaction_id = order_id
		amount = amount
		merchantkey = merchantkey
		merchant = Merchant.objects.get(website_key=merchantkey)
		return render_to_response('pay_api_using_getpaid.html', locals(), 
			RequestContext(request))

def payApiWithMpesa(request):
	a = True
	if a:
	#try:
		merchant = request.POST['merchant']
		merchantkey	= request.POST['merchantkey']
		gp_return = request.POST['gp_return']
		order = request.POST['order']
		phone = request.POST['phone']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		email = request.POST['email']
		country = request.POST['country']
		currency = 'KES'
		amount = request.POST['amount']	
		return render_to_response('pay_api_with_mpesa_final.html', locals(), 
			RequestContext(request))
	else:
	#except:
		return render_to_response('pay_api_with_mpesa.html', locals(), 
			RequestContext(request))

@csrf_exempt
def payApiWithMpesaConfirm(request):
	mimetype = "text/plain"
	print request.POST
	merchant = request.POST['merchant']	
	order = request.POST['order']
	phone_number = request.POST['phone']
	mpesaphone = request.POST['mpesaphone']
	name = request.POST['name']
	email = request.POST['email']
	mpesa_code = request.POST['transaction']
	currency = 'KES'
	amount = request.POST['amount']	
	merchantkey = request.POST['merchantkey']
	gp_return = request.POST['gp_return']
	trans = 0
	d_key = 0
	d_amount = 0
	d_status = 0
	d_txnid = 0
	d_mihpayid = 0
	d_status = 'Failed'
	
	#***********
	d_key = merchantkey
	d_amount = amount	
	#***********
	customer = Customer.objects.filter(phone_number=mpesaphone)
	if not customer: #opposite in prod; if customer, login  first
		reply = 500
		customer = Customer()
		customer.name = name
		customer.phone_number = phone_number
		customer.email = email 
		customer.order = order
		customer.amount = amount
		customer.merchant = merchant
		customer.date_added = timezone.now() 
		customer.save()

	mpesa = Transaction.objects.filter(phone_number=mpesaphone,
		transaction_code=mpesa_code,transaction_type=1,
		successful=False) | Transaction.objects.filter(phone_number=mpesaphone,
		transaction_code=mpesa_code,transaction_type=6,successful=False)
	if mpesa:
		mpesa = mpesa[0]
		print 'mpesa.amount mpesa.amount mpesa.amount'
		print mpesa.amount
		print mpesa
		if (Decimal(amount) == Decimal(mpesa.amount) or Decimal(amount) < 
			Decimal(mpesa.amount)):
			merchant = Merchant.objects.get(id=merchant)
			order = Order(number=order,currency=currency,amount=amount,
				merchant=merchant,settled=True,date_added=timezone.now(),
				date_settled=timezone.now())
			order.save()				
			trxid = transactionCode()
			d_txnid = trxid
			d_mihpayid = trxid
			trans = Transaction()
			trans.transaction_id = trxid
			trans.successful = True
			trans.requested = True
			trans.phone_number = mpesaphone 
			trans.amount = amount 
			trans.currency = currency
			trans.order = order
			trans.transaction_type = '4'
			trans.debit = True
			trans.transaction_code = mpesa_code
			trans.account = order 
			trans.merchant = merchant		
			trans.date_added = timezone.now()
			trans.transaction_date = timezone.now() 
			trans.save()
			mpesa.successful=True
			merchant.balance = merchant.balance + Decimal(amount) 
			merchant.save()	
			
			if Decimal(amount) < Decimal(mpesa.amount):
				trxid = transactionCode()
				new_amount = Decimal(mpesa.amount) - Decimal(amount) 
				trans = Transaction()
				trans.transaction_id = trxid
				trans.requested = True
 				trans.successful = False 
				trans.debit = True
				trans.amount = new_amount 
				trans.currency = currency
				trans.transaction_code = mpesa_code
				trans.phone_number = mpesaphone 
				trans.transaction_type = '6'
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()
			reply = 200 #success
			d_status = 'Success'
			#return render_to_response('pay_order_mpesa_complete.html', locals(), 
			#	RequestContext(request))
		else:
			reply = 300 
			d_status = 'Failed'
			error = 'Insufficent funds. The amount paid cannot settle the order'
			##RequestContext(request))
	else:
		reply = 600 
		d_status = 'Failed'
		error = 'No such transaction, Please check M-pesa confirmation code and\
		phone number used to make the payment to ensure they match'
		#return render_to_response('pay_order_mpesa_next.html', locals(), 
		#RequestContext(request))
	c = pycurl.Curl()
	c.setopt(c.URL, gp_return)
	post_data = {'key': d_key,'amount': d_amount,'status': d_status,'txnid': d_txnid,'mihpayid' : d_mihpayid}
	# Form data must be provided already urlencoded.
	postfields = urlencode(post_data)
	# Sets request method to POST,
	# Content-Type header to application/x-www-form-urlencoded
	# and data to send in request body.
	c.setopt(c.POSTFIELDS, postfields)
	c.perform()
	c.close()
	print postfields
	return HttpResponseRedirect(gp_return,data)



#def payApiWithCard(order_id,amount,merchantkey):

def payApiWithCard(request):
	msg = ''
	error = ''
	response_dict = {}
	a = True
	value = 'pay_with_card.html'
	mimetype = "text/json"
	data = {}
	gp_return = 'http://sandbox.getpaid.co.ke/api/http/payment/'
	code = ""
	trans = 0
	d_key = 0
	d_amount = 0
	d_status = 0
	d_txnid = 0
	d_mihpayid = 0
	d_status = 'Failed'
	if a:
	#try:	
		if request.method == 'POST':
			# Set your secret key: remember to change this to your live secret key in production
			# See your keys here https://dashboard.stripe.com/account/apikeys
			#stripe.api_key = "sk_test_Rk6cp5XvZAku0dJjLaBox0yt"
			stripe.api_key = "sk_live_Y7lFlI9OYrzQE2ozjAPKj3ww"
			# Get the credit card details submitted by the form
			'''
			amount = request.session['amount'] 
			currency = request.session['currency']
			Ordernumber = request.session['Ordernumber']
			'''
			print request.POST
			print 'request.POST'
			print 'request.POST'
			print 'request.POST'
			token = request.POST['stripeToken']
			amount = request.POST['amount']
			amount = Decimal(amount) * 100
			log = SystemLog()
  			log.activity = token
  			log.save() 

  			post_request = request.POST
			log = SystemLog()
			log.activity = post_request
			log.save()
			print post_request
			phone = post_request['phone']
			email = post_request['email']
			order_id = post_request['transaction_id']
			transaction_id = post_request['transaction_id'] #plan to store this in the order
			productinfo = post_request['productinfo']
			firstname = post_request['firstname']
			lastname = post_request['lastname']
			address1 = post_request['address1']
			address2 = post_request['address2']
			city = post_request['city']
			country = post_request['country']
			mpesa_code = 'JAGDHJKL'
			currency = 'KES'
			#mpesa_code = post_request['mpesa_code']
			#currency = post_request['currency']		
			amount = post_request['amount']
			merchantkey = post_request['merchantkey']	
			signature = post_request['signature']
			envmt = post_request['envmt']
			gp_return = post_request['furl']
			gp_return = post_request['surl']
			gp_return = post_request['curl']
			gp_return = post_request['gp_return']

			d_key = merchantkey
			d_amount = amount	
			d_txnid = transaction_id		

			amount = int(round((float(amount) * 100) , 2))

			print token
			#if a:
			try:
				# Create the charge on Stripe's servers - this will charge the user's card			
				charge = stripe.Charge.create(
					  amount=amount, # amount in cents, again
					  currency="kes",
					  source=token,
					  description="GetPaid charge"
				)
				log = SystemLog()
	  			log.activity = 'Stripe Feedback :' + str(charge)
	  			log.save()
				msg = 'You have successfully paid your order using your card. Thank you'	
				value = 'pay_with_card_complete.html'

				customer = Customer.objects.filter(phone_number=phone)					
				if not customer: #opposite in prod; if customer, login  first
					code = '500'
				else:
					if a:
						merchant = Merchant.objects.get(website_key=merchantkey)
						trxid = transactionCode()
						order = Order(number=order_id,currency=currency,amount=amount,
							merchant=merchant,settled=True,date_added=timezone.now(),
							date_settled=timezone.now())
						order.save()				
						trans = Transaction()
						trans.transaction_id = trxid
						trans.successful = True
						trans.requested = True
						trans.phone_number = phone 
						trans.amount = amount 	
						trans.currency = currency			
						trans.order = order 
						trans.transaction_type = '4'
						trans.debit = True
						trans.transaction_code = mpesa_code
						trans.account = order 
						trans.merchant = merchant		
						trans.date_added = timezone.now()
						trans.transaction_date = timezone.now() 
						trans.save()
					else:
						mpesa = Transaction.objects.filter(phone_number=phone,
							transaction_code=mpesa_code,transaction_type=1,
							successful=False) | Transaction.objects.filter(phone_number=phone,
							transaction_code=mpesa_code,transaction_type=6,successful=False)
						if mpesa:
							mpesa = mpesa[0]
							print 'mpesa.amount mpesa.amount mpesa.amount'
							print mpesa.amount
							print mpesa
							if (Decimal(amount) == Decimal(mpesa.amount) or Decimal(amount)
							 < Decimal(mpesa.amount)):
								merchant = Merchant.objects.get(website_key=merchantkey)
								order = Order(number=order,currency=currency,amount=amount,
									merchant=merchant,settled=True,date_added=timezone.now(),
									date_settled=timezone.now())
								order.save()
								trxid = transactionCode()

								d_mihpayid = trxid
								
								trans = Transaction()
								trans.transaction_id = trxid
								trans.successful = True
								trans.requested = True
								trans.phone_number = phone 
								trans.amount = amount 	
								trans.currency = currency			
								trans.order = order 
								trans.transaction_type = '4'
								trans.debit = True
								trans.transaction_code = mpesa_code
								trans.account = order 
								trans.merchant = merchant		
								trans.date_added = timezone.now()
								trans.transaction_date = timezone.now() 
								trans.save()
								mpesa.successful=True
								merchant.balance = merchant.balance + Decimal(amount) 
								merchant.save()					
								if Decimal(amount) < Decimal(mpesa.amount):
									trxid = transactionCode()
									new_amount = Decimal(mpesa.amount) - Decimal(amount) 
									trans = Transaction()
									trans.transaction_id = trxid
									trans.requested = True
					 				trans.successful = False 
									trans.debit = True
									trans.amount = new_amount 
									trans.currency = currency
									trans.transaction_code = mpesa_code
									trans.phone_number = phone 
									trans.transaction_type = '6'
									trans.date_added = timezone.now()
									trans.transaction_date = timezone.now() 
									trans.save()
					d_status = 'Success'

			#else:
			except stripe.error.CardError, e:
				# The card has been declined
				d_status = 'Failed'
				response_dict.update({'error': e.message})
				print 'response_dict'
				print response_dict
				error = str(e.message)
				#error = 'Sorry your card has been declined. Please try again'
				pass		
	c = pycurl.Curl()
	c.setopt(c.URL, gp_return)
	post_data = {'key': d_key,'amount': d_amount,'status': d_status,'txnid': d_txnid,'mihpayid' : d_mihpayid}
	# Form data must be provided already urlencoded.
	postfields = urlencode(post_data)
	header=['Content-Type: application/x-www-form-urlencoded; charset=utf-8']
	c.setopt(pycurl.HTTPHEADER, header)
	# Sets request method to POST,
	# Content-Type header to application/x-www-form-urlencoded
	# and data to send in request body.
	c.setopt(c.POSTFIELDS, postfields)
	c.perform()
	c.close()
	print postfields
	return HttpResponseRedirect(gp_return,data)
 

 ############## for woo commerce plugins ############################

@csrf_exempt
def httpAPI2(request):
	mimetype = "text/json"
	data = {}
	gp_return = 'http://sandbox.getpaid.co.ke/api/http/payment/'
	code = ""
	trans = 0
	d_key = 0
	d_amount = 0
	d_status = 0
	d_txnid = 0
	d_mihpayid = 0
	a = True
	if a:
	#try:
		post_request = request.POST
		log = SystemLog()
		log.activity = post_request
		log.save()
		print post_request
		phone = post_request['phone']
		email = post_request['email']
		order_id = post_request['txnid']
		transaction_id = post_request['txnid'] #plan to store this in the order
		productinfo = post_request['productinfo']
		firstname = post_request['firstname']
		lastname = post_request['lastname']
		address1 = post_request['address1']
		address2 = post_request['address2']
		city = post_request['city']
		country = post_request['country']
		mpesa_code = 'JAGDHJKL'
		currency = 'KES'
		#mpesa_code = post_request['mpesa_code']
		#currency = post_request['currency']		
		amount = post_request['amount']
		merchantkey = post_request['key']	
		signature = post_request['hash']
		envmt = post_request['envmt']
		gp_return = post_request['furl']
		gp_return = post_request['surl']
		gp_return = post_request['curl']
		#gp_returnerror = post_request['gp_returnerror']

		d_key = merchantkey
		d_amount = amount
		d_status = 'Success'		

		customer = Customer.objects.filter(phone_number=phone)					
		if not customer: #opposite in prod; if customer, login  first
			code = '500'
		else:
			if a:
				merchant = Merchant.objects.get(website_key=merchantkey)
				trxid = transactionCode()
				order = Order(number=order_id,currency=currency,amount=amount,
					merchant=merchant,settled=True,date_added=timezone.now(),
					date_settled=timezone.now())
				order.save()				
				trans = Transaction()
				trans.transaction_id = trxid
				trans.successful = True
				trans.requested = True
				trans.phone_number = phone 
				trans.amount = amount 	
				trans.currency = currency			
				trans.order = order 
				trans.transaction_type = '4'
				trans.debit = True
				trans.transaction_code = mpesa_code
				trans.account = order 
				trans.merchant = merchant		
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()
			else:
				mpesa = Transaction.objects.filter(phone_number=phone,
					transaction_code=mpesa_code,transaction_type=1,
					successful=False) | Transaction.objects.filter(phone_number=phone,
					transaction_code=mpesa_code,transaction_type=6,successful=False)
				if mpesa:
					mpesa = mpesa[0]
					print 'mpesa.amount mpesa.amount mpesa.amount'
					print mpesa.amount
					print mpesa
					if (Decimal(amount) == Decimal(mpesa.amount) or Decimal(amount)
					 < Decimal(mpesa.amount)):
						merchant = Merchant.objects.get(website_key=merchantkey)
						order = Order(number=order,currency=currency,amount=amount,
							merchant=merchant,settled=True,date_added=timezone.now(),
							date_settled=timezone.now())
						order.save()
						trxid = transactionCode()

						d_txnid = trxid
						d_mihpayid = trxid
						
						trans = Transaction()
						trans.transaction_id = trxid
						trans.successful = True
						trans.requested = True
						trans.phone_number = phone 
						trans.amount = amount 	
						trans.currency = currency			
						trans.order = order 
						trans.transaction_type = '4'
						trans.debit = True
						trans.transaction_code = mpesa_code
						trans.account = order 
						trans.merchant = merchant		
						trans.date_added = timezone.now()
						trans.transaction_date = timezone.now() 
						trans.save()
						mpesa.successful=True
						merchant.balance = merchant.balance + Decimal(amount) 
						merchant.save()					
						if Decimal(amount) < Decimal(mpesa.amount):
							trxid = transactionCode()
							new_amount = Decimal(mpesa.amount) - Decimal(amount) 
							trans = Transaction()
							trans.transaction_id = trxid
							trans.requested = True
			 				trans.successful = False 
							trans.debit = True
							trans.amount = new_amount 
							trans.currency = currency
							trans.transaction_code = mpesa_code
							trans.phone_number = phone 
							trans.transaction_type = '6'
							trans.date_added = timezone.now()
							trans.transaction_date = timezone.now() 
							trans.save()
						#reply = 200 #success
						#data['code'] = 200
						#data['message'] = 'success'
						code = '200'
					else:
						#reply = 300 #insufficent funds in the account
						#data['code'] = 300
						#data['message'] = 'Insufficent funds in the account'
						code = '300'
				else:
					#reply = 600 #no such transaction
					#data['code'] = 600				
					#data['message'] = 'No such transaction'
					code = '600'
	#except Exception, e:
	else:
		data['error'] = 404
		#data['error'] = "Technical error encountered. Check the fields you \
		#are passing and method so as to be 'POST' and URLEncoded"
		#raise e
		code = '404'
	#reply = json.dumps({'result':data})
	#return HttpResponse(reply,mimetype)
	#return HttpResponse(code)	
	#return HttpResponseRedirect(reverse(gp_return, args=[data]))

	c = pycurl.Curl()
	c.setopt(c.URL, gp_return)
	post_data = {'key': d_key,'amount': d_amount,'status': d_status,'txnid': d_txnid,'mihpayid' : d_mihpayid}
	# Form data must be provided already urlencoded.
	postfields = urlencode(post_data)
	# Sets request method to POST,
	# Content-Type header to application/x-www-form-urlencoded
	# and data to send in request body.
	c.setopt(c.POSTFIELDS, postfields)
	c.perform()
	c.close()
	print postfields
	return HttpResponseRedirect(gp_return,data)


def mpesaPayments(request):
	try:
		merchant = request.POST['merchant']	
		order = request.POST['order']
		#hone = request.POST['phone']
		#name = request.POST['name']
		#email = request.POST['email']
		currency = 'KES'
		amount = request.POST['amount']	
		return render_to_response('pay_order_mpesa_next.html', locals(), 
			RequestContext(request))
	except:
		return render_to_response('pay_order_mpesa_new.html', locals(), 
			RequestContext(request))

@csrf_exempt
def mpesaPaymentsConfirmation(request):
	mimetype = "text/plain"
	print request.POST
	merchant = request.POST['merchant']	
	order = request.POST['order']
	#phone_number = request.POST['phone']
	mpesaphone = request.POST['mpesaphone']
	#name = request.POST['name']
	#email = request.POST['email']
	mpesa_code = request.POST['transaction']
	currency = 'KES'
	amount = request.POST['amount']	
	customer = Customer.objects.filter(phone_number=mpesaphone)
	if not customer: #opposite in prod; if customer, login  first
		reply = 500
	else:
		mpesa = Transaction.objects.filter(phone_number=mpesaphone,
			transaction_code=mpesa_code,transaction_type=1,
			successful=False) | Transaction.objects.filter(phone_number=mpesaphone,
			transaction_code=mpesa_code,transaction_type=6,successful=False)
		if mpesa:
			mpesa = mpesa[0]
			print 'mpesa.amount mpesa.amount mpesa.amount'
			print mpesa.amount
			print mpesa
			if (Decimal(amount) == Decimal(mpesa.amount) or Decimal(amount) < 
				Decimal(mpesa.amount)):
				merchant = Merchant.objects.get(id=merchant)
				order = Order(number=order,currency=currency,amount=amount,
					merchant=merchant,settled=True,date_added=timezone.now(),
					date_settled=timezone.now())
				order.save()				
				trxid = transactionCode()
				trans = Transaction()
				trans.transaction_id = trxid
				trans.successful = True
				trans.requested = True
				trans.phone_number = mpesaphone 
				trans.amount = amount 
				trans.currency = currency
				trans.order = order
				trans.transaction_type = '4'
				trans.debit = True
				trans.transaction_code = mpesa_code
				trans.account = order 
				trans.merchant = merchant		
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()
				mpesa.successful=True
				merchant.balance = merchant.balance + Decimal(amount) 
				merchant.save()	
				'''
				customer = OneTimeCustomer()
				customer.name = mpesaphone #name
				customer.phone_number = mpesaphone # #phone_number
 				customer.email = email 
				customer.order = order
				customer.amount = amount
				customer.merchant = merchant
				customer.date_added = timezone.now() 
				customer.save() '''
				if Decimal(amount) < Decimal(mpesa.amount):
					trxid = transactionCode()
					new_amount = Decimal(mpesa.amount) - Decimal(amount) 
					trans = Transaction()
					trans.transaction_id = trxid
					trans.requested = True
	 				trans.successful = False 
					trans.debit = True
					trans.amount = new_amount 
					trans.currency = currency
					trans.transaction_code = mpesa_code
					trans.phone_number = mpesaphone 
					trans.transaction_type = '6'
					trans.date_added = timezone.now()
					trans.transaction_date = timezone.now() 
					trans.save()
				reply = 200 #success
				return render_to_response('pay_order_mpesa_complete.html', locals(), 
					RequestContext(request))
			else:
				reply = 300 
				error = 'Insufficent funds. The amount paid cannot settle the order'
				return render_to_response('pay_order_mpesa_next.html', locals(), 
				RequestContext(request))
		else:
			reply = 600 
			error = 'No such transaction, Please check M-pesa confirmation code and\
			phone number used to make the payment to ensure they match'
			return render_to_response('pay_order_mpesa_next.html', locals(), 
			RequestContext(request))

#@csrf_exempt
def mpesaPaymentsConfirmation2(request):
	mimetype = "text/plain"
	print request.POST
	merchant = request.POST['merchant']	
	order = request.POST['order']
	phone_number = request.POST['phone']
	mpesaphone = request.POST['mpesaphone']
	name = request.POST['name']
	email = request.POST['email']
	mpesa_code = request.POST['transaction']
	currency = 'KES'
	amount = request.POST['amount']	
	customer = Customer.objects.filter(phone_number=mpesaphone)
	if not customer: #opposite in prod; if customer, login  first
		reply = 500
	else:
		mpesa = Transaction.objects.filter(phone_number=mpesaphone,
			transaction_code=mpesa_code,transaction_type=1,
			successful=False) | Transaction.objects.filter(phone_number=mpesaphone,
			transaction_code=mpesa_code,transaction_type=6,successful=False)
		if mpesa:
			mpesa = mpesa[0]
			print 'mpesa.amount mpesa.amount mpesa.amount'
			print mpesa.amount
			print mpesa
			if (Decimal(amount) == Decimal(mpesa.amount) or Decimal(amount) < 
				Decimal(mpesa.amount)):
				merchant = Merchant.objects.get(id=merchant)
				order = Order(number=order,currency=currency,amount=amount,
					merchant=merchant,settled=True,date_added=timezone.now(),
					date_settled=timezone.now())
				order.save()				
				trxid = transactionCode()
				trans = Transaction()
				trans.transaction_id = trxid
				trans.successful = True
				trans.requested = True
				trans.phone_number = mpesaphone 
				trans.amount = amount 
				trans.currency = currency
				trans.order = order
				trans.transaction_type = '4'
				trans.debit = True
				trans.transaction_code = mpesa_code
				trans.account = order 
				trans.merchant = merchant		
				trans.date_added = timezone.now()
				trans.transaction_date = timezone.now() 
				trans.save()
				mpesa.successful=True
				merchant.balance = merchant.balance + Decimal(amount) 
				merchant.save()	
				customer = OneTimeCustomer()
				customer.name = name
				customer.phone_number = phone_number
 				customer.email = email 
				customer.order = order
				customer.amount = amount
				customer.merchant = merchant
				customer.date_added = timezone.now() 
				customer.save()
				if Decimal(amount) < Decimal(mpesa.amount):
					trxid = transactionCode()
					new_amount = Decimal(mpesa.amount) - Decimal(amount) 
					trans = Transaction()
					trans.transaction_id = trxid
					trans.requested = True
	 				trans.successful = False 
					trans.debit = True
					trans.amount = new_amount 
					trans.currency = currency
					trans.transaction_code = mpesa_code
					trans.phone_number = mpesaphone 
					trans.transaction_type = '6'
					trans.date_added = timezone.now()
					trans.transaction_date = timezone.now() 
					trans.save()
				reply = 200 #success
				return render_to_response('pay_order_mpesa_complete.html', locals(), 
					RequestContext(request))
			else:
				reply = 300 #insufficent funds in the account
				return render_to_response('pay_order_mpesa_next.html', locals(), 
				RequestContext(request))
		else:
			reply = 600 #no such transaction
			return render_to_response('pay_order_mpesa_next.html', locals(), 
			RequestContext(request))

#####################################################################################
	
############### Merchant ###########################	
@login_required	
def withdrawalsm(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	return render_to_response('merchant_withdrawals.html', locals(), 
		RequestContext(request))			
	
@login_required	
def Orders(request):
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	Orders = Order.objects.all()
	return render_to_response('orders.html', locals(), RequestContext(request))		
	
@login_required	
def customers(request):	
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass 
	texts = Customer.objects.all()
	return render_to_response('customers.html', locals(), RequestContext(request))	

@login_required	
def merchantAccount(request):	
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	texts = Customer.objects.all()
	return render_to_response('customers.html', locals(), RequestContext(request))

@login_required	
def merchantPayments(request):	
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
	except:
		pass
	payments = Transaction.objects.filter(transaction_type='4',debit=True)
	return render_to_response('payments.html', locals(), RequestContext(request))
	
@login_required	
def merchantOrders(request):	
	try:
		orders = Order.objects.all()
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass			
	return render_to_response('orders.html', locals(), RequestContext(request))	

@login_required	
def merchantWithdrawals(request):	
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	withdrawals = Transaction.objects.filter(transaction_type='3',debit=True)
	return render_to_response('merchant_withdrawals.html', locals(), 
		RequestContext(request))	

@login_required	
def merchantCustomers(request):	
	try:
		iscustomer = request.session['iscustomer'] 
		isstaff =	request.session['isstaff']  
		ismerchant =	request.session['ismerchant'] 
		client_account = request.session['client_account']
	except:
		pass
	texts = Customer.objects.all()
	return render_to_response('customers.html', locals(), RequestContext(request))	

############### Utilities ###########################		
			
@csrf_exempt 
def processpay(request): 
	mylist = []
	mimetype = "application/javascript"
	if request.method == 'POST': 		
		websitekey = request.POST['websitekey']
		amount = request.POST['amount']
		currency = request.POST['currency']
		Ordernumber = request.POST['Ordernumber']
		signature = request.POST['signature']
		test = request.POST['test']
		culture = request.POST['culture']
		Brq_return = request.POST['Brq_return']
		Brq_returncancel = request.POST['Brq_returncancel']
		Brq_returnerror = request.POST['Brq_returnerror']
		Brq_returnreject = request.POST['Brq_returnreject']
		msg2 = {"Data":websitekey + '  '+ currency + '  '+ amount  
		+ '  '+ Ordernumber + ' ' + \
		signature +  '  ' + test +  '  ' + culture +  '  ' + Brq_return +  '  ' + \
		Brq_returncancel +  '  ' + Brq_returnerror + ' ' + Brq_returnreject }
		print msg2
		
		merchant = Merchant.objects.get(website_key=websitekey,
			return_url=Brq_return,return_url_cancel=Brq_returncancel)
		Order = Order(number=Ordernumber,currency=currency,
			amount=amount,merchant=merchant,date_added=timezone.now())
		Order.save()
		msg2 = "Order No "+ Ordernumber  +" settled successfully"
		data = {}
		data['STATUSCODE'] = 190
		data['Ordernumber'] = Ordernumber
		data['currency'] = currency
		data['amount'] = amount
		data['websitekey'] = websitekey			
		
		#{"Data": "dummy  EUR  128.0  SO001   ff5436115f0a2c5b1b1c00b31e5b366b36168a85  True  en-US"}
		
		#ff5436115f0a2c5b1b1c00b31e5b366b36168a85
		#ff5436115f0a2c5b1b1c00b31e5b366b36168a85
		reply = json.dumps({'Result':msg2})	

	else:  
			reply = json.dumps({'Failed':'Only POST accepted'})	
	#return HttpResponse(reply,mimetype)
	#return render_to_response('pay_order.html', locals(), RequestContext(request))	
	return render_to_response('choose_payment2.html', locals(), RequestContext(request))	

def passwordGen():
	random_number = User.objects.make_random_password(length=5, 
		allowed_chars='QWERTYUIOPLKJHGFDSAZXCVBN'
	+'Mmnbvcxzasdfghjklpoiuytrewq1234567890')
	while Transaction.objects.filter(transaction_code=str(random_number)):
		random_number = User.objects.make_random_password(length=5, 
			allowed_chars='QWERTYUIOPLKJHGFDSAZXCVBN'
		+'Mmnbvcxzasdfghjklpoiuytrewq1234567890')
	return random_number

def transactionCodeOld():
	random_number = User.objects.make_random_password(length=6, 
		allowed_chars='QWERTYUIOPLKJHGFDSAZXCVBN'
	+'Mmnbvcxzasdfghjklpoiuytrewq1234567890')
	while Transaction.objects.filter(transaction_code=str(random_number)):
		random_number = User.objects.make_random_password(length=6, 
			allowed_chars='QWERTYUIOPLKJHGFDSAZXCVBN'
		+'Mmnbvcxzasdfghjklpoiuytrewq1234567890')
	return random_number	

def transactionCode():
	random_number = User.objects.make_random_password(length=9, 
		allowed_chars='QWERTYUIOPLKJHGFDSAZXCVBNM123456789')
	while Transaction.objects.filter(transaction_id=str(random_number)):
		random_number = User.objects.make_random_password(length=9, 
			allowed_chars='QWERTYUIOPLKJHGFDSAZXCVBNM123456789')
	return random_number

	
def mpesaIPN():   
	a = True
	today = date.today()
	if a:
	#try:		
		response = client.service.retrieveTransactionsByDate('254702143616',today,'G33kslivehere!') #
		#response = client.service.retrieveTransactionsByDate('254708000993','2015-08-18','Am@c9In$') #Amaco
		#response = response[:9]
		length = len(response)
		for i in range(length):
			time_stamp = response[i].mpesaDatetime
			mpesa_balance = response[i].mpesaBalance
			trx_id = response[i].mpesaId
			message_id = response[i].messageId
			mpesa_code = response[i].mpesaTxcode
			mpesa_trx_date = response[i].mpesaTxdate 
			mpesa_acc = response[i].mpesaAccountnumber
			business_number = response[i].mpesaTerminal
			mpesa_msisdn = response[i].mpesaSendermobile
			mpesa_sender = response[i].mpesaSendername
			mpesa_amt = response[i].mpesaAmount
			msg = "Ok|Thank you"

			trx = Transaction.objects.filter(transaction_type='1',transaction_code=mpesa_code)
			if not trx:

				print response[i].mpesaTxcode
				print response[i].mpesaSendername

				#if a:	
				try:	
					customer = Customer.objects.filter(phone_number=mpesa_msisdn)[0]	
				#else:
				except Exception, err:
					#register customer
					#pswd = random()
					pswd = passwordGen()
					print 'password'
					print pswd
					user = User.objects.create_user(username=mpesa_msisdn,password=pswd,
						first_name=mpesa_sender,last_name=pswd)
					customer = Customer()
					customer.name = mpesa_sender
					customer.phone_number = mpesa_msisdn
					customer.user = user
					customer.date_added = datetime.datetime.now()
					customer.save()
				customer = Customer.objects.filter(phone_number=mpesa_msisdn)[0]				            
				trans = Transaction()
				trans.transaction_id = trx_id
				trans.customer = customer
				trans.phone_number = mpesa_msisdn
				trans.successful = True
				trans.requested = True
				trans.amount = mpesa_amt
				trans.transaction_type = '1'
				trans.credit = True
				trans.transaction_code = mpesa_code
				trans.business_number = BusinessNumber.objects.get(id=1)
				trans.account = mpesa_acc
				trans.date_added = datetime.datetime.now()
				trans.transaction_date = mpesa_trx_date
				trans.save()
				amount = customer.balance + Decimal(mpesa_amt)
				customer.balance =  amount
				customer.save()	
		msg = "Ok|Thank you" 
	#except:
	else:
		msg = "Sorry|Transaction failed"			
	#return msg
	return HttpResponse(msg)

@csrf_exempt
def mpesa(request):         
	if request.method == 'GET':
		text = request.GET['text']
		orig = request.GET['orig']
		dest = request.GET['dest']
		ttstamp = request.GET['tstamp']
		trx_id = request.GET['id']
		customer_id = request.GET['customer_id']
		routemethod_id = request.GET['routemethod_id']
		routemethod_name = request.GET['routemethod_name']
		user = request.GET['user']
		password = request.GET['pass']
		mpesa_code = request.GET['mpesa_code']
		mpesa_acc = request.GET['mpesa_acc']
		business_number = request.GET['business_number']
		mpesa_msisdn = request.GET['mpesa_msisdn']
		mpesa_trx_date = request.GET['mpesa_trx_date']
		mpesa_trx_time = request.GET['mpesa_trx_time']
		mpesa_amt = request.GET['mpesa_amt']
		mpesa_sender = request.GET['mpesa_sender']
	elif request.method == 'POST':
		text = request.POST['text']
		orig = request.POST['orig']
		dest = request.POST['dest']
		ttstamp = request.POST['tstamp']
		trx_id = request.POST['id']
		customer_id = request.POST['customer_id']
		routemethod_id = request.POST['routemethod_id']
		routemethod_name = request.POST['routemethod_name']
		user = request.POST['user']
		password = request.POST['pass']
		mpesa_code = request.POST['mpesa_code']
		mpesa_acc = request.POST['mpesa_acc']
		business_number = request.POST['business_number']
		mpesa_msisdn = request.POST['mpesa_msisdn']
		mpesa_trx_date = request.POST['mpesa_trx_date']
		mpesa_trx_time = request.POST['mpesa_trx_time']
		mpesa_amt = request.POST['mpesa_amt']
		mpesa_sender = request.POST['mpesa_sender']	
	else:
		msg = "Sorry|Transaction failed"	
	try:	
		customer = Customer.objects.filter(phone_number=mpesa_msisdn)[0]	
	except Exception, err:
		#register customer
		pswd = random()
		print 'password'
		print pswd
		user = User.objects.create_user(username=mpesa_msisdn,password=pswd,
			first_name=mpesa_sender,last_name=pswd)
		customer = Customer()
		customer.name = mpesa_sender
		customer.phone_number = mpesa_msisdn
		customer.user = user
		customer.date_added = datetime.datetime.now()
		customer.save()
		customer = Customer.objects.filter(phone_number=mpesa_msisdn)[0]
	trx = Transaction.objects.filter(transaction_type='1',transaction_code=mpesa_code)
	if not trx:	            
		trans = Transaction()
		trans.transaction_id = trx_id
		trans.customer = customer
		trans.phone_number = mpesa_msisdn
		trans.successful = True
		trans.requested = True
		trans.amount = mpesa_amt
		trans.transaction_type = '1'
		trans.credit = True
		trans.transaction_code = mpesa_code
		trans.business_number = BusinessNumber.objects.get(id=1)
		trans.account = mpesa_acc
		trans.date_added = datetime.datetime.now()
		trans.transaction_date = mpesa_trx_date
		trans.save()
		amount = customer.balance + Decimal(mpesa_amt)
		customer.balance =  amount
		customer.save()				
	return render_to_response('customers.html', locals(), RequestContext(request))			
	
@csrf_exempt
def simulateIPN(request): 
	iscustomer = request.session['iscustomer'] 
	isstaff =	request.session['isstaff']  
	ismerchant =	request.session['ismerchant']   
	client_account = request.session['client_account']
	if request.method == 'POST':
		#text = request.POST['text']
		#orig = request.POST['orig']
		#dest = request.POST['dest']
		#ttstamp = request.POST['tstamp']
		trx_id = request.POST['id']
		customer_id = request.POST['customer_id']
		#routemethod_id = request.POST['routemethod_id']
		#routemethod_name = request.POST['routemethod_name']
		#user = request.POST['user']
		#password = request.POST['pass']
		mpesa_code = request.POST['mpesa_code']
		mpesa_acc = request.POST['mpesa_acc']
		business_number = request.POST['business_number']
		mpesa_msisdn = request.POST['phone']
		mpesa_trx_date = request.POST['datetime']
		#mpesa_trx_time = request.POST['mpesa_trx_time']
		mpesa_amt = request.POST['mpesa_amt']
		mpesa_sender = request.POST['mpesa_sender']	
		customer = Customer.objects.filter(phone_number=mpesa_msisdn)
		print customer
		if customer:
			customer = customer[0]
		else:	
			pswd = random()
			print 'password'
			print pswd
			#Create random password and send it to new users/client
			user = User.objects.create_user(username=mpesa_msisdn,password=pswd,
				first_name=mpesa_sender)
			customer = Customer()
			customer.name = mpesa_sender
			customer.phone_number = mpesa_msisdn
			customer.user = user
			customer.date_added = timezone.now()
			customer.save()
			customer = Customer.objects.filter(phone_number=mpesa_msisdn)[0]
		trx = Transaction.objects.filter(transaction_type='1',transaction_code=mpesa_code)
		if not trx:	            
			trans = Transaction()
			trans.transaction_id = trx_id
			trans.customer = customer
			trans.phone_number = mpesa_msisdn
			trans.successful = False
			trans.requested = True
			trans.amount = mpesa_amt
			trans.transaction_type = '1'
			trans.debit = True
			trans.transaction_code = mpesa_code
			trans.business_number = BusinessNumber.objects.get(id=1)
			trans.account = mpesa_acc
			trans.date_added = timezone.now()
			trans.transaction_date = mpesa_trx_date
			trans.save()
			amount = customer.balance + Decimal(mpesa_amt)
			customer.balance =  amount
			customer.save()				
			texts = Transaction.objects.filter(transaction_type='1',credit=True)
		return render_to_response('deposits.html', locals(), RequestContext(request))		
	else:
		return render_to_response('simulateIPN.html', locals(), RequestContext(request))			
	
	
	

# run mandatory services
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
'''
	
mymsg = {'ADD_RETURNDATA': u"{'http://odoo.getpaid.co.ke/payment/mpesa/return'}",
		'BRQ_AMOUNT': u'49.95',
		'BRQ_CURRENCY': u'EUR',
		'BRQ_CUSTOMER_NAME': u'J.+de+T\xe8ster',
		'BRQ_OrderNUMBER': u'SO023',
		'BRQ_PAYER_HASH': u'89f54609d73c2d9e9ecd3e190099cebf288bfb',
		'BRQ_PAYMENT': u'07A5421B53D24030AA52CB77394BF7CB',
		'BRQ_PAYMENT_METHOD': u'ideal',
		'BRQ_SERVICE_IDEAL_CONSUMERBIC': u'RABONL2U',
		'BRQ_SERVICE_IDEAL_CONSUMERIBAN': u'NL44RABO0123456789',
		'BRQ_SERVICE_IDEAL_CONSUMERISSUER': u'ABNAMRO+Bank+',
		'BRQ_SERVICE_IDEAL_CONSUMERNAME': u'J.+de+T\xe8ster',
		'BRQ_SIGNATURE': u'ab827eec646690b1f0a98af96e183a3b201c798c',
		'BRQ_STATUSCODE': u'190',
		'BRQ_STATUSCODE_DETAIL': u'S001',
		'BRQ_STATUSMESSAGE': u'Transaction+successfully+processed',
		'BRQ_TEST': u'true',
		'BRQ_TIMESTAMP': u'2014-10-14+12:23:30',
		'BRQ_TRANSACTIONS': u'086604CE55894ED4BD1BD68CABC44AA6',
		'BRQ_WEBSITEKEY': u'XXXXXXXXX'}
	
'''	
	
	
'''
		return the following values
		            'RETURNDATA': u'',
            'AMOUNT': u'2240.00',
            'CURRENCY': u'KSH',
            'CUSTOMER_NAME': u'Jan de Tester',
            'OrderNUMBER': u'SO004',
            'PAYMENT': u'573311D081B04069BD6336001611DBD4',
            'PAYMENT_METHOD': u'paypal',
            'SERVICE_PAYPAL_PAYERCOUNTRY': u'KE',
            'SERVICE_PAYPAL_PAYEREMAIL': u'vincent@openerp.com',
            'SERVICE_PAYPAL_PAYERFIRSTNAME': u'Jan',
            'SERVICE_PAYPAL_PAYERLASTNAME': u'Tester',
            'SERVICE_PAYPAL_PAYERMIDDLENAME': u'de',
            'SERVICE_PAYPAL_PAYERSTATUS': u'verified',
            'SIGNATURE': u'175d82dd53a02bad393fee32cb1eafa3b6fbbd91',
            'STATUSCODE': u'190',
            'STATUSCODE_DETAIL': u'S001',
            'STATUSMESSAGE': u'Transaction successfully processed',
            'TEST': u'true',
            'TIMESTAMP': u'2014-05-08 12:41:21',
            'TRANSACTIONS': u'D6106678E1D54EEB8093F5B3AC42EA7B',
            'WEBSITEKEY': u'5xTGyGyPyl',
'''	

	
	
	
