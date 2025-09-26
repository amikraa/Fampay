from fastapi import FastAPI, Query
import subprocess, sys, re, json

app = FastAPI()

@app.get("/upi")
def query_upi(vpa: str = Query(...)):
    result = subprocess.run(
        [sys.executable, "fampay.py", vpa],
        capture_output=True,
        text=True
    )

    output = result.stdout

    # Try to extract first JSON block `{ ... }`
    match = re.search(r"\{[\s\S]*\}", output)
    if match:
        try:
            parsed_json = json.loads(match.group(0))
            return {"status": result.returncode, "data": parsed_json}
        except Exception:
            pass

    # fallback: raw output
    return {"status": result.returncode, "raw_output": output}
