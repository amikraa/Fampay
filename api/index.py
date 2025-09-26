# api/index.py
from fastapi import FastAPI, Query
from mangum import Mangum
import fampay

app = FastAPI()

@app.get("/upi")
def query_upi(vpa: str = Query(...)):
    if "@" in vpa and not vpa.replace("@", "").isdigit():
        status, data = fampay.call_payout(vpa)
    else:
        status, data = fampay.call_verify(vpa)

    return {"status": status, "data": data}

# Required for Vercel / AWS Lambda
handler = Mangum(app)
