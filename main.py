import json
import requests
import uvicorn
from fastapi import FastAPI, APIRouter
from gateway import *

from utils.keyutils import sequence_input, convert_mode, logout, login


# ─────────────────────────────────────────────
# Guard: runner / intr 프로세스가 없을 때만 허용
# ─────────────────────────────────────────────
def _check_idle():
    """runner 프로세스나 인터럽트가 실행 중이면 에러 dict 반환, idle이면 None"""
    try:
        pid_resp = get_main_pid()
        if pid_resp is not None:
            return {"resp": -1, "message": "Runner process is running. SubAction blocked."}
    except Exception:
        pass  # mainAction 서버 꺼져있으면 runner 없는 것으로 간주

    try:
        intr_resp = get_intr_status()
        if intr_resp.get("status") == "running":
            return {"resp": -1, "message": "Interrupt is running. SubAction blocked."}
    except Exception:
        pass  # intrAction 서버 꺼져있으면 intr 없는 것으로 간주

    return None

# ─────────────────────────────────────────────
# FastAPI 앱 & 라우터
# ─────────────────────────────────────────────
app = FastAPI(title="SubAction API", description="로그인/로그아웃, 매크로, 텍스트 입력 등 보조 동작 서버")

weeing_router  = APIRouter(prefix="/weeing",  tags=["Weeing Controls"])
input_router   = APIRouter(prefix="/input",   tags=["Input"])
status_router  = APIRouter(prefix="/status",  tags=["Status"])

# ───────────── Weeing Endpoints ─────────────

@weeing_router.post("/logout", summary="게임 로그아웃")
def try_logout():
    blocked = _check_idle()
    if blocked:
        return blocked
    try:
        logout()
        return {"resp": 0, "message": "Logout handled."}
    except Exception as e:
        return {"resp": -1, "message": str(e)}

@weeing_router.post("/login", summary="게임 로그인")
def try_login(id: str, pw: str):
    blocked = _check_idle()
    if blocked:
        return blocked
    try:
        login(id, pw)
        return {"resp": 0, "message": "Login handled."}
    except Exception as e:
        return {"resp": -1, "message": str(e)}

@weeing_router.get("/macros", summary="매크로 계정 목록 조회")
def get_macros():
    """macros.json 파일에서 저장된 계정 매크로 목록 반환"""
    try:
        macro_path = os.path.join(os.path.dirname(__file__), "src", "macros.json")
        with open(macro_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        accounts = data.get("accounts", [])
        return {"resp": accounts, "message": "Macros loaded."}
    except FileNotFoundError:
        return {"resp": [], "message": "No macros file found."}
    except Exception as e:
        return {"resp": -1, "message": str(e)}

# ───────────── Input Endpoints ─────────────

@input_router.post("/sequence/{key_sequence}", summary="한글/영문 문자열 타이핑")
def input_key_sequence(key_sequence: str):
    blocked = _check_idle()
    if blocked:
        return blocked
    try:
        sequence_input(key_sequence)
        return {"resp": 0, "message": "Key sequence inputted."}
    except Exception as e:
        return {"resp": -1, "message": str(e)}

@input_router.post("/convert_mode", summary="입력 모드 전환")
def convert_input_mode():
    blocked = _check_idle()
    if blocked:
        return blocked
    try:
        convert_mode()
        return {"resp": 0, "message": "Input mode converted."}
    except Exception as e:
        return {"resp": -1, "message": str(e)}

# ───────────── Status Endpoints ─────────────

@status_router.post("/addFCM", summary="FCM 토큰 등록")
def add_fcm_token(token: str):
    try:
        save_path = os.path.join(os.path.dirname(__file__), "..", "alarmHandler", "src", "FCM_LIST.txt")
        with open(save_path, "a") as f:
            f.write(token + "\n")
        return {"resp": 0, "message": "FCM token added."}
    except Exception as e:
        return {"resp": -1, "message": str(e)}

# ───────────── 라우터 등록 ─────────────

app.include_router(weeing_router)
app.include_router(input_router)
app.include_router(status_router)

# ───────────── run app ─────────────

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="warning")
