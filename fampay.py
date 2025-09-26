# fampay.py
import requests

FAMPAY_TOKEN = "eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoiS0s1Sk9zbjRUNGF3NF9EOVd6Z0U0QkJQRF9leGZkZkU4QTdxNXM5QlJOS0I0T2p5SXJqVGMxdnh3RHlBREJoQXpYbjVNd2M5aWU4In0sImFsZyI6IkVDREgtRVMifQ..w3b_31d31e1ptAh06UxMEg.2D0FKvzqMRRmjP35UjJYUt4Ow8yOEOOmyRE6MX-xd9a-sJJK9X0G_OyAL0lBGqTHGz6eixM6I6Ji7pvdO8AsL9QW4O7hxOUAWjEC4Yp23kHeKHrxWcfxAPa6wUmstMGGt7_yvmv7YrhdB_XzFIbITgJhIMlLer1PPMqD_voQ9LU3dUMeq6vUkIVxtDGwIOV1ys2sUqi5JZ6v9KkeejjjHn2_wp6qjAlARKHSbY0-LOgfb6HHdGcKVD7Wo_jhKA7Ez322K_REX7PwZxovutfpUw.HLBRzIVXrbqOrgRdiveiRCYOyPZgKrq9gEt_GkUTS9U"
API_VERIFY = "https://halfblood.famapp.in/vpa/verifyExt"
API_PAYOUT = "https://westeros.famapp.in/txn/create/payout/add/"
USER_AGENT = "vivo 1933 | Android 11 | Dalvik/2.1.0"
DEVICE_ID = "a7ce867c570eb7f8"
APP_VERSION = "525"
PLATFORM = "1"

def build_headers(token: str, is_payout=False):
    headers = {
        "accept": "application/json",
        "user-agent": USER_AGENT,
        "content-type": "application/json",
        "authorization": f"Token {token}"
    }
    if is_payout:
        headers.update({
            "x-device-details": USER_AGENT,
            "x-app-version": APP_VERSION,
            "x-platform": PLATFORM,
            "device-id": DEVICE_ID
        })
    return headers

def call_verify(upi: str):
    payload = {"upi_number": upi}
    resp = requests.post(API_VERIFY, headers=build_headers(FAMPAY_TOKEN), json=payload, timeout=10)
    return resp.status_code, resp.json()

def call_payout(upi: str):
    payload = {"upi_string": f"upi://pay?pa={upi}", "init_mode":"00", "is_uploaded_from_gallery":False}
    resp = requests.post(API_PAYOUT, headers=build_headers(FAMPAY_TOKEN, is_payout=True), json=payload, timeout=10)
    return resp.status_code, resp.json()
