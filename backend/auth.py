"""Accounts and sessions: SQLite + scrypt password hashes + HttpOnly session cookie."""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from collections import defaultdict, deque
from contextlib import closing
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).resolve().parent.parent / "data" / "docunexa.db"))
COOKIE = "docunexa_session"
SESSION_DAYS = 7
router = APIRouter(prefix="/auth", tags=["auth"])


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(db()) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, pw_hash TEXT NOT NULL, created REAL NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires REAL NOT NULL)")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return salt.hex() + "$" + digest.hex()


def check_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$")
        test = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(test.hex(), digest)
    except ValueError:
        return False


_attempts: dict[str, deque] = defaultdict(deque)


def throttle(request: Request, limit: int = 10) -> None:
    ip, now = (request.client.host if request.client else "unknown"), time.time()
    q = _attempts[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(429, "Too many attempts. Please wait a minute.")
    q.append(now)


def _start_session(response: Response, request: Request, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    with closing(db()) as conn, conn:
        conn.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
        conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", (hashlib.sha256(token.encode()).hexdigest(), user_id, time.time() + SESSION_DAYS * 86400))
    secure = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
    response.set_cookie(COOKIE, token, max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax", secure=secure, path="/")


def get_user(request: Request):
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    with closing(db()) as conn:
        return conn.execute(
            "SELECT u.id, u.name, u.email FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ? AND s.expires > ?",
            (hashlib.sha256(token.encode()).hexdigest(), time.time()),
        ).fetchone()


def require_user(request: Request):
    user = get_user(request)
    if not user:
        raise HTTPException(401, "Please log in to continue.")
    return user


def _public(user) -> dict:
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


class SignupBody(BaseModel):
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(body: SignupBody, request: Request, response: Response):
    throttle(request)
    name, email = body.name.strip(), body.email.strip().lower()
    if not 1 <= len(name) <= 60:
        raise HTTPException(422, "Please enter your name.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 120:
        raise HTTPException(422, "Please enter a valid email address.")
    if len(body.password) < 8 or len(body.password) > 128:
        raise HTTPException(422, "Password must be 8 to 128 characters.")
    try:
        with closing(db()) as conn, conn:
            cur = conn.execute("INSERT INTO users (name, email, pw_hash, created) VALUES (?, ?, ?, ?)", (name, email, hash_password(body.password), time.time()))
            uid = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with this email already exists. Try logging in.")
    _start_session(response, request, uid)
    return {"user": {"id": uid, "name": name, "email": email}}


@router.post("/login")
def login(body: LoginBody, request: Request, response: Response):
    throttle(request)
    with closing(db()) as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (body.email.strip().lower(),)).fetchone()
    if not row or not check_password(body.password, row["pw_hash"]):
        raise HTTPException(401, "Incorrect email or password.")
    _start_session(response, request, row["id"])
    return {"user": _public(row)}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)
    if token:
        with closing(db()) as conn, conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
def me(user=Depends(get_user)):
    return {"user": _public(user) if user else None}
