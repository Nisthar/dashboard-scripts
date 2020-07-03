import requests
import json
from bs4 import BeautifulSoup as bs
import random

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

if host.count("/") == 3:
    host = host[:-1]

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
    "X-CSRF-Token": "RJD7+K0HdP8Z/FMbsJJuSXH13h+L0awHmBGOqt1AG4q2/2VH6TcQPY6oVO3OBWhZhvChlfziI8wuJ570Wg6J"
}

print("Starting Discord Login")
r = session.get(host, headers=headers)
r = session.get(host+"/login", headers=headers)

clientId = r.url.split("?client_id=")[1].split("&")[0]
r = session.get(r.url, headers=headers)

data = {"email":discordEmail,"password":discordPassword,"undelete":"false","captcha_key":"null","login_source":"null","gift_code_sku_id":231947760750952460}
r = session.post("https://discord.com/api/v6/auth/login", headers=headers, json=data)
discordToken = json.loads(r.text)["token"]

r = session.get("https://discord.com/oauth2/authorize?client_id="+clientId+"&redirect_uri=https%3A%2F%2Fshreyauth.com%2Fdiscord%2Fconnect&response_type=code&scope=identify%20email%20guilds.join%20guilds", headers=headers)

data = {"permissions":0,"authorize":True}
headers["authorization"] = discordToken
r = session.post("https://discord.com/api/v6/oauth2/authorize?client_id="+clientId+"&response_type=code&redirect_uri=https%3A%2F%2Fshreyauth.com%2Fdiscord%2Fconnect&scope=identify%20email%20guilds.join%20guilds", json=data, headers=headers)

headers.pop("authorization")
r = session.get(json.loads(r.text)["location"], headers=headers)

r = session.get(r.url, headers=headers)

soup = bs(r.text, "html.parser")
csrfToken = soup.find("meta", {"name":"csrf-token"})["content"]
headers["X-CSRF-Token"] = csrfToken

print("Logged In: " + session.cookies.get_dict()["_shreyauth_session"])

password = input("Store Password or Password Link: ")
if "http" in password:
    r = session.get(password, headers=headers)
else:
    r = session.get(host+"?password="+password, headers=headers)

r = session.post(host+"/payment_methods", headers=headers)

stripeSessionId = r.text.split("sessionId: '")[1].split("'")[0]
headers.pop("X-CSRF-Token")

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
    'key': 'pk_live_BAfoB6RFoOUiwWx6tDelkD4y00mZls4N8g'
}
r = session.post("https://api.stripe.com/v1/payment_methods", data=data, headers=headers)
stripePaymentId = json.loads(r.text)["id"]

params = {
    "key": "pk_live_BAfoB6RFoOUiwWx6tDelkD4y00mZls4N8g",
    "session_id": stripeSessionId
}
r = session.get("https://api.stripe.com/v1/payment_pages", params=params, headers=headers)
paymentPageId = json.loads(r.text)["id"]

data = {
    "payment_method": stripePaymentId,
    "key": "pk_live_BAfoB6RFoOUiwWx6tDelkD4y00mZls4N8g"
}
r = session.post("https://api.stripe.com/v1/payment_pages/"+paymentPageId+"/confirm", data=data, headers=headers)
if "card_declined" in r.text:
    print("Declined")
else:
    print("Success")
print("\n \n \n \n " + r.text)