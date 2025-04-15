# adyen_handlers.py

import os
from flask import jsonify, request, redirect, url_for
import Adyen
from dotenv import load_dotenv

load_dotenv()

# Initialize Adyen client
adyen = Adyen.Adyen()
adyen.client.xapikey = os.getenv('ADYEN_API_KEY')
adyen.client.platform = os.getenv('ADYEN_ENVIRONMENT', 'test')

#/paymentMaethods 
def payment_methods():
    json_request = {
        "merchantAccount": os.getenv('ADYEN_MERCHANT_ACCOUNT'),
        "countryCode": "PL",
        "channel": "Web",
        "shopperLocale": "en-US",
        "shopperReference":"shopper123"
    }

    result = adyen.checkout.payments_api.payment_methods(request=json_request)
    print("server payment methods response", result)
    return jsonify(result.message)

#/payments
def payments():
    payment_info = request.get_json()

    request_info = {
        'amount': {
            'currency': 'PLN',
            'value': 8000
        },
        #'countryCode':'BE',
        'reference': 'YOUR_ORDER_REFERENCE',
        'paymentMethod': payment_info['paymentMethod'],
        'returnUrl': 'http://localhost:8080/result/return',
        'merchantAccount': os.getenv('ADYEN_MERCHANT_ACCOUNT'),
        'channel': 'Web',
        'origin': 'http://localhost:8080',
        'authenticationData': {
            'threeDSRequestData': {
                'nativeThreeDS': 'preferred' # 'disabled' for redirect or 'preferred' for native
            }
        },

        #saved payment method params
        'recurringProcessingModel':'CardOnFile',
        'shopperReference': 'shopper123',
        #'storePaymentMethod': payment_info['storePaymentMethod'],
        'storePaymentMethod': payment_info.get('storePaymentMethod', False),
        'shopperInteraction': 'Ecommerce',
        #...

        'browserInfo': {
            'userAgent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9) Gecko/2008052912 Firefox/3.0',
            'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'javaEnabled': True,
            'colorDepth': 24,
            'screenHeight': 2000,
            'screenWidth': 3000,
            'timeZoneOffset': 5,
            'language': 'en'
        },
    }
    print('request_info', request_info)
    response = adyen.checkout.payments_api.payments(request_info)
    return jsonify(response.message)

#/payments/details 
def payment_details():
    details = request.get_json()
    response = adyen.checkout.payments_api.payments_details(details)
    print('payment_details: ', response)
    return jsonify(response.message)


#Redirect return result 
def result_return():
    redirect_result = request.args.get("redirectResult")

    if not redirect_result:
        return redirect(url_for("result_error"))

    details_request = {
        "details": {
            "redirectResult": redirect_result
        }
    }

    try:
        response = adyen.checkout.payments_api.payments_details(details_request)
        result_code = response.message.get("resultCode", "ERROR")
        print("Adyen resultCode:", result_code)

        if result_code == "Authorised":
            return redirect(url_for("result_success"))
        elif result_code in ["Pending", "Received"]:
            return redirect(url_for("result_pending"))
        elif result_code == "Refused":
            return redirect(url_for("result_failed"))
        else:
            return redirect(url_for("result_error"))

    except Exception as e:
        print("Error during /result/return:", str(e))
        return redirect(url_for("result_error"))
