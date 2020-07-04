import requests
import json
import random
import time

session = requests.session()

discordEmail = ""
discordPassword = ""
billingEmail = ""
billingCardNumber = ""
billingCardMonth = ""
billingCardYear = ""
billingCardCVV= ""
billingFirstName = ""
billingLastName = ""
billingAddress1 = ""
billingAddress2 = ""
billingCity = ""
billingZip = ""
billingState = ""       #Abbreviation
billingCountry = ""       #Abbreviation

host = input("Website URL (Example https://dash.cookgroup.io): ")
hostShort = host.split("//")[1]

if host.count("/") == 3:
    host = host[:-1]
    
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
}

print("Starting Discord Login")
r = session.get(host)
r = session.get("https://vlo.to/dashboard/discord?host="+hostShort)

discordUrl = r.text.split("// }")[1].split("// window.location.href = `")[1].split("`")[0]
clientId = discordUrl.split("?client_id=")[1].split("&")[0]
r = session.get(discordUrl, headers=headers)

data = {"email":discordEmail,"password":discordPassword,"undelete":"false","captcha_key":"null","login_source":"null","gift_code_sku_id":231947760750952460}
r = session.post("https://discord.com/api/v6/auth/login", headers=headers, json=data)
discordToken = json.loads(r.text)["token"]

r = session.get("https://discord.com/oauth2/authorize?client_id="+clientId+"&redirect_uri=https%3A%2F%2Fvlo.to%2Flogin%2Fcomplete&response_type=code&scope=identify%20email%20guilds.join%20guilds", headers=headers)

data = {"permissions":0,"authorize":True}
headers["authorization"] = discordToken
r = session.post("https://discord.com/api/v6/oauth2/authorize?client_id="+clientId+"&response_type=code&redirect_uri=https%3A%2F%2Fvlo.to%2Flogin%2Fcomplete&scope=identify%20email%20guilds.join%20guilds", json=data, headers=headers)

headers.pop("authorization")
r = session.get(json.loads(r.text)["location"], headers=headers)

r = session.get(r.url, headers=headers)
veloLoginToken = r.url.split("token=")[1]
r = session.get(host+"/token?token="+veloLoginToken, headers=headers)
print("Logged In: " + session.cookies.get_dict()["user_session"])

password = input("Store Password or Password Link: ")
if "http" in password:
    password = password.split("?password=")[1]

r = session.get(host+"/purchase?password="+password, headers=headers)

if "currently in line" in r.text:
    session.cookies.set("queue_session", r.cookies.get_dict()["queue_session"])
    print("In Queue")
    while True:
        r = session.get(host+"/purchase/queue", headers=headers)
        print(r.text)
        if r.text == '{"success":true,"status":"Through queue","passed":true}':
            print("Passed Queue")
            session.cookies.set("queue_session", r.cookies.get_dict()["queue_session"])
            r = session.get(host+"/purchase?password="+password, headers=headers)
            break
        time.sleep(10)

stripeKey = "pk_live" + r.text.split("Stripe('pk_live")[1].split("');")[0]
print(stripeKey)

headers["password"] = password

r = session.get(host+"/purchase/create",headers=headers)
print(r.text)
stripeSessionId = json.loads(r.text)["checkout"]

r = session.get("https://checkout.stripe.com/pay/"+stripeSessionId, headers=headers)

data = {
    'type': 'card',
    'billing_details[address][city]': billingCity,
    'billing_details[address][country]': billingCountry,
    'billing_details[address][line1]': billingAddress1,
    'billing_details[address][line2]': billingAddress2,
    'billing_details[address][postal_code]': billingZip,
    'billing_details[address][state]': billingState,
    'billing_details[name]': billingFirstName + " " + billingLastName,
    'card[number]': billingCardNumber,
    'card[cvc]': billingCardCVV,
    'card[exp_month]': billingCardMonth,
    'card[exp_year]': billingCardYear,
    'payment_user_agent': 'stripe.js/ddb1e7a0; stripe-js-v3/ddb1e7a0; checkout',
    'time_on_page': str(random.randint(240000,340000)),
    'key': stripeKey
}
r = session.post("https://api.stripe.com/v1/payment_methods", data=data, headers=headers)
stripePaymentId = json.loads(r.text)["id"]

params = {
    "key": stripeKey,
    "session_id": stripeSessionId
}
r = session.get("https://api.stripe.com/v1/payment_pages", params=params, headers=headers)
paymentPageId = json.loads(r.text)["id"]

data = {
    "payment_method": stripePaymentId,
    "key": stripeKey
}
r = session.post("https://api.stripe.com/v1/payment_pages/"+paymentPageId+"/confirm", data=data, headers=headers)
if "card_declined" in r.text:
    print("Declined")
else:
    print("Success")
print("\n \n \n \n " + r.text)
