#!/usr/bin/env python3
import sys
import json
import requests

# ---------------- CONFIG ----------------
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
        return resp.status_code, resp.json(), resp.headers
    except Exception as e:
        return None, {"error": str(e)}, None

def call_payout(upi: str):
    payload = {"upi_string": f"upi://pay?pa={upi}", "init_mode":"00", "is_uploaded_from_gallery":False}
    try:
        resp = requests.post(API_PAYOUT, headers=build_headers(FAMPAY_TOKEN, is_payout=True), json=payload, timeout=10)
        return resp.status_code, resp.json(), resp.headers
    except Exception as e:
        return None, {"error": str(e)}, None

def print_headers(headers):
    if headers:
        for k in ("date","content-type","server","cf-ray"):
            if k in headers: print(f"{k}: {headers[k]}")

def display_verify(data):
    vpa_info = data.get("data", {}).get("verify_vpa_resp")
    if not vpa_info:
        print("No info found.")
        return
    print("\n--- UPI Info ---")
    print("UPI:", vpa_info.get("vpa") or vpa_info.get("upi_number"))
    print("Name:", vpa_info.get("name"))
    print("Is merchant:", vpa_info.get("is_merchant"))
    print("IFSC:", vpa_info.get("ifsc"))
    print("Beneficiary ID:", vpa_info.get("beneficiary_id"))

def display_payout(data):
    user = data.get("user")
    vpa = None
    if data.get("vpa"):
        vpa = data["vpa"].get("vpa")
    elif user and user.get("fvpas"):
        vpa = user["fvpas"][0]["vpa"].get("address")
    print("\n--- VPA Info ---")
    print("UPI:", vpa)
    if user:
        print("Display Name:", user.get("display_username") or "")
        print("First Name:", user.get("first_name") or "")
        print("Last Name:", user.get("last_name") or "")
        contact = user.get("contact", {})
        print("Phone:", contact.get("phone_number") or "")
        print("Country Code:", contact.get("code") or "")
        print("Image URL:", user.get("image") or "")
    else:
        print("No user info found.")

def main(argv):
    if FAMPAY_TOKEN.startswith("REPLACE_WITH"):
        print("Set your FAMPAY_TOKEN inside the script first.")
        sys.exit(1)

    if len(argv) < 2:
        print("Usage: python fampay.py <upi>")
        sys.exit(1)

    upi = argv[1].strip()
    print(f"Querying UPI: {upi}")

    # Choose endpoint
    if "@" in upi and not upi.replace("@","").isdigit():
        status, data, headers = call_payout(upi)
        print(f"\n=== HTTP {status} ===")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print_headers(headers)
        display_payout(data)
    else:
        status, data, headers = call_verify(upi)
        print(f"\n=== HTTP {status} ===")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print_headers(headers)
        display_verify(data)

if __name__ == "__main__":
    main(sys.argv)
