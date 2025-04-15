# app.py

from flask import Flask, render_template
from adyen_handlers import payment_methods, payments, payment_details, result_return
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def start_checkout():
    return render_template('start_checkout.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/paymentMethods', methods=['POST'])
def payment_methods_route():
    return payment_methods()


@app.route('/payments', methods=['POST'])
def payments_route():
    return payments()

@app.route('/payments/details', methods=['POST'])
def payments_details_route():
    return payment_details()


@app.route('/result/return')
def result_return_route():
    return result_return()

@app.route('/result/success')
def result_success():
    return render_template('checkout_success.html')

@app.route('/result/pending')
def result_pending():
     return render_template('checkout_pending.html')

@app.route('/result/failed')
def result_failed():
    return render_template('checkout_failed.html')

@app.route('/result/error')
def result_error():
     return render_template('checkout_error.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
