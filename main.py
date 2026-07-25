import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="SMS Dashboard",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# 只在内存中保留最新一条；不会写入文件或数据库。
latest_sms: Optional[dict] = None


class SMSPayload(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    device: str = Field(default="Android", max_length=100)


def extract_code(text: str) -> str:
    patterns = (
        r"(?:验证码|校验码|动态码|认证码|verification\s*code|code)"
        r"[^\d]{0,15}(\d{4,8})",
        r"(?<!\d)(\d{4,8})(?!\d)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "未识别"


def extract_sender(text: str) -> str:
    match = re.search(r"[【\[]([^】\]]+)[】\]]", text)
    if match:
        return match.group(1).strip()[:80]
    return "短信"


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html = (BASE_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/sms")
async def receive_sms(payload: SMSPayload):
    global latest_sms

    text = payload.text.strip()
    latest_sms = {
        "sender": extract_sender(text),
        "content": text,
        "code": extract_code(text),
        "device": payload.device.strip() or "Android",
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
    }

    return {"ok": True, "code": latest_sms["code"]}


@app.get("/latest")
async def get_latest():
    return JSONResponse(
        {"data": latest_sms},
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )
