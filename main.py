from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import requests
import json

app = FastAPI()

# ---------------- CONFIG ----------------
MAINTENANCE_MODE = False   # 🔴 set True to pause service
FAMPAY_TOKEN = "eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoiS0s1Sk9zbjRUNGF3NF9EOVd6Z0U0QkJQRF9leGZkZkU4QTdxNXM5QlJOS0I0T2p5SXJqVGMxdnh3RHlBREJoQXpYbjVNd2M5aWU4In0sImFsZyI6IkVDREgtRVMifQ..w3b_31d31e1ptAh06UxMEg.2D0FKvzqMRRmjP35UjJYUt4Ow8yOEOOmyRE6MX-xd9a-sJJK9X0G_OyAL0lBGqTHGz6eixM6I6Ji7pvdO8AsL9QW4O7hxOUAWjEC4Yp23kHeKHrxWcfxAPa6wUmstMGGt7_yvmv7YrhdB_XzFIbITgJhIMlLer1PPMqD_voQ9LU3dUMeq6vUkIVxtDGwIOV1ys2sUqi5JZ6v9KkeejjjHn2_wp6qjAlARKHSbY0-LOgfb6HHdGcKVD7Wo_jhKA7Ez322K_REX7PwZxovutfpUw.HLBRzIVXrbqOrgRdiveiRCYOyPZgKrq9gEt_GkUTS9U"
API_VERIFY = "https://halfblood.famapp.in/vpa/verifyExt"
API_PAYOUT = "https://westeros.famapp.in/txn/create/payout/add/"
USER_AGENT = "vivo 1933 | Android 11 | Dalvik/2.1.0"
DEVICE_ID = "a7ce867c570eb7f8"
APP_VERSION = "525"
PLATFORM = "1"
# ----------------------------------------

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
    try:
        resp = requests.post(API_VERIFY, headers=build_headers(FAMPAY_TOKEN), json=payload, timeout=10)
        return resp.status_code, resp.json()
    except Exception as e:
        return None, {"error": str(e)}

def call_payout(upi: str):
    payload = {"upi_string": f"upi://pay?pa={upi}", "init_mode":"00", "is_uploaded_from_gallery":False}
    try:
        resp = requests.post(API_PAYOUT, headers=build_headers(FAMPAY_TOKEN, is_payout=True), json=payload, timeout=10)
        return resp.status_code, resp.json()
    except Exception as e:
        return None, {"error": str(e)}

def query_upi(upi: str):
    if "@" in upi and not upi.replace("@","").isdigit():
        status, data = call_payout(upi)
        vpa = None
        user = data.get("user")
        if data.get("vpa"):
            vpa = data["vpa"].get("vpa")
        elif user and user.get("fvpas"):
            vpa = user["fvpas"][0]["vpa"].get("address")
        return {
            "endpoint": "payout",
            "status": status,
            "upi": vpa,
            "user": {
                "display_name": user.get("display_username") if user else None,
                "first_name": user.get("first_name") if user else None,
                "last_name": user.get("last_name") if user else None,
                "phone": user.get("contact", {}).get("phone_number") if user else None,
                "country_code": user.get("contact", {}).get("code") if user else None,
                "image": user.get("image") if user else None
            } if user else None,
            "raw": data
        }
    else:
        status, data = call_verify(upi)
        vpa_info = data.get("data", {}).get("verify_vpa_resp", {})
        return {
            "endpoint": "verify",
            "status": status,
            "upi": vpa_info.get("vpa") or vpa_info.get("upi_number"),
            "name": vpa_info.get("name"),
            "is_merchant": vpa_info.get("is_merchant"),
            "ifsc": vpa_info.get("ifsc"),
            "beneficiary_id": vpa_info.get("beneficiary_id"),
            "raw": data
        }

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    status = "maintenance" if MAINTENANCE_MODE else "active"
    message = (
        "<h2>⚡ VoidZero API Service ⚡</h2>"
        f"<p>Status: <b>{status}</b></p>"
        f"<p>Contact at Telegram: "
        f"<a href='https://t.me/aerialchan' target='_blank'>@aerialchan</a></p>"
    )
    if MAINTENANCE_MODE:
        message += "<p>🚧 Currently under maintenance. Please check back later.</p>"
    else:
        message += "<p>✅ Service is running. Use /upi?vpa=xxxx</p>"
    return message

@app.get("/upi")
def upi(vpa: str = Query(...)):
    if MAINTENANCE_MODE:
        return {"status": "maintenance", "message": "API is under maintenance. Please try later."}
    return query_upi(vpa)
