import requests
import pyotp
import time
import base64
import json

# ganti dengan userid dan shared secret yang ingin dicoba
userid = "sister"
shared_secret = "ii2210_sister_1234"

# ganti dengan url server kalian
server_url = "http://4.198.168.14:17787/motd"

# ganti dengan motd yang diinginkan
motd = {"motd" : "testing"}

s = base64.b32encode(shared_secret.encode("utf-8")).decode("utf-8")
totp = pyotp.TOTP(s=s,digest="SHA256",digits=8)
x = f"{userid}:" + totp.now()

a = "Basic " + base64.b64encode(bytes(x,encoding="ascii")).decode("ascii")

resp = requests.post(url=server_url, headers={"Authorization" : a}, json=motd)

print(resp.content.decode("utf-8"))
