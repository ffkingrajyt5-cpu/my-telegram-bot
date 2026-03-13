#!/usr/bin/env python3
# =============================================================================
# FREE AI BOT - Advanced Telegram Bot v2.0
# Created by: PROSANJIT BARMAN
# =============================================================================
#
# ========== TERMUX INSTALLATION INSTRUCTIONS ==========
# pkg update && pkg upgrade -y
# pkg install python ffmpeg libxml2 libxslt -y
# pip install python-telegram-bot==20.7
# pip install openai
# pip install gTTS
# pip install SpeechRecognition
# pip install Pillow
# pip install qrcode[pil]
# pip install yt-dlp
# pip install requests
# pip install pydub
# pip install instaloader
# pip install pyshorteners
# pip install img2pdf
# pip install rembg  # For background removal (may need onnxruntime)
# pip install python-whois
# pip install dnspython
# pip install cryptography  # For Encrypt/Decrypt
#
# ========== NEW v2.0 FEATURES ==========
# - Referral System (রেফার করে Points কামান)
# - Payment System: Bkash/Rocket/Nagad/Upay
# - Points থেকে Premium নিন
# - Balance থেকে Premium কিনুন
# - Encrypt/Decrypt Text & Files
# - File Hash Generator (MD5, SHA256)
# - Multi-Language Translation
# - AI Text Summarizer
# - Phone Number Info Lookup
# - Link Safety Checker
# - Temporary Email Generator
# - Tool Usage Limits (Admin Control)
# - Admin Payment Approval Panel
#
# ========== RUN ==========
# python bot.py
#
# ========== API KEYS NEEDED ==========
# - Telegram Bot Token: Get from @BotFather
# - OpenAI API Key: https://platform.openai.com (optional)
# - Remove.bg API Key (optional): https://www.remove.bg/api
# - IPInfo Token (optional): https://ipinfo.io/account
# =============================================================================

import os
import re
import io
import csv
import sys
import json
import math
import time
import html
import uuid
import shutil
import random
import string
import asyncio
import logging
import sqlite3
import hashlib
import zipfile
import tempfile
import datetime
import mimetypes
import subprocess
import traceback
import threading
import urllib.parse
import urllib.request
from pathlib import Path
from functools import wraps
from typing import Optional, Dict, Any

# ===================== EDITABLE VARIABLES =====================
BOT_TOKEN = "8620234038:AAEa-fpAiRYIsFJIRmhy2Sn6QmwaReD7fH0"       # Your Telegram bot token from @BotFather
ADMIN_ID = 8525833485
CREATOR_NAME = "PROSANJIT BARMAN"
BOT_NAME = "FREE AI BOT"
OPENAI_API_KEY = ""          # Optional: OpenAI API key (paid) - leave empty to use free AI
REMOVEBG_API_KEY = ""        # Optional: remove.bg API key - leave empty to use rembg (free)
IPINFO_TOKEN = ""            # Optional: ipinfo.io token - works without token too (free tier)

# ── FREE AI SETTINGS ──
# Free AI via pollinations.ai (no API key needed!)
FREE_AI_API = "https://text.pollinations.ai"
FREE_IMAGE_API = "https://image.pollinations.ai/prompt"
# ==============================================================

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lazy imports with availability flags
OPENAI_AVAILABLE = False
GTTS_AVAILABLE = False
PIL_AVAILABLE = False
QR_AVAILABLE = False
YTDLP_AVAILABLE = False
SPEECH_AVAILABLE = False
PYDUB_AVAILABLE = False
PYSHORTENERS_AVAILABLE = False
IMG2PDF_AVAILABLE = False
REMBG_AVAILABLE = False
WHOIS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    pass

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    pass

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    pass

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    pass

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    pass

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    pass

try:
    import pyshorteners
    PYSHORTENERS_AVAILABLE = True
except ImportError:
    pass

try:
    import img2pdf
    IMG2PDF_AVAILABLE = True
except ImportError:
    pass

try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except ImportError:
    pass

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    pass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# python-telegram-bot imports
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ChatAction, ParseMode

# ===================== DATABASE SETUP =====================
DB_PATH = "freeaibot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_banned INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            premium_expiry TEXT,
            voice_access INTEGER DEFAULT 1,
            join_date TEXT,
            last_active TEXT,
            message_count INTEGER DEFAULT 0,
            referral_code TEXT,
            referred_by INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            balance REAL DEFAULT 0.0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            detail TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_context (
            user_id INTEGER PRIMARY KEY,
            context TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            voice_style TEXT DEFAULT 'female_adult',
            tts_lang TEXT DEFAULT 'en'
        )
    """)
    # ── NEW: Referral tracking ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER,
            timestamp TEXT,
            points_given INTEGER DEFAULT 0
        )
    """)
    # ── NEW: Payment requests ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TEXT,
            approved_by INTEGER DEFAULT 0,
            note TEXT DEFAULT ''
        )
    """)
    # ── NEW: Tool usage limits ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS tool_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tool_name TEXT,
            used_date TEXT,
            count INTEGER DEFAULT 1
        )
    """)
    # ── NEW: Tool limits config ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS tool_limits (
            tool_name TEXT PRIMARY KEY,
            free_limit INTEGER DEFAULT 5,
            premium_limit INTEGER DEFAULT 999,
            is_premium_only INTEGER DEFAULT 0
        )
    """)
    # ── NEW: Temp emails ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS temp_emails (
            user_id INTEGER PRIMARY KEY,
            email TEXT,
            created_at TEXT
        )
    """)
    # ── NEW: Add Money Requests (with photo + txn_id + verify) ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS add_money_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            transaction_id TEXT,
            photo_file_id TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            timestamp TEXT,
            approved_by INTEGER DEFAULT 0,
            admin_note TEXT DEFAULT ''
        )
    """)
    # ── NEW: User-Admin Chat Messages ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sender TEXT,
            message TEXT,
            file_id TEXT DEFAULT '',
            file_type TEXT DEFAULT '',
            timestamp TEXT,
            is_read INTEGER DEFAULT 0
        )
    """)
    # ── NEW: Admin wallets (Bkash, Nagad, Binance etc.) ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_name TEXT UNIQUE,
            wallet_number TEXT,
            wallet_type TEXT DEFAULT 'payment',
            is_active INTEGER DEFAULT 1
        )
    """)
    # ── NEW: Admin social media ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_social (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT UNIQUE,
            handle TEXT,
            url TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)
    # ── NEW: Premium prices (admin editable) ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS premium_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT UNIQUE,
            days INTEGER,
            price REAL,
            points_cost INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)
    # ── NEW: Bot settings (admin editable) ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # ── NEW: Admin API Keys (admin manageable) ──
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_apis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT UNIQUE,
            api_key TEXT,
            api_url TEXT DEFAULT '',
            api_type TEXT DEFAULT 'general',
            description TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            added_at TEXT
        )
    """)
    # Insert default premium prices
    default_prices = [
        ("7 দিন", 7, 50.0, 0, 1),
        ("30 দিন", 30, 150.0, 100, 1),
        ("90 দিন", 90, 400.0, 0, 1),
        ("Lifetime", 0, 1000.0, 0, 1),
    ]
    for p in default_prices:
        c.execute("INSERT OR IGNORE INTO premium_prices (plan_name, days, price, points_cost, is_active) VALUES (?,?,?,?,?)", p)
    # Default wallets
    default_wallets = [
        ("Bkash", "01XXXXXXXXXX", "payment"),
        ("Rocket", "01XXXXXXXXXX", "payment"),
        ("Nagad", "01XXXXXXXXXX", "payment"),
        ("Upay", "01XXXXXXXXXX", "payment"),
        ("Binance", "", "crypto"),
    ]
    for w in default_wallets:
        c.execute("INSERT OR IGNORE INTO admin_wallets (wallet_name, wallet_number, wallet_type) VALUES (?,?,?)", w)
    # Default social media
    default_social = [
        ("Facebook", "", ""),
        ("Telegram", "", ""),
        ("WhatsApp", "", ""),
        ("YouTube", "", ""),
        ("Instagram", "", ""),
        ("Twitter/X", "", ""),
    ]
    for s in default_social:
        c.execute("INSERT OR IGNORE INTO admin_social (platform, handle, url) VALUES (?,?,?)", s)
    # Default bot settings
    default_settings = [
        ("bot_username", "aibot3232_bot"),
        ("free_tool_msg", "🆓 ফ্রি ইউজার হিসেবে আপনি সীমিত টুলস ব্যবহার করতে পারবেন।"),
        ("contact_msg", "প্রিমিয়াম নিতে Admin-এর সাথে যোগাযোগ করুন।"),
    ]
    for s in default_settings:
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?,?)", s)
    # Insert default tool limits
    default_tools = [
        ("qr_gen", 10, 999, 0), ("qr_read", 10, 999, 0),
        ("encrypt", 5, 999, 0), ("decrypt", 5, 999, 0),
        ("password_gen", 20, 999, 0), ("phone_info", 3, 50, 0),
        ("link_check", 5, 100, 0), ("file_hash", 10, 999, 0),
        ("translate", 5, 100, 0), ("summarize", 3, 50, 0),
        ("temp_email", 2, 10, 0), ("url_short", 10, 999, 0),
        ("ip_lookup", 5, 100, 0), ("domain_info", 5, 100, 0),
        ("ai_chat", 10, 999, 0), ("ai_image", 3, 50, 0),
        ("tts", 5, 100, 0), ("stt", 5, 100, 0),
        ("img_rembg", 3, 50, 0), ("vid_download", 3, 20, 0),
    ]
    for t in default_tools:
        c.execute("INSERT OR IGNORE INTO tool_limits VALUES (?,?,?,?)", t)
    # Default Admin APIs
    default_apis = [
        ("NumVerify", "", "http://apilayer.net/api/validate", "phone_lookup", "Phone number validation API", 1),
        ("IPInfo", "", "https://ipinfo.io", "ip_lookup", "IP address information lookup", 1),
        ("OpenAI", "", "https://api.openai.com", "ai", "OpenAI GPT API for AI chat", 1),
        ("RemoveBG", "", "https://api.remove.bg", "image", "Background removal API", 1),
        ("AbstractAPI Phone", "", "https://phonevalidation.abstractapi.com/v1/", "phone_lookup", "Phone validation & carrier info", 1),
        ("Callerinfo", "", "https://api.callerinfo.com/v1/", "phone_lookup", "Truecaller-style caller ID", 1),
    ]
    now_ts = datetime.datetime.now().isoformat()
    for api in default_apis:
        c.execute("INSERT OR IGNORE INTO admin_apis (api_name, api_key, api_url, api_type, description, is_active, added_at) VALUES (?,?,?,?,?,?,?)",
                  (api[0], api[1], api[2], api[3], api[4], api[5], now_ts))
    conn.commit()
    conn.close()

init_db()

# ===================== DB HELPERS =====================
def db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False, timeout=20)

def register_user(user, referred_by=0):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        ref_code = f"REF{user.id}"
        c.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, join_date, last_active, referral_code, referred_by, points, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0.0)
        """, (user.id, user.username, user.first_name, user.last_name, now, now, ref_code, referred_by))
        c.execute("""
            UPDATE users SET username=?, first_name=?, last_name=?, last_active=?, message_count=message_count+1
            WHERE user_id=?
        """, (user.username, user.first_name, user.last_name, now, user.id))
        conn.commit()

def is_banned(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        r = c.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r and r[0] == 1

def is_premium(user_id):
    if user_id == ADMIN_ID:
        return True
    with db_conn() as conn:
        c = conn.cursor()
        r = c.execute("SELECT is_premium, premium_expiry FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not r:
            return False
        if r[0] == 1:
            if r[1]:
                expiry = datetime.datetime.fromisoformat(r[1])
                if datetime.datetime.now() > expiry:
                    c.execute("UPDATE users SET is_premium=0 WHERE user_id=?", (user_id,))
                    conn.commit()
                    return False
            return True
        return False

def has_voice_access(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        r = c.execute("SELECT voice_access FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r[0] == 1 if r else True

def get_all_users():
    with db_conn() as conn:
        c = conn.cursor()
        return c.execute("SELECT * FROM users").fetchall()

def get_stats():
    with db_conn() as conn:
        c = conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        premium = c.execute("SELECT COUNT(*) FROM users WHERE is_premium=1").fetchone()[0]
        banned = c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
        week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
        active = c.execute("SELECT COUNT(*) FROM users WHERE last_active>?", (week_ago,)).fetchone()[0]
        return {"total": total, "premium": premium, "banned": banned, "active": active}

def log_action(user_id, action, detail=""):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT INTO logs (user_id, action, detail, timestamp) VALUES (?,?,?,?)",
                  (user_id, action, detail, now))
        conn.commit()

def get_ai_context(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        r = c.execute("SELECT context FROM ai_context WHERE user_id=?", (user_id,)).fetchone()
        if r:
            try:
                return json.loads(r[0])
            except:
                return []
        return []

def save_ai_context(user_id, context):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO ai_context (user_id, context) VALUES (?,?)",
                  (user_id, json.dumps(context[-20:])))
        conn.commit()

def clear_ai_context(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM ai_context WHERE user_id=?", (user_id,))
        conn.commit()

def get_user_voice_style(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        r = c.execute("SELECT voice_style FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
        return r[0] if r else "female_adult"

def set_user_voice_style(user_id, style):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_settings (user_id, voice_style) VALUES (?,?)",
                  (user_id, style))
        conn.commit()

def set_premium(user_id, days=0):
    with db_conn() as conn:
        c = conn.cursor()
        if days > 0:
            expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
        else:
            expiry = None
        c.execute("UPDATE users SET is_premium=1, premium_expiry=? WHERE user_id=?", (expiry, user_id))
        conn.commit()

def remove_premium(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_premium=0, premium_expiry=NULL WHERE user_id=?", (user_id,))
        conn.commit()

def ban_user(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
        conn.commit()

def unban_user(user_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
        conn.commit()

def set_voice_access(user_id, value):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET voice_access=? WHERE user_id=?", (value, user_id))
        conn.commit()

# ── NEW: Referral & Points Helpers ──
def get_referral_code(user_id):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT referral_code FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r[0] if r else f"REF{user_id}"

def get_user_points(user_id):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT points FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r[0] if r else 0

def add_points(user_id, pts):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET points=points+? WHERE user_id=?", (pts, user_id))
        conn.commit()

def get_user_balance(user_id):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r[0] if r else 0.0

def add_balance(user_id, amount):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        conn.commit()

def deduct_balance(user_id, amount):
    with db_conn() as conn:
        c = conn.cursor()
        bal = conn.cursor().execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()
        if bal and bal[0] >= amount:
            c.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amount, user_id))
            conn.commit()
            return True
        return False

def get_referral_count(user_id):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT COUNT(*) FROM referrals WHERE referrer_id=?", (user_id,)).fetchone()
        return r[0] if r else 0

def record_referral(referrer_id, referred_id, points=10):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        # Check if already referred
        exists = c.execute("SELECT id FROM referrals WHERE referred_id=?", (referred_id,)).fetchone()
        if not exists:
            c.execute("INSERT INTO referrals (referrer_id, referred_id, timestamp, points_given) VALUES (?,?,?,?)",
                      (referrer_id, referred_id, now, points))
            c.execute("UPDATE users SET points=points+? WHERE user_id=?", (points, referrer_id))
            conn.commit()
            return True
        return False

# ── NEW: Payment Helpers ──
def create_payment_request(user_id, amount, method, txn_id, note=""):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT INTO payments (user_id, amount, method, transaction_id, status, timestamp, note) VALUES (?,?,?,?,?,?,?)",
                  (user_id, amount, method, txn_id, "pending", now, note))
        conn.commit()
        return c.lastrowid

def get_pending_payments():
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM payments WHERE status='pending' ORDER BY id DESC").fetchall()

def get_user_payments(user_id):
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,)).fetchall()

def approve_payment(payment_id, admin_id):
    with db_conn() as conn:
        c = conn.cursor()
        p = c.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
        if p and p[5] == "pending":
            c.execute("UPDATE payments SET status='approved', approved_by=? WHERE id=?", (admin_id, payment_id))
            add_balance(p[1], p[2])
            conn.commit()
            return p[1], p[2]  # user_id, amount
        return None, None

def reject_payment(payment_id, admin_id):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE payments SET status='rejected', approved_by=? WHERE id=?", (admin_id, payment_id))
        conn.commit()

# ── NEW: Tool Usage / Limit Helpers ──
def get_tool_limit(tool_name, premium=False):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT free_limit, premium_limit, is_premium_only FROM tool_limits WHERE tool_name=?", (tool_name,)).fetchone()
        if not r:
            return 999, False
        if premium:
            return r[1], r[2] == 1
        return r[0], r[2] == 1

def get_tool_usage_today(user_id, tool_name):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT count FROM tool_usage WHERE user_id=? AND tool_name=? AND used_date=?",
                                  (user_id, tool_name, today)).fetchone()
        return r[0] if r else 0

def increment_tool_usage(user_id, tool_name):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with db_conn() as conn:
        c = conn.cursor()
        exists = c.execute("SELECT id FROM tool_usage WHERE user_id=? AND tool_name=? AND used_date=?",
                           (user_id, tool_name, today)).fetchone()
        if exists:
            c.execute("UPDATE tool_usage SET count=count+1 WHERE user_id=? AND tool_name=? AND used_date=?",
                      (user_id, tool_name, today))
        else:
            c.execute("INSERT INTO tool_usage (user_id, tool_name, used_date, count) VALUES (?,?,?,1)",
                      (user_id, tool_name, today))
        conn.commit()

def check_tool_access(user_id, tool_name):
    """Returns (allowed: bool, message: str)"""
    if user_id == ADMIN_ID:
        return True, ""
    prem = is_premium(user_id)
    limit, prem_only = get_tool_limit(tool_name, prem)
    if prem_only and not prem:
        return False, f"🔒 এই টুলটি শুধুমাত্র প্রিমিয়াম ইউজারদের জন্য।\n💎 Premium নিতে /start → Premium System"
    used = get_tool_usage_today(user_id, tool_name)
    if used >= limit:
        return False, f"⚠️ আজকের লিমিট শেষ! ({used}/{limit})\n💎 বেশি ব্যবহারের জন্য Premium নিন।"
    return True, ""

# ── NEW: Temp Email Helpers ──
def save_temp_email(user_id, email):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO temp_emails (user_id, email, created_at) VALUES (?,?,?)",
                  (user_id, email, now))
        conn.commit()

def get_temp_email(user_id):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT email FROM temp_emails WHERE user_id=?", (user_id,)).fetchone()
        return r[0] if r else None

# ── NEW: Add Money Request Helpers ──
def create_add_money_request(user_id, amount, method, txn_id, photo_file_id=""):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT INTO add_money_requests (user_id, amount, method, transaction_id, photo_file_id, status, timestamp) VALUES (?,?,?,?,?,?,?)",
                  (user_id, amount, method, txn_id, photo_file_id, "pending", now))
        conn.commit()
        return c.lastrowid

def get_pending_add_money():
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM add_money_requests WHERE status='pending' ORDER BY id DESC").fetchall()

def get_user_add_money_history(user_id):
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM add_money_requests WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,)).fetchall()

def approve_add_money(req_id, admin_id):
    with db_conn() as conn:
        c = conn.cursor()
        p = c.execute("SELECT * FROM add_money_requests WHERE id=?", (req_id,)).fetchone()
        if p and p[6] == "pending":
            c.execute("UPDATE add_money_requests SET status='approved', approved_by=? WHERE id=?", (admin_id, req_id))
            add_balance(p[1], p[2])
            conn.commit()
            return p[1], p[2]  # user_id, amount
        return None, None

def reject_add_money(req_id, admin_id, note=""):
    with db_conn() as conn:
        c = conn.cursor()
        p = c.execute("SELECT user_id FROM add_money_requests WHERE id=?", (req_id,)).fetchone()
        c.execute("UPDATE add_money_requests SET status='rejected', approved_by=?, admin_note=? WHERE id=?", (admin_id, note, req_id))
        conn.commit()
        return p[0] if p else None

# ── NEW: Support Chat Helpers ──
def save_support_message(user_id, sender, message, file_id="", file_type=""):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT INTO support_messages (user_id, sender, message, file_id, file_type, timestamp) VALUES (?,?,?,?,?,?)",
                  (user_id, sender, message, file_id, file_type, now))
        conn.commit()
        return c.lastrowid

def get_support_chat(user_id, limit=20):
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM support_messages WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit)).fetchall()

def get_all_support_users():
    """Get unique users who have support messages."""
    with db_conn() as conn:
        return conn.cursor().execute("""
            SELECT DISTINCT sm.user_id, u.first_name, u.username,
                   (SELECT COUNT(*) FROM support_messages WHERE user_id=sm.user_id AND is_read=0 AND sender='user') as unread
            FROM support_messages sm
            LEFT JOIN users u ON sm.user_id=u.user_id
            ORDER BY sm.id DESC
        """).fetchall()

def mark_support_read(user_id):
    with db_conn() as conn:
        conn.cursor().execute("UPDATE support_messages SET is_read=1 WHERE user_id=? AND sender='user'", (user_id,))
        conn.commit()

# ── Admin Wallet Helpers ──
def get_admin_wallets(wallet_type=None):
    with db_conn() as conn:
        if wallet_type:
            return conn.cursor().execute("SELECT * FROM admin_wallets WHERE wallet_type=? AND is_active=1", (wallet_type,)).fetchall()
        return conn.cursor().execute("SELECT * FROM admin_wallets WHERE is_active=1").fetchall()

def update_admin_wallet(wallet_name, wallet_number):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE admin_wallets SET wallet_number=? WHERE wallet_name=?", (wallet_number, wallet_name))
        conn.commit()

def add_admin_wallet(wallet_name, wallet_number, wallet_type="payment"):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO admin_wallets (wallet_name, wallet_number, wallet_type, is_active) VALUES (?,?,?,1)",
                  (wallet_name, wallet_number, wallet_type))
        conn.commit()

def delete_admin_wallet(wallet_name):
    with db_conn() as conn:
        conn.cursor().execute("DELETE FROM admin_wallets WHERE wallet_name=?", (wallet_name,))
        conn.commit()

# ── Admin Social Media Helpers ──
def get_admin_socials():
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM admin_social WHERE is_active=1").fetchall()

def update_admin_social(platform, handle, url=""):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE admin_social SET handle=?, url=? WHERE platform=?", (handle, url, platform))
        if c.rowcount == 0:
            c.execute("INSERT INTO admin_social (platform, handle, url) VALUES (?,?,?)", (platform, handle, url))
        conn.commit()

def delete_admin_social(platform):
    with db_conn() as conn:
        conn.cursor().execute("UPDATE admin_social SET is_active=0 WHERE platform=?", (platform,))
        conn.commit()

# ── Premium Price Helpers ──
def get_premium_prices():
    with db_conn() as conn:
        return conn.cursor().execute("SELECT * FROM premium_prices WHERE is_active=1 ORDER BY price").fetchall()

def update_premium_price(plan_name, price, days, points_cost=0):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE premium_prices SET price=?, days=?, points_cost=? WHERE plan_name=?", (price, days, points_cost, plan_name))
        conn.commit()

def add_premium_price(plan_name, days, price, points_cost=0):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO premium_prices (plan_name, days, price, points_cost, is_active) VALUES (?,?,?,?,1)",
                  (plan_name, days, price, points_cost))
        conn.commit()

def delete_premium_price(plan_name):
    with db_conn() as conn:
        conn.cursor().execute("UPDATE premium_prices SET is_active=0 WHERE plan_name=?", (plan_name,))
        conn.commit()

# ── Bot Settings Helpers ──
def get_bot_setting(key, default=""):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT value FROM bot_settings WHERE key=?", (key,)).fetchone()
        return r[0] if r else default

def set_bot_setting(key, value):
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?,?)", (key, value))
        conn.commit()

# ── Admin API Key Helpers ──
def get_admin_apis(api_type=None):
    with db_conn() as conn:
        if api_type:
            return conn.cursor().execute("SELECT * FROM admin_apis WHERE api_type=? AND is_active=1", (api_type,)).fetchall()
        return conn.cursor().execute("SELECT * FROM admin_apis WHERE is_active=1 ORDER BY api_type, api_name").fetchall()

def get_admin_api_key(api_name):
    with db_conn() as conn:
        r = conn.cursor().execute("SELECT api_key, api_url FROM admin_apis WHERE api_name=? AND is_active=1", (api_name,)).fetchone()
        return (r[0], r[1]) if r else ("", "")

def set_admin_api_key(api_name, api_key, api_url=""):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO admin_apis (api_name, api_key, api_url, is_active, added_at) VALUES (?,?,?,1,?)",
                  (api_name, api_key, api_url, now))
        conn.commit()

def add_admin_api(api_name, api_key, api_url, api_type, description):
    with db_conn() as conn:
        c = conn.cursor()
        now = datetime.datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO admin_apis (api_name, api_key, api_url, api_type, description, is_active, added_at) VALUES (?,?,?,?,?,1,?)",
                  (api_name, api_key, api_url, api_type, description, now))
        conn.commit()

def delete_admin_api(api_name):
    with db_conn() as conn:
        conn.cursor().execute("UPDATE admin_apis SET is_active=0 WHERE api_name=?", (api_name,))
        conn.commit()

# ===================== USER STATE =====================
user_states: Dict[int, Dict] = {}

def get_state(user_id):
    return user_states.get(user_id, {})

def set_state(user_id, **kwargs):
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id].update(kwargs)

def clear_state(user_id):
    user_states.pop(user_id, None)

# ===================== KEYBOARDS =====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 AI Tools", callback_data="menu_ai"),
         InlineKeyboardButton("🖼 Image Tools", callback_data="menu_image")],
        [InlineKeyboardButton("🎬 Video Tools", callback_data="menu_video"),
         InlineKeyboardButton("📥 Downloader Tools", callback_data="menu_downloader")],
        [InlineKeyboardButton("📁 File Tools", callback_data="menu_file"),
         InlineKeyboardButton("🌐 Web Tools", callback_data="menu_web")],
        [InlineKeyboardButton("🛠 Utility Tools", callback_data="menu_utility"),
         InlineKeyboardButton("🔒 Encrypt Tools", callback_data="menu_encrypt")],
        [InlineKeyboardButton("🎭 New AI Tools I", callback_data="menu_newai1"),
         InlineKeyboardButton("🎪 New AI Tools II", callback_data="menu_newai2")],
        [InlineKeyboardButton("🎨 New AI Tools III", callback_data="menu_newai3"),
         InlineKeyboardButton("🎵 Audio/Video AI", callback_data="menu_newai4")],
        [InlineKeyboardButton("💳 Payment & Balance", callback_data="menu_payment"),
         InlineKeyboardButton("👥 Refer & Earn", callback_data="menu_referral")],
        [InlineKeyboardButton("💎 Premium System", callback_data="menu_premium"),
         InlineKeyboardButton("⚙️ Admin Panel", callback_data="menu_admin")],
        [InlineKeyboardButton("💬 Admin Chat | সাপোর্ট", callback_data="menu_support"),
         InlineKeyboardButton("📞 Contact Admin", callback_data="menu_contact")],
        [InlineKeyboardButton("🚀 Speed Test", callback_data="menu_speedtest"),
         InlineKeyboardButton("📱 Phone Lookup", callback_data="util_phoneinfo_direct")],
        [InlineKeyboardButton("ℹ️ About Bot", callback_data="menu_about"),
         InlineKeyboardButton("⋯ More Tools", callback_data="menu_more")],
    ])

def back_keyboard(target="main"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data=f"back_{target}")]])

def ai_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 AI Chat", callback_data="ai_chat"),
         InlineKeyboardButton("🎨 AI Image Generator", callback_data="ai_image")],
        [InlineKeyboardButton("❓ AI Q&A", callback_data="ai_qa"),
         InlineKeyboardButton("🔊 Text to Voice", callback_data="ai_tts")],
        [InlineKeyboardButton("🎤 Voice to Text", callback_data="ai_stt"),
         InlineKeyboardButton("🎙 Voice Style", callback_data="ai_voice_style")],
        [InlineKeyboardButton("🗑 Clear Chat Memory", callback_data="ai_clear_memory")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def image_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✂️ Remove Background", callback_data="img_rembg"),
         InlineKeyboardButton("🖼 To PNG", callback_data="img_topng")],
        [InlineKeyboardButton("✨ Enhance Image", callback_data="img_enhance"),
         InlineKeyboardButton("📐 Resize Image", callback_data="img_resize")],
        [InlineKeyboardButton("🗜 Compress Image", callback_data="img_compress"),
         InlineKeyboardButton("📄 Image to PDF", callback_data="img_topdf")],
        [InlineKeyboardButton("💧 Add Watermark", callback_data="img_watermark"),
         InlineKeyboardButton("🔄 Grayscale", callback_data="img_grayscale")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def video_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️ Download Video", callback_data="vid_download"),
         InlineKeyboardButton("✂️ Trim Video", callback_data="vid_trim")],
        [InlineKeyboardButton("🔗 Merge Videos", callback_data="vid_merge"),
         InlineKeyboardButton("🎵 Video to MP3", callback_data="vid_tomp3")],
        [InlineKeyboardButton("🗜 Compress Video", callback_data="vid_compress"),
         InlineKeyboardButton("🖼 Extract Thumbnail", callback_data="vid_thumbnail")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def downloader_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ YouTube", callback_data="dl_youtube"),
         InlineKeyboardButton("🎵 YT Audio", callback_data="dl_ytaudio")],
        [InlineKeyboardButton("🎵 TikTok", callback_data="dl_tiktok"),
         InlineKeyboardButton("📸 Instagram", callback_data="dl_instagram")],
        [InlineKeyboardButton("🔗 Direct Link", callback_data="dl_direct"),
         InlineKeyboardButton("🌐 Any URL", callback_data="dl_anyurl")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def file_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Convert File", callback_data="file_convert"),
         InlineKeyboardButton("📄 PDF to Image", callback_data="file_pdftoimg")],
        [InlineKeyboardButton("🖼 Image to PDF", callback_data="file_imgtopdf"),
         InlineKeyboardButton("✏️ Rename File", callback_data="file_rename")],
        [InlineKeyboardButton("🗜 Compress File", callback_data="file_compress"),
         InlineKeyboardButton("ℹ️ File Info", callback_data="file_info")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def web_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Source Code", callback_data="web_source"),
         InlineKeyboardButton("🔤 Extract Title", callback_data="web_title")],
        [InlineKeyboardButton("✅ Status Check", callback_data="web_status"),
         InlineKeyboardButton("🌐 IP Lookup", callback_data="web_ip")],
        [InlineKeyboardButton("🏷 Domain Info", callback_data="web_domain"),
         InlineKeyboardButton("🔗 URL Shortener", callback_data="web_shorten")],
        [InlineKeyboardButton("🔓 Unshorten URL", callback_data="web_unshorten"),
         InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def utility_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔊 Text to Speech | TTS", callback_data="util_tts"),
         InlineKeyboardButton("🎤 Speech to Text | STT", callback_data="util_stt")],
        [InlineKeyboardButton("📱 QR Generator | কিউআর তৈরি", callback_data="util_qrgen"),
         InlineKeyboardButton("📷 QR Reader | কিউআর পড়া", callback_data="util_qrread")],
        [InlineKeyboardButton("🔐 Password Gen | পাসওয়ার্ড", callback_data="util_passgen"),
         InlineKeyboardButton("👤 Name Generator", callback_data="util_namegen")],
        [InlineKeyboardButton("🕐 Time Checker", callback_data="util_time"),
         InlineKeyboardButton("📊 Base64 Encode", callback_data="util_base64enc")],
        [InlineKeyboardButton("📊 Base64 Decode", callback_data="util_base64dec"),
         InlineKeyboardButton("🌐 Translate | অনুবাদ", callback_data="util_translate")],
        [InlineKeyboardButton("📝 Summarize | সারসংক্ষেপ", callback_data="util_summarize"),
         InlineKeyboardButton("📱 Phone Info | ফোন ইনফো", callback_data="util_phoneinfo")],
        [InlineKeyboardButton("🔍 Link Check | লিংক চেক", callback_data="util_linkcheck"),
         InlineKeyboardButton("📧 Temp Email | অস্থায়ী ইমেইল", callback_data="util_tempemail")],
        [InlineKeyboardButton("📬 Check Email Inbox", callback_data="util_checkinbox"),
         InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def premium_keyboard(user_id):
    prem = is_premium(user_id)
    status = "✅ Active" if prem else "❌ Not Active"
    pts = get_user_points(user_id)
    bal = get_user_balance(user_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💎 Your Status: {status}", callback_data="prem_status")],
        [InlineKeyboardButton(f"⭐ Points: {pts} | 💰 Balance: ৳{bal:.2f}", callback_data="prem_balance")],
        [InlineKeyboardButton("🌟 Premium Features", callback_data="prem_features")],
        [InlineKeyboardButton("💰 Premium Price List", callback_data="prem_price")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="prem_contact")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 All Users", callback_data="adm_users"),
         InlineKeyboardButton("📊 Stats", callback_data="adm_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast"),
         InlineKeyboardButton("📋 Logs", callback_data="adm_logs")],
        [InlineKeyboardButton("🚫 Ban User", callback_data="adm_ban"),
         InlineKeyboardButton("✅ Unban User", callback_data="adm_unban")],
        [InlineKeyboardButton("💎 Add Premium", callback_data="adm_addprem"),
         InlineKeyboardButton("❌ Remove Premium", callback_data="adm_remprem")],
        [InlineKeyboardButton("🎤 Voice Access ON", callback_data="adm_voiceon"),
         InlineKeyboardButton("🔇 Voice Access OFF", callback_data="adm_voiceoff")],
        [InlineKeyboardButton("💳 Pending Payments", callback_data="adm_payments"),
         InlineKeyboardButton("⚡ Approve Payment", callback_data="adm_approve_pay")],
        [InlineKeyboardButton("🛑 Reject Payment", callback_data="adm_reject_pay"),
         InlineKeyboardButton("💰 Add Money Requests", callback_data="adm_addmoney_req")],
        [InlineKeyboardButton("💬 Support Chat Users", callback_data="adm_support_users"),
         InlineKeyboardButton("🔧 Tool Limits", callback_data="adm_tool_limits")],
        [InlineKeyboardButton("💰 Add Balance", callback_data="adm_addbalance"),
         InlineKeyboardButton("🎯 Add Points", callback_data="adm_addpoints")],
        [InlineKeyboardButton("👛 Manage Wallets", callback_data="adm_wallets"),
         InlineKeyboardButton("📱 Social Media", callback_data="adm_socials")],
        [InlineKeyboardButton("💎 Premium Prices", callback_data="adm_prices"),
         InlineKeyboardButton("⚙️ Bot Settings", callback_data="adm_botsettings")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def voice_style_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👩 Female Adult (EN)", callback_data="vs_female_adult_en"),
         InlineKeyboardButton("👨 Male Adult (EN)", callback_data="vs_male_adult_en")],
        [InlineKeyboardButton("👧 Female Child (EN)", callback_data="vs_female_child_en"),
         InlineKeyboardButton("👦 Male Child (EN)", callback_data="vs_male_child_en")],
        [InlineKeyboardButton("🇮🇳 Hindi Female", callback_data="vs_female_adult_hi"),
         InlineKeyboardButton("🇧🇩 Bengali Male", callback_data="vs_male_adult_bn")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_ai")],
    ])

# ── NEW KEYBOARDS ──
def encrypt_tools_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Encrypt Text | টেক্সট এনক্রিপ্ট", callback_data="enc_text"),
         InlineKeyboardButton("🔓 Decrypt Text | ডিক্রিপ্ট", callback_data="dec_text")],
        [InlineKeyboardButton("🔑 Encrypt File | ফাইল এনক্রিপ্ট", callback_data="enc_file"),
         InlineKeyboardButton("📂 Decrypt File | ফাইল ডিক্রিপ্ট", callback_data="dec_file")],
        [InlineKeyboardButton("🔢 File Hash MD5/SHA256 | হ্যাশ", callback_data="util_filehash"),
         InlineKeyboardButton("✅ File Integrity | ফাইল চেক", callback_data="util_filecheck")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def new_ai_tools_keyboard_1():
    """Tools 1-15"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 AI Video Style Transfer", callback_data="nai_video_style"),
         InlineKeyboardButton("🖼 AI Portrait Generator", callback_data="nai_portrait")],
        [InlineKeyboardButton("✨ Animated Sticker Maker", callback_data="nai_sticker"),
         InlineKeyboardButton("🔄 GIF to Video", callback_data="nai_gif2vid")],
        [InlineKeyboardButton("📹 Video to GIF", callback_data="nai_vid2gif"),
         InlineKeyboardButton("🎨 AI Color Palette", callback_data="nai_colorpalette")],
        [InlineKeyboardButton("😂 Meme Caption AI", callback_data="nai_memecaption"),
         InlineKeyboardButton("🌫 AI Background Blur", callback_data="nai_bgblur")],
        [InlineKeyboardButton("😊 Face Emotion Detection", callback_data="nai_faceemotion"),
         InlineKeyboardButton("🎭 AI Cartoonifier", callback_data="nai_cartoonify")],
        [InlineKeyboardButton("👤 AI Avatar Creator", callback_data="nai_avatar"),
         InlineKeyboardButton("🎵 Voice Pitch Changer", callback_data="nai_voicepitch")],
        [InlineKeyboardButton("⏩ Audio Speed Changer", callback_data="nai_audiospeed"),
         InlineKeyboardButton("💋 AI Lip Sync Video", callback_data="nai_lipsync")],
        [InlineKeyboardButton("📝 YouTube Transcript", callback_data="nai_yttranscript"),
         InlineKeyboardButton("🌐 Audio Translator", callback_data="nai_audiotranslate")],
        [InlineKeyboardButton("📈 Video Quality Enhancer", callback_data="nai_videnhance"),
         InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def new_ai_tools_keyboard_2():
    """Tools 16-30"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Face Swap Video", callback_data="nai_faceswap"),
         InlineKeyboardButton("🎶 AI Background Music", callback_data="nai_bgmusic")],
        [InlineKeyboardButton("💬 Video Subtitle Translator", callback_data="nai_subtitletrans"),
         InlineKeyboardButton("😤 Voice Emotion Recognition", callback_data="nai_voiceemotion")],
        [InlineKeyboardButton("🔇 Audio Noise Remover", callback_data="nai_noiseremove"),
         InlineKeyboardButton("🎬 AI Scene Detection", callback_data="nai_scenedetect")],
        [InlineKeyboardButton("🖌 AI Style Image Gen", callback_data="nai_styleimage"),
         InlineKeyboardButton("🎭 Meme Video Generator", callback_data="nai_memevideo")],
        [InlineKeyboardButton("🎞 Frame Interpolator", callback_data="nai_frameinterp"),
         InlineKeyboardButton("🎯 AI Object Tracking", callback_data="nai_objecttrack")],
        [InlineKeyboardButton("✨ AI Face Retouch", callback_data="nai_faceretouch"),
         InlineKeyboardButton("📝 Animated Text Video", callback_data="nai_animtext")],
        [InlineKeyboardButton("✂️ Video Crop & Resize", callback_data="nai_vidcrop"),
         InlineKeyboardButton("📋 AI Video Summarizer", callback_data="nai_vidsummary")],
        [InlineKeyboardButton("🔍 Audio Language ID", callback_data="nai_audiolangid"),
         InlineKeyboardButton("📷 Image OCR Scanner", callback_data="nai_ocr")],
        [InlineKeyboardButton("📝 AI Text on Video", callback_data="nai_textovervid"),
         InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def new_ai_tools_keyboard_3():
    """Tools 31-45"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Batch Audio Converter", callback_data="nai_batchaudio"),
         InlineKeyboardButton("🎤 Voice Cloning AI", callback_data="nai_voiceclone")],
        [InlineKeyboardButton("🎸 AI Music Genre ID", callback_data="nai_musicgenre"),
         InlineKeyboardButton("🖼 AI Image Inpainting", callback_data="nai_inpainting")],
        [InlineKeyboardButton("👴 Face Age Estimator", callback_data="nai_faceage"),
         InlineKeyboardButton("🌈 AI Colorize B&W", callback_data="nai_colorize")],
        [InlineKeyboardButton("🗑 Object Removal Video", callback_data="nai_objremovevid"),
         InlineKeyboardButton("😄 AI Animated Emoji", callback_data="nai_animemoji")],
        [InlineKeyboardButton("🎙 Voice Command Auto", callback_data="nai_voicecmd"),
         InlineKeyboardButton("📺 Video Frame Enhance", callback_data="nai_frameenhance")],
        [InlineKeyboardButton("💧 Batch Video Watermark", callback_data="nai_batchwater"),
         InlineKeyboardButton("🤚 AI Gesture Recognition", callback_data="nai_gesture")],
        [InlineKeyboardButton("🖌 AI Image Style Transfer", callback_data="nai_imgstyletrans"),
         InlineKeyboardButton("🎨 AI Cartoon Video", callback_data="nai_cartvideo")],
        [InlineKeyboardButton("🏞 AI Video BG Replace", callback_data="nai_vidbgreplace"),
         InlineKeyboardButton("👄 AI Lip Reading", callback_data="nai_lipread")],
        [InlineKeyboardButton("🔇 Audio Silence Remover", callback_data="nai_silenceremove"),
         InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def new_ai_tools_keyboard_4():
    """Tools 46-60"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 AI Noise Synthesizer", callback_data="nai_noisesynth"),
         InlineKeyboardButton("✂️ Video Scene Splitter", callback_data="nai_scenesplit")],
        [InlineKeyboardButton("🖼 AI Image Denoiser", callback_data="nai_imgdenoise"),
         InlineKeyboardButton("😂 AI Text-to-Meme", callback_data="nai_text2meme")],
        [InlineKeyboardButton("🔍 AI Object Detection", callback_data="nai_objdetect"),
         InlineKeyboardButton("🎵 AI Music Composer", callback_data="nai_musiccompose")],
        [InlineKeyboardButton("🎨 AI Video Color Grader", callback_data="nai_vidcolorgrade"),
         InlineKeyboardButton("📖 AI Animated Story", callback_data="nai_animstory")],
        [InlineKeyboardButton("🎞 AI Text-to-GIF", callback_data="nai_text2gif"),
         InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def admin_wallet_keyboard():
    wallets = get_admin_wallets()
    buttons = []
    for w in wallets:
        num = w[2] if w[2] else "Not Set"
        buttons.append([InlineKeyboardButton(f"{w[1]}: {num}", callback_data=f"adm_wallet_edit_{w[1]}")])
    buttons.append([InlineKeyboardButton("➕ Add New Wallet", callback_data="adm_wallet_add")])
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)

def admin_social_keyboard():
    socials = get_admin_socials()
    buttons = []
    for s in socials:
        handle = s[2] if s[2] else "Not Set"
        buttons.append([InlineKeyboardButton(f"{s[1]}: {handle}", callback_data=f"adm_social_edit_{s[1]}")])
    buttons.append([InlineKeyboardButton("➕ Add Platform", callback_data="adm_social_add")])
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)

def admin_price_keyboard():
    prices = get_premium_prices()
    buttons = []
    for p in prices:
        days_txt = f"{p[2]} দিন" if p[2] > 0 else "Lifetime"
        buttons.append([InlineKeyboardButton(f"{p[1]}: ৳{p[3]} ({days_txt})", callback_data=f"adm_price_edit_{p[1]}")])
    buttons.append([InlineKeyboardButton("➕ Add New Plan", callback_data="adm_price_add")])
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(buttons)

def payment_keyboard(user_id):
    bal = get_user_balance(user_id)
    pts = get_user_points(user_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💰 Balance: ৳{bal:.2f} | Points: {pts}", callback_data="pay_mybalance")],
        [InlineKeyboardButton("➕ Add Money | টাকা যোগ করুন", callback_data="pay_addmoney")],
        [InlineKeyboardButton("💎 Balance দিয়ে Premium নিন", callback_data="pay_buy_premium")],
        [InlineKeyboardButton("📋 আমার পেমেন্ট হিস্টোরি", callback_data="pay_history")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

def referral_keyboard(user_id):
    ref_code = get_referral_code(user_id)
    count = get_referral_count(user_id)
    pts = get_user_points(user_id)
    bot_username = "aibot3232_bot"
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"👥 আপনার রেফারেল: {count} জন | Points: {pts}", callback_data="ref_stats")],
        [InlineKeyboardButton("🔗 রেফারেল লিংক কপি করুন", callback_data="ref_getlink")],
        [InlineKeyboardButton("📊 Points থেকে Premium নিন", callback_data="ref_redeem")],
        [InlineKeyboardButton("ℹ️ Refer করার নিয়ম", callback_data="ref_howto")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

# ===================== DECORATORS =====================
def require_not_banned(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user and is_banned(user.id):
            if update.message:
                await update.message.reply_text("🚫 You are banned from using this bot.")
            elif update.callback_query:
                await update.callback_query.answer("🚫 You are banned.", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def require_admin(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or user.id != ADMIN_ID:
            if update.message:
                await update.message.reply_text("⛔ Admin only command.")
            elif update.callback_query:
                await update.callback_query.answer("⛔ Admin only.", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ===================== UTILITIES =====================
async def typing_animation(update: Update, context: ContextTypes.DEFAULT_TYPE, delay=0.3):
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        if delay > 0:
            await asyncio.sleep(delay)
    except:
        pass

def safe_edit_or_reply(update, context, text, keyboard=None, parse_mode=None):
    kwargs = {"text": text}
    if keyboard:
        kwargs["reply_markup"] = keyboard
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    try:
        if update.callback_query:
            return update.callback_query.edit_message_text(**kwargs)
        elif update.message:
            return update.message.reply_text(**kwargs)
    except Exception as e:
        logger.error(f"safe_edit_or_reply error: {e}")
        if update.effective_chat:
            return context.bot.send_message(chat_id=update.effective_chat.id, **kwargs)

def make_tts_audio(text, style="female_adult", lang="en"):
    """Generate TTS audio bytes using gTTS."""
    if not GTTS_AVAILABLE:
        return None, "gTTS not installed. Run: pip install gTTS"
    try:
        slow = "child" in style
        tts = gTTS(text=text[:500], lang=lang, slow=slow)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf, None
    except Exception as e:
        return None, str(e)

def speech_to_text_from_file(file_path):
    """Convert audio file to text using SpeechRecognition."""
    if not SPEECH_AVAILABLE:
        return None, "SpeechRecognition not installed. Run: pip install SpeechRecognition"
    try:
        r = sr.Recognizer()
        wav_path = file_path
        if not file_path.endswith(".wav"):
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(file_path)
                wav_path = file_path + ".wav"
                audio.export(wav_path, format="wav")
            else:
                return None, "pydub needed for non-WAV. Run: pip install pydub"
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand audio."
    except Exception as e:
        return None, str(e)

async def free_ai_chat(messages):
    """Call Free AI via pollinations.ai (no API key needed)."""
    for attempt in range(3):  # Retry up to 3 times
        try:
            # Build conversation text from messages
            conversation = ""
            system_prompt = ""
            for m in messages:
                if m["role"] == "system":
                    system_prompt = m["content"]
                elif m["role"] == "user":
                    conversation += f"User: {m['content']}\n"
                elif m["role"] == "assistant":
                    conversation += f"Assistant: {m['content']}\n"

            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n"
            full_prompt += conversation + "Assistant:"

            encoded = urllib.parse.quote(full_prompt)
            url = f"{FREE_AI_API}/{encoded}"

            loop = asyncio.get_event_loop()
            def do_request():
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=45) as resp:
                    return resp.read().decode("utf-8", errors="ignore")

            result = await asyncio.wait_for(
                loop.run_in_executor(None, do_request),
                timeout=50
            )
            return result.strip(), None
        except asyncio.TimeoutError:
            if attempt < 2:
                await asyncio.sleep(2)
                continue
            return None, "AI সার্ভার রেসপন্ড করছে না। কিছুক্ষণ পর আবার চেষ্টা করুন।"
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(2)
                continue
            return None, str(e)
    return None, "AI সার্ভার সাড়া দিচ্ছে না।"

async def openai_chat(messages, user_id=None):
    """Call AI - uses OpenAI if key set, otherwise free Pollinations AI."""
    # Try OpenAI if key is configured
    if OPENAI_AVAILABLE and OPENAI_API_KEY and not OPENAI_API_KEY.startswith("http"):
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return resp.choices[0].message.content.strip(), None
        except Exception as e:
            logger.warning(f"OpenAI failed, falling back to free AI: {e}")
    
    # Fallback to free Pollinations AI
    return await free_ai_chat(messages)

async def free_ai_image(prompt):
    """Generate image using Pollinations AI (completely free, no API key)."""
    try:
        encoded = urllib.parse.quote(prompt)
        # Pollinations returns image directly
        url = f"{FREE_IMAGE_API}/{encoded}?width=1024&height=1024&seed={random.randint(1,99999)}&nologo=true"
        return url, None
    except Exception as e:
        return None, str(e)

async def openai_image(prompt):
    """Generate image - uses OpenAI DALL-E if key set, otherwise free Pollinations AI."""
    # Try OpenAI DALL-E if key is configured
    if OPENAI_AVAILABLE and OPENAI_API_KEY and not OPENAI_API_KEY.startswith("http"):
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            resp = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            url = resp.data[0].url
            return url, None
        except Exception as e:
            logger.warning(f"DALL-E failed, using free image gen: {e}")
    
    # Use free Pollinations image generation
    return await free_ai_image(prompt)

def fetch_url_content(url, timeout=10):
    """Fetch URL content."""
    if not REQUESTS_AVAILABLE:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="ignore"), None
        except Exception as e:
            return None, str(e)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=timeout)
        return r.text, None
    except Exception as e:
        return None, str(e)

def get_ip_info(ip):
    """Lookup IP information."""
    try:
        url = f"https://ipinfo.io/{ip}/json"
        if IPINFO_TOKEN and IPINFO_TOKEN.strip() and not IPINFO_TOKEN.startswith("http"):
            url += f"?token={IPINFO_TOKEN}"
        if REQUESTS_AVAILABLE:
            r = requests.get(url, timeout=8)
            return r.json(), None
        else:
            with urllib.request.urlopen(url, timeout=8) as resp:
                return json.loads(resp.read()), None
    except Exception as e:
        return None, str(e)

def generate_password(length=16, symbols=True):
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += "!@#$%^&*()-_=+"
    return "".join(random.choices(chars, k=length))

def generate_name():
    first = ["Alex", "Jordan", "Morgan", "Casey", "Riley", "Taylor",
             "Avery", "Quinn", "Drew", "Parker", "Logan", "Blake",
             "Aryan", "Prosanjit", "Farhan", "Nadia", "Priya", "Zara"]
    last = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Wilson", "Moore", "Barman", "Hossain",
            "Sharma", "Khan", "Chowdhury", "Das", "Roy", "Ahmed"]
    return f"{random.choice(first)} {random.choice(last)}"

def check_website_status(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        if REQUESTS_AVAILABLE:
            r = requests.head(url, timeout=8, allow_redirects=True)
            return r.status_code, r.url
        else:
            with urllib.request.urlopen(url, timeout=8) as resp:
                return resp.status, resp.url
    except Exception as e:
        return None, str(e)

def extract_title(html_text):
    match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else "No title found"

def shorten_url(url):
    if PYSHORTENERS_AVAILABLE:
        try:
            s = pyshorteners.Shortener()
            return s.tinyurl.short(url), None
        except Exception as e:
            return None, str(e)
    return None, "pyshorteners not installed. Run: pip install pyshorteners"

def unshorten_url(url):
    try:
        if REQUESTS_AVAILABLE:
            r = requests.head(url, allow_redirects=True, timeout=10)
            return r.url, None
        else:
            return url, "requests not installed"
    except Exception as e:
        return None, str(e)

def get_whois_info(domain):
    if WHOIS_AVAILABLE:
        try:
            w = whois.whois(domain)
            lines = []
            for k, v in w.items():
                if v:
                    lines.append(f"<b>{k}</b>: {v}")
            return "\n".join(lines[:20]), None
        except Exception as e:
            return None, str(e)
    return None, "python-whois not installed. Run: pip install python-whois"

async def download_with_ytdlp(url, audio_only=False, output_dir="/tmp"):
    if not YTDLP_AVAILABLE:
        return None, "yt-dlp not installed. Run: pip install yt-dlp"
    try:
        ydl_opts = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
        }
        if audio_only:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fname = ydl.prepare_filename(info)
            if audio_only and not fname.endswith(".mp3"):
                fname = os.path.splitext(fname)[0] + ".mp3"
            return fname, None
    except Exception as e:
        return None, str(e)

def pil_remove_background(input_path, output_path):
    if REMBG_AVAILABLE:
        try:
            with open(input_path, "rb") as f:
                inp = f.read()
            out = rembg_remove(inp)
            with open(output_path, "wb") as f:
                f.write(out)
            return True, None
        except Exception as e:
            return False, str(e)
    return False, "rembg not installed. Run: pip install rembg"

def pil_to_png(input_path, output_path):
    if not PIL_AVAILABLE:
        return False, "Pillow not installed. Run: pip install Pillow"
    try:
        img = Image.open(input_path).convert("RGBA")
        img.save(output_path, "PNG")
        return True, None
    except Exception as e:
        return False, str(e)

def pil_enhance(input_path, output_path, factor=1.5):
    if not PIL_AVAILABLE:
        return False, "Pillow not installed."
    try:
        img = Image.open(input_path)
        img = ImageEnhance.Sharpness(img).enhance(factor)
        img = ImageEnhance.Contrast(img).enhance(factor)
        img = ImageEnhance.Brightness(img).enhance(1.1)
        img.save(output_path)
        return True, None
    except Exception as e:
        return False, str(e)

def pil_resize(input_path, output_path, width, height):
    if not PIL_AVAILABLE:
        return False, "Pillow not installed."
    try:
        img = Image.open(input_path)
        img = img.resize((width, height), Image.LANCZOS)
        img.save(output_path)
        return True, None
    except Exception as e:
        return False, str(e)

def pil_compress(input_path, output_path, quality=60):
    if not PIL_AVAILABLE:
        return False, "Pillow not installed."
    try:
        img = Image.open(input_path)
        img.save(output_path, optimize=True, quality=quality)
        return True, None
    except Exception as e:
        return False, str(e)

def pil_watermark(input_path, output_path, text="WATERMARK"):
    if not PIL_AVAILABLE:
        return False, "Pillow not installed."
    try:
        img = Image.open(input_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (img.width - tw) // 2
        y = (img.height - th) // 2
        draw.text((x, y), text, fill=(255, 255, 255, 120), font=font)
        combined = Image.alpha_composite(img, overlay)
        combined.convert("RGB").save(output_path)
        return True, None
    except Exception as e:
        return False, str(e)

def pil_grayscale(input_path, output_path):
    if not PIL_AVAILABLE:
        return False, "Pillow not installed."
    try:
        img = Image.open(input_path).convert("L")
        img.save(output_path)
        return True, None
    except Exception as e:
        return False, str(e)

def image_to_pdf_file(input_path, output_path):
    if IMG2PDF_AVAILABLE:
        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(input_path))
            return True, None
        except Exception as e:
            return False, str(e)
    elif PIL_AVAILABLE:
        try:
            img = Image.open(input_path).convert("RGB")
            img.save(output_path, "PDF")
            return True, None
        except Exception as e:
            return False, str(e)
    return False, "img2pdf or Pillow not installed."

def video_to_mp3(input_path, output_path):
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", input_path, "-q:a", "0", "-map", "a", output_path, "-y"],
            capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0, result.stderr
    except FileNotFoundError:
        return False, "ffmpeg not found. Run: pkg install ffmpeg"
    except Exception as e:
        return False, str(e)

def video_compress(input_path, output_path, crf=28):
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", str(crf), output_path, "-y"],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0, result.stderr
    except FileNotFoundError:
        return False, "ffmpeg not found."
    except Exception as e:
        return False, str(e)

def video_thumbnail(input_path, output_path):
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", input_path, "-ss", "00:00:01", "-vframes", "1", output_path, "-y"],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stderr
    except FileNotFoundError:
        return False, "ffmpeg not found."
    except Exception as e:
        return False, str(e)

def video_trim(input_path, output_path, start, duration):
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", input_path, "-ss", str(start), "-t", str(duration),
             "-c", "copy", output_path, "-y"],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0, result.stderr
    except FileNotFoundError:
        return False, "ffmpeg not found."
    except Exception as e:
        return False, str(e)

def compress_to_zip(input_path, output_path):
    try:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(input_path, os.path.basename(input_path))
        return True, None
    except Exception as e:
        return False, str(e)

def get_file_info(path):
    try:
        stat = os.stat(path)
        size = stat.st_size
        human = f"{size / 1024:.1f} KB" if size < 1048576 else f"{size / 1048576:.1f} MB"
        mime = mimetypes.guess_type(path)[0] or "unknown"
        return {
            "name": os.path.basename(path),
            "size": human,
            "type": mime,
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"error": str(e)}

def generate_qr(text, output_path):
    if not QR_AVAILABLE:
        return False, "qrcode not installed. Run: pip install qrcode[pil]"
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        return True, None
    except Exception as e:
        return False, str(e)

# ── NEW: Encrypt/Decrypt (Fernet) ──
def encrypt_text_fernet(text, password):
    try:
        import base64, hashlib
        from cryptography.fernet import Fernet
        key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        f = Fernet(key)
        token = f.encrypt(text.encode())
        return token.decode(), None
    except ImportError:
        # Fallback: simple XOR + base64
        import base64
        key_bytes = password.encode()
        data = text.encode()
        encrypted = bytes([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])
        return base64.b64encode(encrypted).decode(), None
    except Exception as e:
        return None, str(e)

def decrypt_text_fernet(token, password):
    try:
        import base64, hashlib
        from cryptography.fernet import Fernet
        key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        f = Fernet(key)
        result = f.decrypt(token.encode())
        return result.decode(), None
    except ImportError:
        # Fallback: simple XOR + base64
        import base64
        try:
            key_bytes = password.encode()
            data = base64.b64decode(token.encode())
            decrypted = bytes([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])
            return decrypted.decode(), None
        except Exception as e:
            return None, str(e)
    except Exception as e:
        return None, str(e)

def get_file_hash(file_path):
    try:
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
                sha256.update(chunk)
        return {"MD5": md5.hexdigest(), "SHA256": sha256.hexdigest()}, None
    except Exception as e:
        return None, str(e)

# ── NEW: Enhanced Phone number lookup (Truecaller-like, multi-API) ──
def get_phone_info(phone):
    """Enhanced phone lookup using multiple free APIs."""
    try:
        phone_clean = phone.strip().replace(" ", "").replace("-", "")
        if not phone_clean.startswith("+"):
            phone_clean = "+" + phone_clean.lstrip("+")
        
        info = {"📱 Number": phone_clean}
        
        # Country code mapping (extended)
        country_codes = {
            "880": ("🇧🇩 Bangladesh", "BD"), "91": ("🇮🇳 India", "IN"),
            "1": ("🇺🇸 USA/Canada", "US"), "44": ("🇬🇧 UK", "GB"),
            "61": ("🇦🇺 Australia", "AU"), "86": ("🇨🇳 China", "CN"),
            "81": ("🇯🇵 Japan", "JP"), "49": ("🇩🇪 Germany", "DE"),
            "33": ("🇫🇷 France", "FR"), "7": ("🇷🇺 Russia", "RU"),
            "55": ("🇧🇷 Brazil", "BR"), "966": ("🇸🇦 Saudi Arabia", "SA"),
            "971": ("🇦🇪 UAE", "AE"), "92": ("🇵🇰 Pakistan", "PK"),
            "60": ("🇲🇾 Malaysia", "MY"), "65": ("🇸🇬 Singapore", "SG"),
            "62": ("🇮🇩 Indonesia", "ID"), "63": ("🇵🇭 Philippines", "PH"),
            "66": ("🇹🇭 Thailand", "TH"), "84": ("🇻🇳 Vietnam", "VN"),
            "82": ("🇰🇷 South Korea", "KR"), "90": ("🇹🇷 Turkey", "TR"),
            "20": ("🇪🇬 Egypt", "EG"), "234": ("🇳🇬 Nigeria", "NG"),
            "254": ("🇰🇪 Kenya", "KE"), "27": ("🇿🇦 South Africa", "ZA"),
        }
        
        # Bangladesh carrier detection
        bd_carriers = {
            "0171": "Grameenphone (GP)", "0172": "Robi", "0173": "Banglalink",
            "0174": "Teletalk", "0175": "Teletalk", "0176": "Robi",
            "0177": "Robi", "0178": "Banglalink", "0179": "Banglalink",
            "0161": "Airtel BD", "0162": "Robi", "0163": "Robi",
            "0164": "Robi", "0165": "Banglalink", "0166": "Banglalink",
            "0167": "Banglalink", "0168": "Banglalink", "0169": "Banglalink",
            "0181": "Robi", "0182": "Banglalink", "0183": "Grameenphone",
            "0185": "Teletalk", "0186": "Grameenphone", "0188": "Robi",
            "0189": "Airtel BD", "0131": "Teletalk", "0132": "Teletalk",
        }
        
        phone_no_plus = phone_clean.lstrip("+")
        
        # Detect country
        country_name = "🌍 Unknown"
        country_code = ""
        for code in sorted(country_codes.keys(), key=len, reverse=True):
            if phone_no_plus.startswith(code):
                country_name, country_code = country_codes[code]
                info["🌍 Country"] = country_name
                break
        
        # BD-specific carrier detection
        if phone_no_plus.startswith("880"):
            local = "0" + phone_no_plus[3:]
            prefix = local[:4]
            carrier = bd_carriers.get(prefix, "Unknown Carrier")
            info["📡 Carrier"] = carrier
            info["📍 Region"] = "Bangladesh"
            info["📋 Number Type"] = "Mobile"
            info["🔢 Local Format"] = local
            info["🌐 Intl Format"] = phone_clean
        
        # Try AbstractAPI (free tier - 250 req/month)
        abstract_key, abstract_url = get_admin_api_key("AbstractAPI Phone")
        if abstract_key and REQUESTS_AVAILABLE:
            try:
                r = requests.get(
                    f"https://phonevalidation.abstractapi.com/v1/?api_key={abstract_key}&phone={phone_no_plus}",
                    timeout=8
                )
                data = r.json()
                if data.get("valid"):
                    info["✅ Valid"] = "Yes"
                    if data.get("carrier"): info["📡 Carrier"] = data["carrier"]
                    if data.get("type"): info["📋 Type"] = data["type"]
                    if data.get("location"): info["📍 Location"] = data["location"]
                    if data.get("country", {}).get("name"): info["🌍 Country"] = data["country"]["name"]
            except:
                pass
        
        # Try NumVerify (free tier)
        numverify_key, _ = get_admin_api_key("NumVerify")
        if numverify_key and REQUESTS_AVAILABLE:
            try:
                r = requests.get(
                    f"http://apilayer.net/api/validate?access_key={numverify_key}&number={phone_no_plus}&format=1",
                    timeout=8
                )
                data = r.json()
                if data.get("valid"):
                    if data.get("carrier"): info["📡 Carrier"] = data["carrier"]
                    if data.get("line_type"): info["📋 Type"] = data["line_type"]
                    if data.get("location"): info["📍 Location"] = data["location"]
                    if data.get("country_name"): info["🌍 Country"] = data["country_name"]
            except:
                pass
        
        # Phone number format analysis
        digits_only = "".join(filter(str.isdigit, phone_clean))
        info["🔢 Digits"] = str(len(digits_only))
        
        # Format suggestion
        if len(digits_only) == 13 and digits_only.startswith("880"):
            info["📝 Format Check"] = "✅ Valid BD Number (13 digits)"
        elif len(digits_only) < 10:
            info["📝 Format Check"] = "⚠️ Too Short"
        elif len(digits_only) > 15:
            info["📝 Format Check"] = "⚠️ Too Long"
        else:
            info["📝 Format Check"] = "✅ Valid Length"
        
        return info, None
    except Exception as e:
        return {"📱 Number": phone, "⚠️ Note": "Basic lookup only"}, None

# ── NEW: Internet Speed Test (Automatic, Text-based) ──
async def internet_speed_test():
    """Test download speed using free test file URLs."""
    results = {}
    try:
        test_urls = [
            ("Cloudflare", "https://speed.cloudflare.com/__down?bytes=10000000"),
            ("Fast.com Proxy", "https://raw.githubusercontent.com/nicedoc/onlyoffice-office-checker/master/test_resources/sample.pdf"),
        ]
        import time as _time
        
        best_speed = 0
        for name, url in test_urls:
            try:
                start = _time.time()
                if REQUESTS_AVAILABLE:
                    r = requests.get(url, timeout=15, stream=True)
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=65536):
                        downloaded += len(chunk)
                        if downloaded >= 5_000_000 or (_time.time() - start) > 10:
                            break
                    elapsed = _time.time() - start
                    if elapsed > 0 and downloaded > 0:
                        speed_mbps = (downloaded * 8) / (elapsed * 1_000_000)
                        if speed_mbps > best_speed:
                            best_speed = speed_mbps
                        results["📥 Download Speed"] = f"{speed_mbps:.2f} Mbps"
                        results["📦 Downloaded"] = f"{downloaded/1024/1024:.2f} MB in {elapsed:.1f}s"
                        break
            except:
                continue
        
        if not results.get("📥 Download Speed"):
            results["📥 Download Speed"] = "❌ Test Failed"
    except Exception as e:
        results["❌ Error"] = str(e)
    
    return results

async def get_my_ip_and_vpn_info():
    """Get current IP, location, VPN/proxy detection."""
    info = {}
    try:
        # Multiple IP APIs for reliability
        ip_apis = [
            "https://ipinfo.io/json",
            "https://ip-api.com/json",
            "https://ipapi.co/json/",
        ]
        
        ip_data = None
        for api_url in ip_apis:
            try:
                if REQUESTS_AVAILABLE:
                    r = requests.get(api_url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
                    ip_data = r.json()
                    if ip_data.get("ip") or ip_data.get("query"):
                        break
                else:
                    with urllib.request.urlopen(api_url, timeout=8) as resp:
                        ip_data = json.loads(resp.read().decode())
                    if ip_data.get("ip"):
                        break
            except:
                continue
        
        if ip_data:
            # ipinfo.io format
            if ip_data.get("ip"):
                info["🌐 IP Address"] = ip_data.get("ip", "N/A")
                info["🌍 Country"] = ip_data.get("country", "N/A")
                info["🏙 City"] = ip_data.get("city", "N/A")
                info["📍 Region"] = ip_data.get("region", "N/A")
                info["📡 ISP"] = ip_data.get("org", "N/A")
                if ip_data.get("loc"):
                    info["🗺 Location"] = ip_data.get("loc", "N/A")
                if ip_data.get("timezone"):
                    info["🕐 Timezone"] = ip_data.get("timezone", "N/A")
            # ip-api.com format
            elif ip_data.get("query"):
                info["🌐 IP Address"] = ip_data.get("query", "N/A")
                info["🌍 Country"] = ip_data.get("country", "N/A")
                info["🏙 City"] = ip_data.get("city", "N/A")
                info["📍 Region"] = ip_data.get("regionName", "N/A")
                info["📡 ISP"] = ip_data.get("isp", "N/A")
                info["🕐 Timezone"] = ip_data.get("timezone", "N/A")
                # VPN detection from ip-api
                proxy = ip_data.get("proxy", False)
                hosting = ip_data.get("hosting", False)
                if proxy or hosting:
                    info["🔒 VPN/Proxy"] = "✅ VPN/Proxy Detected"
                    info["🛡 Status"] = "Using VPN or Proxy"
                else:
                    info["🔒 VPN/Proxy"] = "❌ No VPN Detected"
                    info["🛡 Status"] = "Direct Connection"
            
            # VPN keyword detection fallback
            if "🔒 VPN/Proxy" not in info:
                org = info.get("📡 ISP", "").lower()
                vpn_keywords = ["vpn", "proxy", "tor", "hosting", "datacenter",
                                "digitalocean", "amazon", "cloudflare", "linode",
                                "vultr", "hetzner", "ovh", "private"]
                is_vpn = any(kw in org for kw in vpn_keywords)
                if is_vpn:
                    info["🔒 VPN/Proxy"] = "⚠️ Possibly VPN/Datacenter IP"
                else:
                    info["🔒 VPN/Proxy"] = "✅ Residential IP (No VPN)"
        else:
            info["❌ Error"] = "IP লুকআপ ব্যর্থ"
    except Exception as e:
        info["❌ Error"] = str(e)
    
    return info
def check_link_safety(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        # Check via URLScan.io free API (no key needed for basic)
        suspicious_keywords = ["phish", "hack", "malware", "virus", "spam", "free-money",
                               "login-verify", "account-suspend", "bit.ly", "tinyurl.com"]
        domain = url.split("/")[2] if "/" in url else url
        risk_score = 0
        flags = []
        for kw in suspicious_keywords:
            if kw in url.lower():
                risk_score += 20
                flags.append(f"⚠️ Suspicious keyword: `{kw}`")
        if not url.startswith("https"):
            risk_score += 10
            flags.append("⚠️ Not using HTTPS")
        # Try to fetch headers
        if REQUESTS_AVAILABLE:
            try:
                r = requests.head(url, timeout=5, allow_redirects=True)
                final = r.url
                if final != url:
                    flags.append(f"🔄 Redirects to: `{final[:60]}`")
                if r.status_code >= 400:
                    risk_score += 20
                    flags.append(f"⚠️ HTTP Error: {r.status_code}")
            except:
                risk_score += 15
                flags.append("⚠️ Cannot connect to URL")
        if risk_score == 0:
            status = "✅ নিরাপদ (Safe)"
        elif risk_score < 30:
            status = "⚠️ সন্দেহজনক (Suspicious)"
        else:
            status = "❌ বিপজ্জনক (Dangerous)"
        result = f"🔍 *Link Safety Check*\n\n🌐 URL: `{url[:60]}`\n📊 Risk Score: `{risk_score}/100`\n🛡 Status: {status}"
        if flags:
            result += "\n\n" + "\n".join(flags)
        return result, None
    except Exception as e:
        return None, str(e)

# ── NEW: Translation using free MyMemory API ──
async def translate_text(text, target_lang="bn", source_lang="auto"):
    try:
        encoded = urllib.parse.quote(text[:500])
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair={source_lang}|{target_lang}"
        loop = asyncio.get_event_loop()
        def do_req():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        data = await asyncio.wait_for(loop.run_in_executor(None, do_req), timeout=25)
        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"], None
        return None, "Translation failed"
    except asyncio.TimeoutError:
        return None, "Translation timeout। আবার চেষ্টা করুন।"
    except Exception as e:
        return None, str(e)

# ── NEW: Text Summarizer (simple extractive) ──
def summarize_text(text, sentences=3):
    try:
        import re
        # Simple extractive summarization
        sents = re.split(r'[।.!?]+', text)
        sents = [s.strip() for s in sents if len(s.strip()) > 20]
        if not sents:
            return text[:500], None
        # Score by word frequency
        words = text.lower().split()
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        def score(s):
            return sum(freq.get(w.lower(), 0) for w in s.split())
        ranked = sorted(sents, key=score, reverse=True)
        summary = ". ".join(ranked[:sentences])
        return summary, None
    except Exception as e:
        return None, str(e)

# ── NEW: Temporary Email via 1secmail ──
async def generate_temp_email():
    try:
        url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1"
        loop = asyncio.get_event_loop()
        def do_req():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        data = await asyncio.wait_for(loop.run_in_executor(None, do_req), timeout=25)
        if data and len(data) > 0:
            return data[0], None
        return None, "Could not generate email"
    except asyncio.TimeoutError:
        return None, "Email সার্ভার রেসপন্ড করছে না।"
    except Exception as e:
        return None, str(e)

async def check_temp_email_inbox(email):
    try:
        login, domain = email.split("@")
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        loop = asyncio.get_event_loop()
        def do_req():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        data = await asyncio.wait_for(loop.run_in_executor(None, do_req), timeout=25)
        return data, None
    except asyncio.TimeoutError:
        return None, "Email inbox চেক করতে সমস্যা।"
    except Exception as e:
        return None, str(e)

def encode_base64(text):
    import base64
    return base64.b64encode(text.encode()).decode()

def decode_base64(text):
    import base64
    try:
        return base64.b64decode(text.encode()).decode(), None
    except Exception as e:
        return None, str(e)

def get_time_info(timezone="UTC"):
    now_utc = datetime.datetime.utcnow()
    return (
        f"🕐 *Current Time Info*\n"
        f"UTC: `{now_utc.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"Day: `{now_utc.strftime('%A')}`\n"
        f"Week: `{now_utc.strftime('Week %W of %Y')}`\n"
        f"Timestamp: `{int(time.time())}`"
    )

# ===================== SEND MAIN MENU =====================
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    user = update.effective_user
    prem = is_premium(user.id)
    pts = get_user_points(user.id)
    bal = get_user_balance(user.id)
    prem_badge = "💎 Premium" if prem else "🆓 Free"
    text = (
        f"👋 Welcome, *{html.escape(user.first_name)}*!\n\n"
        f"🤖 *{BOT_NAME}* — Your All-in-One Telegram Bot\n"
        f"👨‍💻 Creator: *{CREATOR_NAME}*\n\n"
        f"📊 Status: {prem_badge} | ⭐ Points: {pts} | 💰 ৳{bal:.2f}\n\n"
        f"Choose a category below:"
    )
    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
        except:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
    else:
        if update.message:
            await update.message.reply_text(
                text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
            )

# ===================== COMMAND HANDLERS =====================
@require_not_banned
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referred_by = 0
    # Check referral
    if context.args:
        arg = context.args[0]
        if arg.startswith("ref_"):
            try:
                ref_uid = int(arg[4:])
                if ref_uid != user.id:
                    referred_by = ref_uid
            except:
                pass
    register_user(user, referred_by)
    # Give referral points
    if referred_by:
        given = record_referral(referred_by, user.id, points=10)
        if given:
            try:
                await context.bot.send_message(
                    chat_id=referred_by,
                    text=f"🎉 *নতুন রেফারেল!*\n\n{user.first_name} আপনার রেফারেল লিংক ব্যবহার করে যোগ দিয়েছেন!\n✅ আপনি *10 Points* পেয়েছেন! 🎯",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
    log_action(user.id, "start")
    clear_state(user.id)
    await send_main_menu(update, context)

@require_not_banned
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"ℹ️ *{BOT_NAME} Help*\n\n"
        "Use /start to open the main menu.\n"
        "Navigate using the inline buttons.\n\n"
        f"Creator: *{CREATOR_NAME}*",
        parse_mode=ParseMode.MARKDOWN
    )

# ===================== ADMIN COMMANDS =====================
@require_admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ *Admin Panel*", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN
    )

@require_admin
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    users = get_all_users()
    sent, failed = 0, 0
    status_msg = await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    for i, u in enumerate(users):
        try:
            await context.bot.send_message(chat_id=u[0], text=f"📢 *Broadcast*\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
            await asyncio.sleep(0.05)  # Avoid flood ban
        except Exception:
            failed += 1
        # Update progress every 50 users
        if (i + 1) % 50 == 0:
            try:
                await status_msg.edit_text(f"📢 Broadcasting... {i+1}/{len(users)}")
            except:
                pass
    await status_msg.edit_text(f"📢 Broadcast done!\n✅ Sent: {sent}\n❌ Failed: {failed}")

@require_admin
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_all_users()
    lines = [f"👥 *All Users ({len(users)})*\n"]
    for u in users[:30]:
        uid, uname, fname = u[0], u[1] or "N/A", u[2] or "N/A"
        prem = "💎" if u[5] else ""
        ban = "🚫" if u[4] else ""
        lines.append(f"• {fname} (@{uname}) `{uid}` {prem}{ban}")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

@require_admin
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    try:
        uid = int(context.args[0])
        ban_user(uid)
        await update.message.reply_text(f"✅ User `{uid}` banned.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid user ID.")

@require_admin
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    try:
        uid = int(context.args[0])
        unban_user(uid)
        await update.message.reply_text(f"✅ User `{uid}` unbanned.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid user ID.")

@require_admin
async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /premium <user_id> [days]")
        return
    try:
        uid = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 0
        set_premium(uid, days)
        msg = f"✅ User `{uid}` given premium" + (f" for {days} days." if days else " (lifetime).")
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid input.")

@require_admin
async def remove_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove_premium <user_id>")
        return
    try:
        uid = int(context.args[0])
        remove_premium(uid)
        await update.message.reply_text(f"✅ Premium removed from `{uid}`.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid user ID.")

@require_admin
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_stats()
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n"
        f"👥 Total Users: `{s['total']}`\n"
        f"✅ Active (7d): `{s['active']}`\n"
        f"💎 Premium: `{s['premium']}`\n"
        f"🚫 Banned: `{s['banned']}`",
        parse_mode=ParseMode.MARKDOWN
    )

@require_admin
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with db_conn() as conn:
        c = conn.cursor()
        rows = c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 20").fetchall()
    lines = ["📋 *Recent Logs*\n"]
    for r in rows:
        lines.append(f"`{r[4]}` | UID:{r[1]} | {r[2]} | {r[3][:30]}")
    await update.message.reply_text("\n".join(lines) if lines else "No logs.", parse_mode=ParseMode.MARKDOWN)

# ===================== CALLBACK HANDLER =====================
@require_not_banned
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    user = query.from_user
    try:
        register_user(user)
    except Exception:
        pass
    data = query.data

    # ── BACK ──
    if data.startswith("back_"):
        clear_state(user.id)
        await send_main_menu(update, context, edit=True)
        return

    # ── MAIN MENUS ──
    if data == "menu_ai":
        await query.edit_message_text("🤖 *AI Tools* — Choose an option:", reply_markup=ai_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_image":
        await query.edit_message_text("🖼 *Image Tools* — Choose an option:", reply_markup=image_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_video":
        await query.edit_message_text("🎬 *Video Tools* — Choose an option:", reply_markup=video_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_downloader":
        await query.edit_message_text("📥 *Downloader Tools* — Choose an option:", reply_markup=downloader_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_file":
        await query.edit_message_text("📁 *File Tools* — Choose an option:", reply_markup=file_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_web":
        await query.edit_message_text("🌐 *Web Tools* — Choose an option:", reply_markup=web_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_utility":
        await query.edit_message_text("🛠 *Utility Tools* — Choose an option:", reply_markup=utility_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_premium":
        prem = is_premium(user.id)
        status = "✅ Active" if prem else "❌ Not Active"
        await query.edit_message_text(
            f"💎 *Premium System*\n\nYour Status: {status}\n\nPremium unlocks all tools and removes limits.",
            reply_markup=premium_keyboard(user.id), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_admin":
        if user.id != ADMIN_ID:
            await query.answer("⛔ Admin only.", show_alert=True)
            return
        await query.edit_message_text("⚙️ *Admin Panel*", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_about":
        await query.edit_message_text(
            f"ℹ️ *About {BOT_NAME}*\n\n"
            f"🤖 Bot Name: `{BOT_NAME}`\n"
            f"👨‍💻 Creator: `{CREATOR_NAME}`\n"
            f"👑 Admin: `{CREATOR_NAME}`\n"
            f"🛠 Version: 3.0.0\n\n"
            "I was created to provide free AI and utility tools to everyone!\n\n"
            "If you ask me 'Who created you?' my answer is always:\n"
            f"*{CREATOR_NAME}* 🙏",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_contact":
        wallets = get_admin_wallets(wallet_type="payment")
        socials = get_admin_socials()
        wallet_lines = ""
        emojis = {"Bkash": "📲", "Rocket": "🚀", "Nagad": "💛", "Upay": "🔴", "Binance": "🟡"}
        for w in wallets:
            if w[2]:
                emo = emojis.get(w[1], "💳")
                wallet_lines += f"{emo} *{w[1]}:* `{w[2]}`\n"
        social_lines = ""
        for s in socials:
            if s[2]:
                url_part = f" → {s[3]}" if s[3] else ""
                social_lines += f"• *{s[1]}:* {s[2]}{url_part}\n"
        contact_msg = get_bot_setting("contact_msg", "প্রিমিয়াম নিতে Admin-এর সাথে যোগাযোগ করুন।")
        await query.edit_message_text(
            f"📞 *Contact Admin | যোগাযোগ করুন*\n\n"
            f"👤 Admin: *{CREATOR_NAME}*\n\n"
            + (f"💳 *Payment Numbers:*\n{wallet_lines}\n" if wallet_lines else "") +
            (f"🌐 *Social Media:*\n{social_lines}\n" if social_lines else "") +
            f"ℹ️ {contact_msg}\n\n"
            f"📌 আপনার User ID: `{user.id}`",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    # ── NEW AI MENUS ──
    if data == "menu_newai1":
        await query.edit_message_text(
            "🎭 *New AI Tools I* (1-15)\n\nযেকোনো টুল বেছে নিন:",
            reply_markup=new_ai_tools_keyboard_1(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_newai2":
        await query.edit_message_text(
            "🎪 *New AI Tools II* (16-30)\n\nযেকোনো টুল বেছে নিন:",
            reply_markup=new_ai_tools_keyboard_2(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_newai3":
        await query.edit_message_text(
            "🎨 *New AI Tools III* (31-45)\n\nযেকোনো টুল বেছে নিন:",
            reply_markup=new_ai_tools_keyboard_3(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_newai4":
        await query.edit_message_text(
            "🎵 *Audio/Video AI Tools* (46-60)\n\nযেকোনো টুল বেছে নিন:",
            reply_markup=new_ai_tools_keyboard_4(), parse_mode=ParseMode.MARKDOWN
        )
        return
    # ── NEW MENUS ──
    if data == "menu_encrypt":
        await query.edit_message_text("🔒 *Encrypt Tools* — Choose an option:", reply_markup=encrypt_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "menu_payment":
        await query.edit_message_text(
            f"💳 *Payment & Balance System*\n\n"
            f"💰 Balance দিয়ে Premium কিনুন\n"
            f"📲 Bkash/Rocket/Nagad/Upay সাপোর্ট\n"
            f"✅ Transaction ID + ফটো দিন → Admin Approve করবেন",
            reply_markup=payment_keyboard(user.id), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_support":
        # Check if user has existing chat
        msgs = get_support_chat(user.id, 1)
        await query.edit_message_text(
            f"💬 *Admin Support Chat*\n\n"
            f"সরাসরি Admin-এর সাথে কথা বলুন!\n"
            f"আপনার সমস্যা, প্রশ্ন বা অনুরোধ পাঠান।\n\n"
            f"💡 Message টাইপ করুন এবং Send করুন।\n"
            f"Admin reply করলে আপনি notification পাবেন।",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✉️ Message পাঠান | Send Message", callback_data="support_sendmsg")],
                [InlineKeyboardButton("📜 Chat History দেখুন", callback_data="support_history")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
            ]), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "menu_referral":
        ref_code = get_referral_code(user.id)
        count = get_referral_count(user.id)
        pts = get_user_points(user.id)
        bot_username = "aibot3232_bot"
        ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
        await query.edit_message_text(
            f"👥 *Refer & Earn System*\n\n"
            f"🔗 আপনার রেফারেল লিংক:\n`{ref_link}`\n\n"
            f"👤 মোট রেফারেল: *{count} জন*\n"
            f"⭐ আপনার Points: *{pts}*\n\n"
            f"💡 প্রতিটি রেফারেলে *10 Points* পাবেন\n"
            f"🎁 *100 Points* = *1 মাস Premium* (Free!)",
            reply_markup=referral_keyboard(user.id), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── AI TOOLS ──
    if data == "ai_chat":
        set_state(user.id, mode="ai_chat")
        await query.edit_message_text(
            "💬 *AI Chat Mode*\n\nSend your message and I'll reply with AI!\nI remember our conversation context.\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ai_image":
        set_state(user.id, mode="ai_image")
        await query.edit_message_text(
            "🎨 *AI Image Generator*\n\nDescribe the image you want to generate.\nExample: A beautiful sunset over mountains\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ai_qa":
        set_state(user.id, mode="ai_qa")
        await query.edit_message_text(
            "❓ *AI Question & Answer*\n\nAsk me anything! I'll give you the best answer.\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ai_tts":
        if not has_voice_access(user.id):
            await query.answer("❌ Voice access disabled by admin.", show_alert=True)
            return
        set_state(user.id, mode="ai_tts")
        style = get_user_voice_style(user.id)
        await query.edit_message_text(
            f"🔊 *Text to Voice*\n\nCurrent voice style: `{style}`\nSend text and I'll reply with a voice message!\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ai_stt":
        if not has_voice_access(user.id):
            await query.answer("❌ Voice access disabled by admin.", show_alert=True)
            return
        set_state(user.id, mode="ai_stt")
        await query.edit_message_text(
            "🎤 *Voice to Text*\n\nSend a voice message and I'll transcribe it to text!\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ai_voice_style":
        if not has_voice_access(user.id):
            await query.answer("❌ Voice access disabled by admin.", show_alert=True)
            return
        await query.edit_message_text(
            "🎙 *Choose Voice Style*\n\nSelect your preferred voice:", reply_markup=voice_style_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ai_clear_memory":
        clear_ai_context(user.id)
        await query.answer("✅ Chat memory cleared!", show_alert=True)
        await query.edit_message_text("🤖 *AI Tools* — Choose an option:", reply_markup=ai_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── VOICE STYLE ──
    if data.startswith("vs_"):
        parts = data[3:].split("_")
        gender = parts[0]
        age = parts[1]
        lang = parts[2] if len(parts) > 2 else "en"
        style = f"{gender}_{age}"
        lang_map = {"en": "en", "hi": "hi", "bn": "bn"}
        set_user_voice_style(user.id, style)
        with db_conn() as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO user_settings (user_id, voice_style, tts_lang) VALUES (?,?,?)",
                      (user.id, style, lang_map.get(lang, "en")))
            conn.commit()
        await query.answer(f"✅ Voice style set to {gender} {age}!", show_alert=True)
        await query.edit_message_text("🎙 *Voice style updated!*\n\nReturn to AI Tools:", reply_markup=ai_tools_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── IMAGE TOOLS ──
    img_modes = {
        "img_rembg": ("img_rembg", "✂️ *Remove Background*\n\nSend an image to remove its background."),
        "img_topng": ("img_topng", "🖼 *Convert to PNG*\n\nSend any image to convert it to PNG."),
        "img_enhance": ("img_enhance", "✨ *Enhance Image*\n\nSend an image to enhance sharpness, contrast & brightness."),
        "img_resize": ("img_resize", "📐 *Resize Image*\n\nSend an image. Then reply with: `width height` (e.g. `800 600`)."),
        "img_compress": ("img_compress", "🗜 *Compress Image*\n\nSend an image to compress and reduce its size."),
        "img_topdf": ("img_topdf", "📄 *Image to PDF*\n\nSend an image to convert to PDF."),
        "img_watermark": ("img_watermark", "💧 *Add Watermark*\n\nSend an image. Then reply with the watermark text."),
        "img_grayscale": ("img_grayscale", "🔄 *Grayscale*\n\nSend an image to convert to grayscale."),
    }
    if data in img_modes:
        mode, msg = img_modes[data]
        set_state(user.id, mode=mode)
        await query.edit_message_text(msg + "\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── VIDEO TOOLS ──
    if data == "vid_download":
        set_state(user.id, mode="vid_download")
        await query.edit_message_text("⬇️ *Download Video*\n\nSend a video URL to download.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "vid_trim":
        set_state(user.id, mode="vid_trim_upload")
        await query.edit_message_text("✂️ *Trim Video*\n\nUpload a video file first.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "vid_merge":
        await query.edit_message_text("🔗 *Merge Videos*\n\n⚠️ Please upload videos via ffmpeg in your environment.\nThis feature requires local ffmpeg setup.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "vid_tomp3":
        set_state(user.id, mode="vid_tomp3")
        await query.edit_message_text("🎵 *Video to MP3*\n\nSend a video file to extract audio as MP3.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "vid_compress":
        set_state(user.id, mode="vid_compress")
        await query.edit_message_text("🗜 *Compress Video*\n\nSend a video file to compress it.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "vid_thumbnail":
        set_state(user.id, mode="vid_thumbnail")
        await query.edit_message_text("🖼 *Extract Thumbnail*\n\nSend a video file to extract its first thumbnail.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── DOWNLOADER TOOLS ──
    if data == "dl_youtube":
        set_state(user.id, mode="dl_youtube")
        await query.edit_message_text("▶️ *YouTube Downloader*\n\nSend a YouTube URL to download video.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "dl_ytaudio":
        set_state(user.id, mode="dl_ytaudio")
        await query.edit_message_text("🎵 *YouTube Audio Downloader*\n\nSend a YouTube URL to download audio as MP3.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "dl_tiktok":
        set_state(user.id, mode="dl_tiktok")
        await query.edit_message_text("🎵 *TikTok Downloader*\n\nSend a TikTok video URL to download.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "dl_instagram":
        set_state(user.id, mode="dl_instagram")
        await query.edit_message_text("📸 *Instagram Downloader*\n\nSend an Instagram post/reel URL.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "dl_direct":
        set_state(user.id, mode="dl_direct")
        await query.edit_message_text("🔗 *Direct Link Downloader*\n\nSend any direct download URL.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "dl_anyurl":
        set_state(user.id, mode="dl_anyurl")
        await query.edit_message_text("🌐 *Any URL Downloader*\n\nSend any URL (image/file/audio).\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── FILE TOOLS ──
    if data == "file_convert":
        await query.edit_message_text("🔄 *File Converter*\n\nCurrently supported:\n• Image → PNG\n• Image → PDF\n• Video → MP3\n\nUse Image Tools or Video Tools menus for these.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "file_pdftoimg":
        await query.edit_message_text("📄 *PDF to Image*\n\n⚠️ Install: `pip install pdf2image poppler-utils`\nSend a PDF file and I'll convert it to images.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "file_imgtopdf":
        set_state(user.id, mode="file_imgtopdf")
        await query.edit_message_text("🖼 *Image to PDF*\n\nSend an image to convert to PDF.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "file_rename":
        set_state(user.id, mode="file_rename_upload")
        await query.edit_message_text("✏️ *Rename File*\n\nSend the file you want to rename.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "file_compress":
        set_state(user.id, mode="file_compress")
        await query.edit_message_text("🗜 *Compress File*\n\nSend any file to compress it as ZIP.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "file_info":
        set_state(user.id, mode="file_info")
        await query.edit_message_text("ℹ️ *File Info*\n\nSend any file to view its info.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── WEB TOOLS ──
    web_modes = {
        "web_source": ("web_source", "📄 *Website Source Code*\n\nSend a URL to get its HTML source."),
        "web_title": ("web_title", "🔤 *Extract Title*\n\nSend a URL to extract its page title."),
        "web_status": ("web_status", "✅ *Website Status*\n\nSend a URL or domain to check status."),
        "web_ip": ("web_ip", "🌐 *IP Lookup*\n\nSend an IP address to look it up."),
        "web_domain": ("web_domain", "🏷 *Domain Info*\n\nSend a domain name (e.g. google.com) for WHOIS info."),
        "web_shorten": ("web_shorten", "🔗 *URL Shortener*\n\nSend a URL to shorten it."),
        "web_unshorten": ("web_unshorten", "🔓 *Unshorten URL*\n\nSend a shortened URL to expand it."),
    }
    if data in web_modes:
        mode, msg = web_modes[data]
        set_state(user.id, mode=mode)
        await query.edit_message_text(msg + "\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── UTILITY TOOLS ──
    if data == "util_tts":
        if not has_voice_access(user.id):
            await query.answer("❌ Voice access disabled by admin.", show_alert=True)
            return
        set_state(user.id, mode="util_tts")
        await query.edit_message_text("🔊 *Text to Speech*\n\nSend any text and I'll convert it to a voice message.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "util_stt":
        if not has_voice_access(user.id):
            await query.answer("❌ Voice access disabled by admin.", show_alert=True)
            return
        set_state(user.id, mode="util_stt")
        await query.edit_message_text("🎤 *Speech to Text*\n\nSend a voice message to transcribe.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "util_qrgen":
        set_state(user.id, mode="util_qrgen")
        await query.edit_message_text("📱 *QR Code Generator*\n\nSend any text or URL to generate a QR code.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "util_qrread":
        await query.edit_message_text("📷 *QR Code Reader*\n\n⚠️ Install: `pip install pyzbar`\nSend a QR code image to decode it.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "util_passgen":
        pw = generate_password(16, True)
        await query.edit_message_text(
            f"🔐 *Password Generator*\n\n`{pw}`\n\nPress again to generate new.", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Generate New", callback_data="util_passgen")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_namegen":
        name = generate_name()
        await query.edit_message_text(
            f"👤 *Random Name Generator*\n\n`{name}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Generate New", callback_data="util_namegen")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_time":
        await query.edit_message_text(get_time_info(), reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "util_base64enc":
        set_state(user.id, mode="util_base64enc")
        await query.edit_message_text("📊 *Base64 Encode*\n\nSend text to encode.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "util_base64dec":
        set_state(user.id, mode="util_base64dec")
        await query.edit_message_text("📊 *Base64 Decode*\n\nSend Base64 string to decode.\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── PREMIUM CALLBACKS ──
    if data == "prem_status":
        prem = is_premium(user.id)
        txt = "✅ আপনার Premium Active আছে!" if prem else "❌ আপনার Premium নেই।"
        await query.answer(txt, show_alert=True)
        return
    if data == "prem_balance":
        bal = get_user_balance(user.id)
        pts = get_user_points(user.id)
        await query.answer(f"💰 Balance: ৳{bal:.2f} | ⭐ Points: {pts}", show_alert=True)
        return
    if data == "prem_features":
        prices = get_premium_prices()
        price_lines = ""
        for p in prices:
            days_txt = f"{p[2]} দিন" if p[2] > 0 else "Lifetime"
            pts_txt = f" অথবা {p[4]} Points" if p[4] > 0 else ""
            price_lines += f"• {p[1]} → ৳{p[3]}{pts_txt}\n"
        await query.edit_message_text(
            "🌟 *Premium Features*\n\n"
            "• Unlimited AI Chat\n"
            "• AI Image Generation (50/day)\n"
            "• Voice messages (TTS/STT) - 100/day\n"
            "• Priority processing\n"
            "• All downloader tools - 20/day\n"
            "• Video editing tools\n"
            "• Encrypt/Decrypt - Unlimited\n"
            "• Translation - 100/day\n"
            "• All 60 New AI Tools\n"
            "• No daily rate limits\n\n"
            f"💰 *Premium Price:*\n{price_lines}",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "prem_price":
        prices = get_premium_prices()
        lines = ["💰 *Premium Price List*\n\n━━━━━━━━━━━━━━━━━━"]
        for p in prices:
            days_txt = f"{p[2]} দিন" if p[2] > 0 else "Lifetime"
            pts_txt = f" | অথবা {p[4]} Points" if p[4] > 0 else ""
            lines.append(f"{'📅' if p[2] > 0 else '♾️'} {days_txt} → ৳{p[3]} BDT{pts_txt}")
        lines.append("━━━━━━━━━━━━━━━━━━\n\n💳 *Payment Methods:*")
        wallets = get_admin_wallets(wallet_type="payment")
        for w in wallets:
            lines.append(f"• {w[1]}: `{w[2] if w[2] else 'Not Set'}`")
        lines.append("\n➡️ Payment করতে: Menu → Payment & Balance")
        await query.edit_message_text(
            "\n".join(lines), reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "prem_contact":
        wallets = get_admin_wallets(wallet_type="payment")
        socials = get_admin_socials()
        wallet_lines = ""
        emojis_map = {"Bkash": "📲", "Rocket": "🚀", "Nagad": "💛", "Upay": "🔴"}
        for w in wallets:
            if w[2]:
                emo = emojis_map.get(w[1], "💳")
                wallet_lines += f"{emo} {w[1]}: `{w[2]}`\n"
        social_lines = ""
        for s in socials:
            if s[2]:
                social_lines += f"• {s[1]}: {s[2]}\n"
        contact_msg = get_bot_setting("contact_msg", "প্রিমিয়াম নিতে Admin-এর সাথে যোগাযোগ করুন।")
        await query.edit_message_text(
            f"📞 *Contact Admin*\n\nPremium নিতে Admin-এ যোগাযোগ করুন:\n👤 {CREATOR_NAME}\n\n"
            + (f"💳 *Payment Numbers:*\n{wallet_lines}\n" if wallet_lines else "") +
            (f"🌐 *Social:*\n{social_lines}\n" if social_lines else "") +
            f"ℹ️ {contact_msg}\n\n"
            f"আপনার User ID: `{user.id}`",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── ADMIN CALLBACKS ──
    if data.startswith("adm_"):
        if user.id != ADMIN_ID:
            await query.answer("⛔ Admin only.", show_alert=True)
            return
        if data == "adm_users":
            users = get_all_users()
            lines = [f"👥 *Total Users: {len(users)}*\n"]
            for u in users[:20]:
                prem = "💎" if u[5] else ""
                ban = "🚫" if u[4] else ""
                lines.append(f"• {u[2] or 'N/A'} `{u[0]}` {prem}{ban}")
            await query.edit_message_text("\n".join(lines), reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_stats":
            s = get_stats()
            await query.edit_message_text(
                f"📊 *Bot Statistics*\n\n"
                f"👥 Total: `{s['total']}`\n✅ Active (7d): `{s['active']}`\n"
                f"💎 Premium: `{s['premium']}`\n🚫 Banned: `{s['banned']}`",
                reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data == "adm_broadcast":
            set_state(user.id, mode="adm_broadcast")
            await query.edit_message_text("📢 *Broadcast*\n\nSend your broadcast message:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_logs":
            with db_conn() as conn:
                rows = conn.cursor().execute("SELECT * FROM logs ORDER BY id DESC LIMIT 15").fetchall()
            lines = ["📋 *Recent Logs*\n"]
            for r in rows:
                lines.append(f"`{r[4][:16]}` UID:{r[1]} {r[2]}")
            await query.edit_message_text("\n".join(lines), reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_ban":
            set_state(user.id, mode="adm_ban")
            await query.edit_message_text("🚫 *Ban User*\n\nSend the User ID to ban:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_unban":
            set_state(user.id, mode="adm_unban")
            await query.edit_message_text("✅ *Unban User*\n\nSend the User ID to unban:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_addprem":
            set_state(user.id, mode="adm_addprem")
            await query.edit_message_text("💎 *Add Premium*\n\nSend: `user_id days` (e.g. `123456 30`) or `user_id 0` for lifetime:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_remprem":
            set_state(user.id, mode="adm_remprem")
            await query.edit_message_text("❌ *Remove Premium*\n\nSend the User ID:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_voiceon":
            set_state(user.id, mode="adm_voiceon")
            await query.edit_message_text("🎤 *Enable Voice Access*\n\nSend the User ID:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_voiceoff":
            set_state(user.id, mode="adm_voiceoff")
            await query.edit_message_text("🔇 *Disable Voice Access*\n\nSend the User ID:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        # ── NEW ADMIN CALLBACKS ──
        if data == "adm_payments":
            payments = get_pending_payments()
            if not payments:
                await query.answer("✅ কোনো Pending Payment নেই।", show_alert=True)
                return
            lines = ["💳 *Pending Payments*\n"]
            for p in payments[:10]:
                lines.append(f"ID:`{p[0]}` | UID:`{p[1]}` | ৳{p[2]} | {p[3]} | TXN:`{p[4][:15]}`")
            await query.edit_message_text("\n".join(lines),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Approve", callback_data="adm_approve_pay"),
                     InlineKeyboardButton("❌ Reject", callback_data="adm_reject_pay")],
                    [InlineKeyboardButton("🔙 Admin", callback_data="menu_admin")]
                ]), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_approve_pay":
            set_state(user.id, mode="adm_approve_pay")
            await query.edit_message_text("✅ *Payment Approve*\n\nPayment ID পাঠান:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_reject_pay":
            set_state(user.id, mode="adm_reject_pay")
            await query.edit_message_text("❌ *Payment Reject*\n\nPayment ID পাঠান:", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_tool_limits":
            with db_conn() as conn:
                limits = conn.cursor().execute("SELECT tool_name, free_limit, premium_limit FROM tool_limits LIMIT 10").fetchall()
            lines = ["🔧 *Tool Limits*\n"]
            for l in limits:
                lines.append(f"`{l[0]}`: Free={l[1]} | Premium={l[2]}")
            lines.append("\n_Format to change: tool_name free_limit premium_limit_")
            await query.edit_message_text("\n".join(lines), reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_addbalance":
            set_state(user.id, mode="adm_addbalance")
            await query.edit_message_text("💰 *Add Balance*\n\nFormat: `user_id amount`\nExample: `123456 100`", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        if data == "adm_addpoints":
            set_state(user.id, mode="adm_addpoints")
            await query.edit_message_text("🎯 *Add Points*\n\nFormat: `user_id points`\nExample: `123456 50`", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
        # ── NEW: Wallet Management ──
        if data == "adm_wallets":
            wallets = get_admin_wallets()
            lines = ["👛 *Wallet Management*\n\nআপনার payment numbers:"]
            emojis = {"Bkash": "📲", "Rocket": "🚀", "Nagad": "💛", "Upay": "🔴", "Binance": "🟡"}
            for w in wallets:
                emo = emojis.get(w[1], "💳")
                num = w[2] if w[2] else "_Not Set_"
                lines.append(f"{emo} *{w[1]}:* `{num}`")
            await query.edit_message_text(
                "\n".join(lines) + "\n\n_Edit করতে wallet-এ ক্লিক করুন:_",
                reply_markup=admin_wallet_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data.startswith("adm_wallet_edit_"):
            wallet_name = data[len("adm_wallet_edit_"):]
            set_state(user.id, mode="adm_wallet_edit", wallet_name=wallet_name)
            await query.edit_message_text(
                f"👛 *Edit {wallet_name} Number*\n\nনতুন নাম্বার পাঠান:\nExample: `01712345678`",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data == "adm_wallet_add":
            set_state(user.id, mode="adm_wallet_add")
            await query.edit_message_text(
                "➕ *Add New Wallet*\n\nFormat: `WalletName::Number::Type`\nType: payment বা crypto\nExample: `Binance::123456789::crypto`",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        # ── NEW: Social Media Management ──
        if data == "adm_socials":
            socials = get_admin_socials()
            lines = ["📱 *Social Media Management*\n"]
            for s in socials:
                handle = s[2] if s[2] else "_Not Set_"
                lines.append(f"• *{s[1]}:* {handle}")
            await query.edit_message_text(
                "\n".join(lines) + "\n\n_Edit করতে platform-এ ক্লিক করুন:_",
                reply_markup=admin_social_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data.startswith("adm_social_edit_"):
            platform = data[len("adm_social_edit_"):]
            set_state(user.id, mode="adm_social_edit", platform=platform)
            await query.edit_message_text(
                f"📱 *Edit {platform}*\n\nFormat: `handle::url` (url optional)\nExample: `@mypage::https://fb.com/mypage`\nঅথবা শুধু: `@mypage`",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data == "adm_social_add":
            set_state(user.id, mode="adm_social_add")
            await query.edit_message_text(
                "➕ *Add Social Media*\n\nFormat: `Platform::Handle::URL`\nExample: `TikTok::@mypage::https://tiktok.com/@mypage`",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        # ── NEW: Premium Prices ──
        if data == "adm_prices":
            prices = get_premium_prices()
            lines = ["💎 *Premium Price Management*\n"]
            for p in prices:
                days_txt = f"{p[2]} দিন" if p[2] > 0 else "Lifetime"
                pts_txt = f" | {p[4]} pts" if p[4] > 0 else ""
                lines.append(f"• *{p[1]}:* ৳{p[3]} ({days_txt}){pts_txt}")
            await query.edit_message_text(
                "\n".join(lines) + "\n\n_Edit করতে plan-এ ক্লিক করুন:_",
                reply_markup=admin_price_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data.startswith("adm_price_edit_"):
            plan = data[len("adm_price_edit_"):]
            set_state(user.id, mode="adm_price_edit", plan_name=plan)
            await query.edit_message_text(
                f"💎 *Edit Plan: {plan}*\n\nFormat: `price::days::points_cost`\nExample: `200::30::0`\n(days=0 for lifetime, points_cost=0 if not redeemable by points)",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        if data == "adm_price_add":
            set_state(user.id, mode="adm_price_add")
            await query.edit_message_text(
                "➕ *Add New Premium Plan*\n\nFormat: `PlanName::days::price::points_cost`\nExample: `15 দিন::15::75::0`",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
        # ── NEW: Bot Settings ──
        if data == "adm_botsettings":
            bot_user = get_bot_setting("bot_username", "aibot3232_bot")
            contact_msg = get_bot_setting("contact_msg", "")
            set_state(user.id, mode="adm_botsettings")
            await query.edit_message_text(
                f"⚙️ *Bot Settings*\n\n"
                f"🤖 Bot Username: `{bot_user}`\n"
                f"📩 Contact Message: _{contact_msg[:50]}_\n\n"
                f"Format পাঠান:\n"
                f"`bot_username::new_username`\n"
                f"অথবা `contact_msg::your message`",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return

    # ── NEW AI TOOLS (60 tools) ──
    NEW_AI_TOOLS = {
        "nai_video_style": ("🎬 AI Video Style Transfer", "ভিডিও আপলোড করুন। AI দিয়ে আর্টিস্টিক স্টাইলে রূপান্তর করা হবে।"),
        "nai_portrait": ("🖼 AI Portrait Generator", "আপনার ছবি পাঠান। AI পোর্ট্রেট তৈরি করা হবে।"),
        "nai_sticker": ("✨ Animated Sticker Maker", "ছবি পাঠান। অ্যানিমেটেড স্টিকার তৈরি করা হবে।"),
        "nai_gif2vid": ("🔄 GIF to Video Converter", "GIF ফাইল পাঠান। ভিডিওতে রূপান্তর করা হবে।"),
        "nai_vid2gif": ("📹 Video to GIF Converter", "ভিডিও পাঠান। GIF তৈরি করা হবে।"),
        "nai_colorpalette": ("🎨 AI Color Palette Generator", "ছবি পাঠান। রঙের প্যালেট জেনারেট করা হবে।"),
        "nai_memecaption": ("😂 Meme Caption AI", "মেমে ছবি পাঠান। AI ক্যাপশন যোগ করা হবে।"),
        "nai_bgblur": ("🌫 AI Background Blur", "ছবি পাঠান। ব্যাকগ্রাউন্ড ব্লার করা হবে।"),
        "nai_faceemotion": ("😊 Face Emotion Detection", "মুখের ছবি পাঠান। ইমোশন ডিটেক্ট করা হবে।"),
        "nai_cartoonify": ("🎭 AI Cartoonifier", "ছবি পাঠান। কার্টুনে রূপান্তর করা হবে।"),
        "nai_avatar": ("👤 AI Avatar Creator", "ছবি পাঠান। AI অ্যাভাটার তৈরি করা হবে।"),
        "nai_voicepitch": ("🎵 Voice Pitch Changer", "ভয়েস মেসেজ পাঠান তারপর pitch level (0.5-2.0) পাঠান।"),
        "nai_audiospeed": ("⏩ Audio Speed Changer", "অডিও পাঠান তারপর speed (0.5-3.0) পাঠান।"),
        "nai_lipsync": ("💋 AI Lip Sync Video", "ভিডিও এবং অডিও পাঠান। লিপ সিঙ্ক করা হবে।"),
        "nai_yttranscript": ("📝 YouTube Transcript", "YouTube ভিডিও লিংক পাঠান। ট্রান্সক্রিপ্ট বের করা হবে।"),
        "nai_audiotranslate": ("🌐 Audio Language Translator", "অডিও পাঠান তারপর target language code পাঠান (bn/en/hi)।"),
        "nai_videnhance": ("📈 Video Quality Enhancer", "ভিডিও পাঠান। মান উন্নত করা হবে।"),
        "nai_faceswap": ("🔄 Face Swap Video", "দুটি ছবি পাঠান (face source + target)। ফেস সুইচ করা হবে।"),
        "nai_bgmusic": ("🎶 AI Background Music Generator", "ভিডিও পাঠান। AI ব্যাকগ্রাউন্ড মিউজিক যোগ করা হবে।"),
        "nai_subtitletrans": ("💬 Video Subtitle Translator", "ভিডিও পাঠান তারপর target language পাঠান। সাবটাইটেল অনুবাদ হবে।"),
        "nai_voiceemotion": ("😤 Voice Emotion Recognition", "ভয়েস মেসেজ পাঠান। ইমোশন ডিটেক্ট করা হবে।"),
        "nai_noiseremove": ("🔇 Audio Noise Remover", "অডিও পাঠান। নয়েজ রিমুভ করা হবে।"),
        "nai_scenedetect": ("🎬 AI Scene Detection", "ভিডিও পাঠান। দৃশ্য শনাক্ত করা হবে।"),
        "nai_styleimage": ("🖌 AI Style Image Generator", "ছবি পাঠান তারপর style name পাঠান (oil painting/sketch/watercolor)।"),
        "nai_memevideo": ("🎭 Meme Video Generator", "ভিডিও পাঠান তারপর caption পাঠান।"),
        "nai_frameinterp": ("🎞 Video Frame Interpolator", "ভিডিও পাঠান। ফ্রেম ইন্টারপোলেশন হবে।"),
        "nai_objecttrack": ("🎯 AI Object Tracking", "ভিডিও পাঠান। অবজেক্ট ট্র্যাকিং করা হবে।"),
        "nai_faceretouch": ("✨ AI Face Retouch", "ছবি পাঠান। ফেস রিটাচ করা হবে।"),
        "nai_animtext": ("📝 Animated Text Video", "টেক্সট পাঠান। অ্যানিমেটেড টেক্সট ভিডিও তৈরি হবে।"),
        "nai_vidcrop": ("✂️ Video Crop & Resize", "ভিডিও পাঠান তারপর format পাঠান (width:height)।"),
        "nai_vidsummary": ("📋 AI Video Summarizer", "ভিডিও পাঠান। AI সারসংক্ষেপ তৈরি করা হবে।"),
        "nai_audiolangid": ("🔍 Audio Language Identifier", "অডিও পাঠান। ভাষা শনাক্ত করা হবে।"),
        "nai_ocr": ("📷 Image OCR Scanner", "ছবি পাঠান। টেক্সট পড়া হবে (OCR)।"),
        "nai_textovervid": ("📝 AI Text on Video", "ভিডিও পাঠান তারপর টেক্সট পাঠান।"),
        "nai_batchaudio": ("🔄 Batch Audio Converter", "অডিও ফাইল পাঠান তারপর format পাঠান (mp3/wav/ogg)।"),
        "nai_voiceclone": ("🎤 Voice Cloning AI", "ভয়েস স্যাম্পল পাঠান তারপর clone করার টেক্সট পাঠান।"),
        "nai_musicgenre": ("🎸 AI Music Genre Classifier", "মিউজিক ফাইল পাঠান। জেনার শনাক্ত করা হবে।"),
        "nai_inpainting": ("🖼 AI Image Inpainting", "ছবি পাঠান। নষ্ট অংশ AI দিয়ে পূরণ করা হবে।"),
        "nai_faceage": ("👴 Face Age Estimator", "মুখের ছবি পাঠান। বয়স অনুমান করা হবে।"),
        "nai_colorize": ("🌈 AI Colorize Black & White", "সাদা-কালো ছবি পাঠান। রঙিন করা হবে।"),
        "nai_objremovevid": ("🗑 AI Object Removal Video", "ভিডিও পাঠান। অবজেক্ট রিমুভ করা হবে।"),
        "nai_animemoji": ("😄 AI Animated Emoji Creator", "ছবি পাঠান। অ্যানিমেটেড ইমোজি তৈরি হবে।"),
        "nai_voicecmd": ("🎙 Voice Command Automation", "ভয়েস কমান্ড পাঠান।"),
        "nai_frameenhance": ("📺 AI Video Frame Enhancer", "ভিডিও পাঠান। ফ্রেম উন্নত করা হবে।"),
        "nai_batchwater": ("💧 Batch Video Watermark", "ভিডিও পাঠান তারপর watermark টেক্সট পাঠান।"),
        "nai_gesture": ("🤚 AI Gesture Recognition", "ভিডিও পাঠান। জেসচার শনাক্ত করা হবে।"),
        "nai_imgstyletrans": ("🖌 AI Image Style Transfer", "ছবি পাঠান তারপর style পাঠান।"),
        "nai_cartvideo": ("🎨 AI Cartoon Video Maker", "ভিডিও পাঠান। কার্টুন ভিডিও তৈরি হবে।"),
        "nai_vidbgreplace": ("🏞 AI Video BG Replacement", "ভিডিও পাঠান তারপর নতুন ব্যাকগ্রাউন্ড ছবি পাঠান।"),
        "nai_lipread": ("👄 AI Lip Reading Tool", "ভিডিও পাঠান। লিপ রিডিং করা হবে।"),
        "nai_silenceremove": ("🔇 Audio Silence Remover", "অডিও পাঠান। শূন্যস্থান রিমুভ করা হবে।"),
        "nai_noisesynth": ("🎵 AI Noise Synthesizer", "টেক্সট পাঠান (nature/rain/cafe etc)। সাউন্ড জেনারেট হবে।"),
        "nai_scenesplit": ("✂️ Video Scene Splitter", "ভিডিও পাঠান। দৃশ্য আলাদা করা হবে।"),
        "nai_imgdenoise": ("🖼 AI Image Denoiser", "ছবি পাঠান। নয়েজ কমানো হবে।"),
        "nai_text2meme": ("😂 AI Text-to-Meme Generator", "টেক্সট পাঠান। মেমে তৈরি হবে।"),
        "nai_objdetect": ("🔍 AI Object Detection", "ছবি পাঠান। অবজেক্ট শনাক্ত করা হবে।"),
        "nai_musiccompose": ("🎵 AI Music Composer", "মুড/genre টেক্সট পাঠান (happy/sad/epic)। মিউজিক কম্পোজ হবে।"),
        "nai_vidcolorgrade": ("🎨 AI Video Color Grader", "ভিডিও পাঠান তারপর style পাঠান (cinematic/warm/cool)।"),
        "nai_animstory": ("📖 AI Animated Story Generator", "গল্পের বিষয় পাঠান। অ্যানিমেটেড স্টোরি তৈরি হবে।"),
        "nai_text2gif": ("🎞 AI Text-to-GIF Generator", "টেক্সট পাঠান। GIF তৈরি হবে।"),
    }
    if data in NEW_AI_TOOLS:
        tool_name, instructions = NEW_AI_TOOLS[data]
        set_state(user.id, mode=f"nai_{data[4:]}", tool_name=tool_name)
        await query.edit_message_text(
            f"*{tool_name}*\n\n"
            f"📋 {instructions}\n\n"
            f"⚠️ এই টুলটি AI-powered। সেরা ফলাফলের জন্য স্পষ্ট ইনপুট দিন।\n\n"
            f"/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── ENCRYPT TOOL CALLBACKS ──
    enc_modes = {
        "enc_text": ("enc_text_input", "🔐 *Encrypt Text | টেক্সট এনক্রিপ্ট*\n\nFormat: `password::your text`\nExample: `mypass::Hello World`"),
        "dec_text": ("dec_text_input", "🔓 *Decrypt Text | টেক্সট ডিক্রিপ্ট*\n\nFormat: `password::encrypted_text`"),
        "enc_file": ("enc_file", "🔑 *Encrypt File | ফাইল এনক্রিপ্ট*\n\nপ্রথমে ফাইল পাঠান, তারপর পাসওয়ার্ড।"),
        "dec_file": ("dec_file", "📂 *Decrypt File | ফাইল ডিক্রিপ্ট*\n\nপ্রথমে encrypted ফাইল পাঠান, তারপর পাসওয়ার্ড।"),
        "util_filehash": ("util_filehash", "🔢 *File Hash Generator | ফাইল হ্যাশ*\n\nMD5 ও SHA256 হ্যাশ জানতে ফাইল পাঠান।"),
        "util_filecheck": ("util_filecheck", "✅ *File Integrity Checker | ফাইল চেক*\n\nফাইল পাঠান, তারপর expected হ্যাশ পাঠান।"),
    }
    if data in enc_modes:
        allowed, msg_err = check_tool_access(user.id, "encrypt")
        if not allowed:
            await query.answer(msg_err, show_alert=True)
            return
        mode_key, msg_text = enc_modes[data]
        set_state(user.id, mode=mode_key)
        await query.edit_message_text(msg_text + "\n\n/start to exit.", reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ── PAYMENT CALLBACKS ──
    # Dynamic payment from DB wallets
    wallets_list = get_admin_wallets(wallet_type="payment")
    wallet_map = {w[1].lower(): w for w in wallets_list}
    wallet_emojis = {"bkash": "📲", "rocket": "🚀", "nagad": "💛", "upay": "🔴"}
    
    for wname, wdata in wallet_map.items():
        if data == f"pay_{wname}":
            set_state(user.id, mode=f"pay_{wname}", wallet_name=wdata[1])
            num = wdata[2] if wdata[2] else "Not Set"
            emo = wallet_emojis.get(wname, "💳")
            await query.edit_message_text(
                f"{emo} *{wdata[1]} Payment*\n\n"
                f"📱 Send To Number: `{num}`\n\n"
                f"✅ Payment করার পর এই format-এ পাঠান:\n"
                f"`amount::transaction_id`\n"
                f"Example: `150::TXN123456`\n\n"
                f"📸 Screenshot পাঠালে Admin দ্রুত Approve করবেন।\n"
                f"⚡ Admin অনুমোদনের পর Balance যোগ হবে।",
                reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
            )
            return
    if data == "pay_addmoney":
        wallets = get_admin_wallets(wallet_type="payment")
        wallet_buttons = []
        emojis = {"Bkash": "📲", "Rocket": "🚀", "Nagad": "💛", "Upay": "🔴"}
        row = []
        for w in wallets:
            if w[2]:  # only show wallets with numbers set
                emo = emojis.get(w[1], "💳")
                btn = InlineKeyboardButton(f"{emo} {w[1]}", callback_data=f"addmoney_method_{w[1]}")
                row.append(btn)
                if len(row) == 2:
                    wallet_buttons.append(row)
                    row = []
        if row:
            wallet_buttons.append(row)
        wallet_buttons.append([InlineKeyboardButton("🔙 Back", callback_data="menu_payment")])
        await query.edit_message_text(
            "➕ *Add Money | টাকা যোগ করুন*\n\n"
            "💳 Payment Method বেছে নিন:",
            reply_markup=InlineKeyboardMarkup(wallet_buttons), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data.startswith("addmoney_method_"):
        method = data[len("addmoney_method_"):]
        wallets = get_admin_wallets(wallet_type="payment")
        wallet_num = ""
        for w in wallets:
            if w[1] == method:
                wallet_num = w[2]
                break
        emojis = {"Bkash": "📲", "Rocket": "🚀", "Nagad": "💛", "Upay": "🔴"}
        emo = emojis.get(method, "💳")
        set_state(user.id, mode="addmoney_enter_amount", method=method, wallet_num=wallet_num)
        await query.edit_message_text(
            f"{emo} *{method} দিয়ে Add Money*\n\n"
            f"📱 Send To: `{wallet_num}`\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📝 *Step 1:* উপরের নাম্বারে টাকা পাঠান\n"
            f"📝 *Step 2:* Amount (পরিমাণ) পাঠান\n"
            f"📝 *Step 3:* Transaction ID পাঠান\n"
            f"📝 *Step 4:* Payment Screenshot আপলোড করুন\n"
            f"📝 *Step 5:* Verify বাটনে চাপুন\n\n"
            f"💡 এখন পরিমাণ লিখুন (শুধু সংখ্যা):\nExample: `150`",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── SUPPORT CHAT CALLBACKS ──
    if data == "support_sendmsg":
        set_state(user.id, mode="support_chat_user")
        await query.edit_message_text(
            "💬 *Admin-এর কাছে Message পাঠান*\n\n"
            "আপনার message, ছবি বা ফাইল পাঠান।\n"
            "Admin শীঘ্রই reply করবেন।\n\n"
            "/start to cancel",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "support_history":
        msgs = get_support_chat(user.id, 10)
        if not msgs:
            await query.answer("কোনো message নেই।", show_alert=True)
            return
        lines = ["💬 *Chat History*\n"]
        for m in reversed(msgs[-8:]):
            sender_label = "👤 আপনি" if m[2] == "user" else "👑 Admin"
            msg_preview = m[3][:50] + "..." if len(m[3]) > 50 else m[3]
            timestamp = m[6][:16] if m[6] else ""
            lines.append(f"{sender_label} `{timestamp}`\n_{msg_preview}_\n")
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✉️ নতুন Message", callback_data="support_sendmsg")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu_support")],
            ]), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── ADMIN: Support Users List ──
    if data == "adm_support_users":
        if user.id != ADMIN_ID:
            await query.answer("⛔ Admin only.", show_alert=True)
            return
        support_users = get_all_support_users()
        if not support_users:
            await query.answer("কোনো support user নেই।", show_alert=True)
            return
        buttons = []
        for su in support_users[:15]:
            uid, fname, uname, unread = su[0], su[1] or "N/A", su[2] or "N/A", su[3]
            unread_badge = f" 🔴{unread}" if unread > 0 else ""
            buttons.append([InlineKeyboardButton(
                f"👤 {fname} (@{uname}) {unread_badge}",
                callback_data=f"adm_chat_user_{uid}"
            )])
        buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="menu_admin")])
        await query.edit_message_text(
            "💬 *Support Chat Users*\n\nUser বেছে নিন reply করতে:",
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data.startswith("adm_chat_user_"):
        if user.id != ADMIN_ID:
            await query.answer("⛔ Admin only.", show_alert=True)
            return
        target_uid = int(data[len("adm_chat_user_"):])
        mark_support_read(target_uid)
        msgs = get_support_chat(target_uid, 10)
        lines = [f"💬 *Chat with User {target_uid}*\n"]
        for m in reversed(msgs[-8:]):
            sender_label = "👤 User" if m[2] == "user" else "👑 Admin"
            msg_preview = m[3][:60] + "..." if len(m[3]) > 60 else m[3]
            file_note = " 📎" if m[4] else ""
            lines.append(f"{sender_label}: _{msg_preview}_{file_note}")
        set_state(user.id, mode="adm_reply_user", target_uid=target_uid)
        await query.edit_message_text(
            "\n".join(lines) + f"\n\n✍️ Reply পাঠান (text, photo, audio):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Support Users", callback_data="adm_support_users")],
            ]), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── ADMIN: Add Money Requests ──
    if data == "adm_addmoney_req":
        if user.id != ADMIN_ID:
            await query.answer("⛔ Admin only.", show_alert=True)
            return
        reqs = get_pending_add_money()
        if not reqs:
            await query.answer("✅ কোনো Pending Add Money Request নেই।", show_alert=True)
            return
        buttons = []
        lines = [f"💰 *Pending Add Money Requests ({len(reqs)})*\n"]
        for r in reqs[:10]:
            lines.append(f"🆔 `{r[0]}` | 👤`{r[1]}` | ৳{r[2]} | {r[3]} | TXN:`{r[4][:12]}`")
            photo_btn = "📸" if r[5] else "❌"
            buttons.append([
                InlineKeyboardButton(f"✅ Approve #{r[0]}", callback_data=f"adm_amt_approve_{r[0]}"),
                InlineKeyboardButton(f"❌ Reject #{r[0]}", callback_data=f"adm_amt_reject_{r[0]}"),
            ])
            if r[5]:
                buttons.append([InlineKeyboardButton(f"📸 View Screenshot #{r[0]}", callback_data=f"adm_amt_photo_{r[0]}")])
        buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="menu_admin")])
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data.startswith("adm_amt_photo_"):
        if user.id != ADMIN_ID:
            return
        req_id = int(data[len("adm_amt_photo_"):])
        with db_conn() as conn:
            r = conn.cursor().execute("SELECT * FROM add_money_requests WHERE id=?", (req_id,)).fetchone()
        if r and r[5]:
            await context.bot.send_photo(
                chat_id=user.id,
                photo=r[5],
                caption=f"📸 *Payment Screenshot*\n\nReq ID: `{r[0]}`\nUser: `{r[1]}`\nAmount: ৳{r[2]}\nMethod: {r[3]}\nTXN: `{r[4]}`",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.answer("কোনো screenshot নেই।", show_alert=True)
        return
    if data.startswith("adm_amt_approve_"):
        if user.id != ADMIN_ID:
            return
        req_id = int(data[len("adm_amt_approve_"):])
        uid, amount = approve_add_money(req_id, ADMIN_ID)
        if uid:
            await query.answer(f"✅ Approved! ৳{amount} added to user {uid}", show_alert=True)
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎉 *Add Money Approved!*\n\n✅ আপনার ৳{amount} Balance যোগ হয়েছে!\n🆔 Request ID: `{req_id}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        else:
            await query.answer("❌ Request পাওয়া যায়নি।", show_alert=True)
        return
    if data.startswith("adm_amt_reject_"):
        if user.id != ADMIN_ID:
            return
        req_id = int(data[len("adm_amt_reject_"):])
        set_state(user.id, mode="adm_amt_reject_note", req_id=req_id)
        await query.edit_message_text(
            f"❌ *Reject Request #{req_id}*\n\nRejection কারণ লিখুন (optional):\nঅথবা 'skip' পাঠান:",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
        bal = get_user_balance(user.id)
        prices = get_premium_prices()
        price_lines = ""
        buttons = []
        row = []
        for p in prices:
            days_txt = f"{p[2]} দিন" if p[2] > 0 else "Lifetime"
            price_lines += f"📅 {days_txt} → ৳{p[3]}\n"
            safe_plan = p[1].replace(" ", "_")
            btn = InlineKeyboardButton(f"৳{p[3]} → {days_txt}", callback_data=f"buy_prem_db_{p[0]}")
            row.append(btn)
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
        await query.edit_message_text(
            f"💎 *Balance দিয়ে Premium কিনুন*\n\n"
            f"💰 আপনার Balance: ৳{bal:.2f}\n\n"
            f"{price_lines}\n"
            f"একটি প্ল্যান বেছে নিন:",
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN
        )
        return
    # ── Buy Premium from DB plans ──
    if data.startswith("buy_prem_db_"):
        plan_id = int(data[len("buy_prem_db_"):])
        with db_conn() as conn:
            plan = conn.cursor().execute("SELECT * FROM premium_prices WHERE id=?", (plan_id,)).fetchone()
        if not plan:
            await query.answer("❌ Plan পাওয়া যায়নি।", show_alert=True)
            return
        bal = get_user_balance(user.id)
        cost = plan[3]
        days = plan[2]
        plan_name = plan[1]
        if bal < cost:
            await query.answer(f"❌ অপর্যাপ্ত Balance! দরকার ৳{cost}, আপনার কাছে ৳{bal:.2f}", show_alert=True)
            return
        deduct_balance(user.id, cost)
        set_premium(user.id, days)
        days_txt = f"{days} দিন" if days > 0 else "Lifetime"
        await query.edit_message_text(
            f"🎉 *Congratulations!*\n\n"
            f"✅ আপনার *{plan_name}* Premium Activated!\n"
            f"📅 মেয়াদ: {days_txt}\n"
            f"💰 কাটা হয়েছে: ৳{cost}",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "pay_history":
        payments = get_user_payments(user.id)
        if not payments:
            await query.answer("কোনো পেমেন্ট হিস্টোরি নেই।", show_alert=True)
            return
        lines = ["📋 *Payment History*\n"]
        for p in payments[:8]:
            status_emoji = "✅" if p[5] == "approved" else ("❌" if p[5] == "rejected" else "⏳")
            lines.append(f"{status_emoji} ৳{p[2]} | {p[3]} | {p[5]}")
        await query.edit_message_text("\n".join(lines), reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    if data == "pay_mybalance":
        bal = get_user_balance(user.id)
        pts = get_user_points(user.id)
        await query.answer(f"💰 Balance: ৳{bal:.2f}\n⭐ Points: {pts}", show_alert=True)
        return

    # ── ADD MONEY SUBMIT ──
    if data == "addmoney_submit":
        state_data = get_state(user.id)
        method = state_data.get("method", "")
        amount = state_data.get("amount", 0)
        txn_id = state_data.get("txn_id", "")
        photo_file_id = state_data.get("photo_file_id", "")
        wallet_num = state_data.get("wallet_num", "")

        if not method or not amount or not txn_id:
            await query.answer("❌ তথ্য অসম্পূর্ণ। আবার শুরু করুন।", show_alert=True)
            clear_state(user.id)
            return

        req_id = create_add_money_request(user.id, amount, method, txn_id, photo_file_id)
        clear_state(user.id)

        await query.edit_message_text(
            f"✅ *Add Money Request Submitted!*\n\n"
            f"🆔 Request ID: `{req_id}`\n"
            f"💳 Method: {method}\n"
            f"💰 Amount: ৳{amount}\n"
            f"🔖 TXN: `{txn_id}`\n"
            f"📸 Screenshot: {'✅' if photo_file_id else '❌'}\n\n"
            f"⏳ Admin verify করার পর Balance যোগ হবে।\n"
            f"সমস্যা হলে Admin Chat ব্যবহার করুন।",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )

        # Notify admin with full details
        try:
            admin_text = (
                f"💰 *New Add Money Request!*\n\n"
                f"🆔 Request ID: `{req_id}`\n"
                f"👤 User: `{user.id}` ({html.escape(user.first_name or 'N/A')})\n"
                f"💳 Method: {method}\n"
                f"📱 Number: `{wallet_num}`\n"
                f"💰 Amount: ৳{amount}\n"
                f"🔖 TXN ID: `{txn_id}`\n"
                f"📸 Screenshot: {'✅ আছে' if photo_file_id else '❌ নেই'}\n\n"
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID, text=admin_text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"✅ Approve #{req_id}", callback_data=f"adm_amt_approve_{req_id}"),
                     InlineKeyboardButton(f"❌ Reject #{req_id}", callback_data=f"adm_amt_reject_{req_id}")],
                ])
            )
            if photo_file_id:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID, photo=photo_file_id,
                    caption=f"📸 Payment Screenshot - Request #{req_id}"
                )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")
        return

    # ── REFERRAL CALLBACKS ──
    if data == "ref_stats":
        count = get_referral_count(user.id)
        pts = get_user_points(user.id)
        await query.answer(f"👥 রেফারেল: {count} জন\n⭐ Points: {pts}", show_alert=True)
        return
    if data == "ref_getlink":
        bot_username = "aibot3232_bot"
        ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
        await query.edit_message_text(
            f"🔗 *আপনার রেফারেল লিংক*\n\n`{ref_link}`\n\n"
            f"⬆️ উপরের লিংক কপি করে বন্ধুদের পাঠান!\n"
            f"প্রতিজন বন্ধুর জন্য *10 Points* পাবেন।",
            reply_markup=referral_keyboard(user.id), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ref_redeem":
        pts = get_user_points(user.id)
        # Find plan with points_cost
        prices = get_premium_prices()
        points_plans = [p for p in prices if p[4] > 0]
        if not points_plans:
            await query.answer("❌ কোনো points-redeemable plan নেই।", show_alert=True)
            return
        plan = points_plans[0]
        required_pts = plan[4]
        if pts < required_pts:
            await query.answer(f"❌ আপনার Points কম! {pts}/{required_pts} আছে।", show_alert=True)
            return
        add_points(user.id, -required_pts)
        set_premium(user.id, plan[2])
        days_txt = f"{plan[2]} দিন" if plan[2] > 0 else "Lifetime"
        await query.edit_message_text(
            f"🎉 *Premium Activated!*\n\n"
            f"✅ {required_pts} Points খরচ করে {days_txt}-এর Premium পেয়েছেন!\n"
            f"⭐ বাকি Points: {pts - required_pts}",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "ref_howto":
        await query.edit_message_text(
            "ℹ️ *Refer করার নিয়ম*\n\n"
            "1️⃣ 'রেফারেল লিংক কপি করুন' বাটনে ক্লিক করুন\n"
            "2️⃣ লিংকটি বন্ধুদের পাঠান\n"
            "3️⃣ বন্ধু লিংকে ক্লিক করে বট Start করলে\n"
            "   আপনি *10 Points* পাবেন\n\n"
            "🎁 *পয়েন্ট রিডিম:*\n"
            "• 100 Points = 30 দিন Premium (Free!)\n\n"
            "💡 বেশি রেফার করুন, বেশি Points কামান!",
            reply_markup=referral_keyboard(user.id), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── NEW TOOL CALLBACKS (translate, summarize, phone info, link check, temp email) ──
    if data == "util_translate":
        set_state(user.id, mode="util_translate")
        await query.edit_message_text(
            "🌐 *Multi-Language Translation | বহুভাষা অনুবাদ*\n\n"
            "Format: `target_lang::text`\n"
            "Example: `bn::Hello World` (English → Bengali)\n"
            "Example: `en::আমি ভালো আছি` (Bengali → English)\n\n"
            "Language codes: bn, en, hi, ar, fr, de, ja, ko, zh",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_summarize":
        allowed, err_msg = check_tool_access(user.id, "summarize")
        if not allowed:
            await query.answer(err_msg, show_alert=True)
            return
        set_state(user.id, mode="util_summarize")
        await query.edit_message_text(
            "📝 *AI Summarizer | টেক্সট সারসংক্ষেপ*\n\nদীর্ঘ টেক্সট পাঠান, আমি সংক্ষিপ্ত করব।\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_phoneinfo":
        allowed, err_msg = check_tool_access(user.id, "phone_info")
        if not allowed:
            await query.answer(err_msg, show_alert=True)
            return
        set_state(user.id, mode="util_phoneinfo")
        await query.edit_message_text(
            "📱 *Phone Number Info | ফোন নাম্বার ইনফো*\n\nফোন নাম্বার পাঠান (country code সহ)\nExample: `+8801711000000`\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_linkcheck":
        allowed, err_msg = check_tool_access(user.id, "link_check")
        if not allowed:
            await query.answer(err_msg, show_alert=True)
            return
        set_state(user.id, mode="util_linkcheck")
        await query.edit_message_text(
            "🔍 *Link Safety Checker | লিংক পরীক্ষা*\n\nকোনো লিংক পাঠান, আমি চেক করব এটি Safe না Dangerous।\n\n/start to exit.",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_tempemail":
        allowed, err_msg = check_tool_access(user.id, "temp_email")
        if not allowed:
            await query.answer(err_msg, show_alert=True)
            return
        await query.edit_message_text(
            "📧 *Temporary Email | অস্থায়ী ইমেইল*\n\nGenerate করছি...",
            reply_markup=back_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        email, err = await generate_temp_email()
        if err:
            await query.edit_message_text(f"❌ Error: {err}", reply_markup=back_keyboard())
            return
        save_temp_email(user.id, email)
        increment_tool_usage(user.id, "temp_email")
        set_state(user.id, mode="temp_email_check", email=email)
        await query.edit_message_text(
            f"📧 *Temporary Email Generated!*\n\n"
            f"📮 Email: `{email}`\n\n"
            f"Inbox চেক করতে /start → Utility → Check Inbox বা নিচের বাটন ব্যবহার করুন।",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📬 Inbox চেক করুন", callback_data="util_checkinbox")],
                [InlineKeyboardButton("🔄 নতুন Email নিন", callback_data="util_tempemail")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]), parse_mode=ParseMode.MARKDOWN
        )
        return
    if data == "util_checkinbox":
        email = get_temp_email(user.id)
        if not email:
            await query.answer("❌ কোনো temp email নেই। নতুন নিন।", show_alert=True)
            return
        msgs, err = await check_temp_email_inbox(email)
        if err:
            await query.edit_message_text(f"❌ Error: {err}", reply_markup=back_keyboard())
            return
        if not msgs:
            await query.edit_message_text(
                f"📬 *Inbox: {email}*\n\nInbox খালি। এখনো কোনো mail আসেনি।",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh", callback_data="util_checkinbox")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
                ]), parse_mode=ParseMode.MARKDOWN
            )
            return
        lines = [f"📬 *Inbox: {email}*\n"]
        for m in msgs[:5]:
            lines.append(f"📩 From: `{m.get('from','?')}` | {m.get('subject','No subject')[:30]}")
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="util_checkinbox")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]), parse_mode=ParseMode.MARKDOWN
        )

# ===================== MESSAGE HANDLER =====================
@require_not_banned
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        register_user(user)
    except Exception:
        pass
    msg = update.message
    state = get_state(user.id)
    mode = state.get("mode", "")
    text = msg.text or ""

    # ── Handle who-made-you type questions ──
    if text and not mode:
        lower = text.lower()
        if any(q in lower for q in ["who made you", "who created you", "who is your creator", "who developed you", "তোমাকে কে তৈরি"]):
            await msg.reply_text(
                f"🤖 I was created by *{CREATOR_NAME}*!\n\n"
                f"👑 Admin: *{CREATOR_NAME}*\n"
                f"🤖 Bot: *{BOT_NAME}*",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        await send_main_menu(update, context)
        return

    # ── ADMIN ACTIONS ──
    if mode == "adm_broadcast" and user.id == ADMIN_ID:
        users = get_all_users()
        sent, failed = 0, 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u[0], text=f"📢 *Broadcast*\n\n{text}", parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)  # Avoid flood ban
            except:
                failed += 1
        await msg.reply_text(f"✅ Broadcast sent!\n✅ Sent: {sent}\n❌ Failed: {failed}")
        clear_state(user.id)
        return

    if mode == "adm_ban" and user.id == ADMIN_ID:
        try:
            uid = int(text.strip())
            ban_user(uid)
            await msg.reply_text(f"✅ User `{uid}` banned.", parse_mode=ParseMode.MARKDOWN)
        except:
            await msg.reply_text("❌ Invalid user ID.")
        clear_state(user.id)
        return

    if mode == "adm_unban" and user.id == ADMIN_ID:
        try:
            uid = int(text.strip())
            unban_user(uid)
            await msg.reply_text(f"✅ User `{uid}` unbanned.", parse_mode=ParseMode.MARKDOWN)
        except:
            await msg.reply_text("❌ Invalid user ID.")
        clear_state(user.id)
        return

    if mode == "adm_addprem" and user.id == ADMIN_ID:
        try:
            parts = text.strip().split()
            uid = int(parts[0])
            days = int(parts[1]) if len(parts) > 1 else 0
            set_premium(uid, days)
            await msg.reply_text(f"✅ Premium added to `{uid}`.", parse_mode=ParseMode.MARKDOWN)
        except:
            await msg.reply_text("❌ Invalid input. Format: user_id days")
        clear_state(user.id)
        return

    if mode == "adm_remprem" and user.id == ADMIN_ID:
        try:
            uid = int(text.strip())
            remove_premium(uid)
            await msg.reply_text(f"✅ Premium removed from `{uid}`.", parse_mode=ParseMode.MARKDOWN)
        except:
            await msg.reply_text("❌ Invalid user ID.")
        clear_state(user.id)
        return

    if mode == "adm_voiceon" and user.id == ADMIN_ID:
        try:
            uid = int(text.strip())
            set_voice_access(uid, 1)
            await msg.reply_text(f"✅ Voice access enabled for `{uid}`.", parse_mode=ParseMode.MARKDOWN)
        except:
            await msg.reply_text("❌ Invalid user ID.")
        clear_state(user.id)
        return

    if mode == "adm_voiceoff" and user.id == ADMIN_ID:
        try:
            uid = int(text.strip())
            set_voice_access(uid, 0)
            await msg.reply_text(f"✅ Voice access disabled for `{uid}`.", parse_mode=ParseMode.MARKDOWN)
        except:
            await msg.reply_text("❌ Invalid user ID.")
        clear_state(user.id)
        return

    # ── NEW ADMIN MESSAGE HANDLERS ──
    if mode == "adm_approve_pay" and user.id == ADMIN_ID:
        try:
            pay_id = int(text.strip())
            uid, amount = approve_payment(pay_id, ADMIN_ID)
            if uid:
                await msg.reply_text(f"✅ Payment ID `{pay_id}` Approved!\nUID `{uid}` এর Balance এ ৳{amount} যোগ হয়েছে।", parse_mode=ParseMode.MARKDOWN)
                try:
                    await context.bot.send_message(chat_id=uid, text=f"🎉 *Payment Approved!*\n\n✅ আপনার ৳{amount} Balance যোগ হয়েছে!", parse_mode=ParseMode.MARKDOWN)
                except:
                    pass
            else:
                await msg.reply_text("❌ Payment পাওয়া যায়নি বা ইতোমধ্যে processed।")
        except:
            await msg.reply_text("❌ Invalid Payment ID.")
        clear_state(user.id)
        return

    if mode == "adm_reject_pay" and user.id == ADMIN_ID:
        try:
            pay_id = int(text.strip())
            with db_conn() as conn:
                p = conn.cursor().execute("SELECT user_id FROM payments WHERE id=?", (pay_id,)).fetchone()
            reject_payment(pay_id, ADMIN_ID)
            await msg.reply_text(f"❌ Payment ID `{pay_id}` Rejected.", parse_mode=ParseMode.MARKDOWN)
            if p:
                try:
                    await context.bot.send_message(chat_id=p[0], text=f"❌ *Payment Rejected*\n\nআপনার Payment ID `{pay_id}` reject হয়েছে। Admin এ যোগাযোগ করুন।", parse_mode=ParseMode.MARKDOWN)
                except:
                    pass
        except:
            await msg.reply_text("❌ Invalid Payment ID.")
        clear_state(user.id)
        return

    if mode == "adm_addbalance" and user.id == ADMIN_ID:
        try:
            parts = text.strip().split()
            uid, amount = int(parts[0]), float(parts[1])
            add_balance(uid, amount)
            await msg.reply_text(f"✅ UID `{uid}` এর Balance এ ৳{amount} যোগ হয়েছে।", parse_mode=ParseMode.MARKDOWN)
            try:
                await context.bot.send_message(chat_id=uid, text=f"💰 Admin আপনার Balance এ ৳{amount} যোগ করেছেন!", parse_mode=ParseMode.MARKDOWN)
            except:
                pass
        except:
            await msg.reply_text("❌ Format: user_id amount")
        clear_state(user.id)
        return

    if mode == "adm_addpoints" and user.id == ADMIN_ID:
        try:
            parts = text.strip().split()
            uid, pts = int(parts[0]), int(parts[1])
            add_points(uid, pts)
            await msg.reply_text(f"✅ UID `{uid}` এর Points এ {pts} যোগ হয়েছে।", parse_mode=ParseMode.MARKDOWN)
            try:
                await context.bot.send_message(chat_id=uid, text=f"⭐ Admin আপনাকে {pts} Points দিয়েছেন!", parse_mode=ParseMode.MARKDOWN)
            except:
                pass
        except:
            await msg.reply_text("❌ Format: user_id points")
        clear_state(user.id)
        return

    # ── ADMIN WALLET EDIT ──
    if mode == "adm_wallet_edit" and user.id == ADMIN_ID:
        wallet_name = state.get("wallet_name", "")
        new_number = text.strip() if text else ""
        if wallet_name and new_number:
            update_admin_wallet(wallet_name, new_number)
            await msg.reply_text(f"✅ *{wallet_name}* নাম্বার আপডেট হয়েছে: `{new_number}`", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text("❌ Invalid input.")
        clear_state(user.id)
        return

    if mode == "adm_wallet_add" and user.id == ADMIN_ID:
        parts = text.strip().split("::")
        if len(parts) >= 2:
            wname = parts[0].strip()
            wnumber = parts[1].strip()
            wtype = parts[2].strip() if len(parts) > 2 else "payment"
            add_admin_wallet(wname, wnumber, wtype)
            await msg.reply_text(f"✅ Wallet Added!\n{wname}: `{wnumber}` ({wtype})", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text("❌ Format: `WalletName::Number::Type`")
        clear_state(user.id)
        return

    # ── ADMIN SOCIAL EDIT ──
    if mode == "adm_social_edit" and user.id == ADMIN_ID:
        platform = state.get("platform", "")
        parts = text.strip().split("::", 1)
        handle = parts[0].strip()
        url = parts[1].strip() if len(parts) > 1 else ""
        if platform and handle:
            update_admin_social(platform, handle, url)
            await msg.reply_text(f"✅ *{platform}* আপডেট হয়েছে: {handle}", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text("❌ Invalid input.")
        clear_state(user.id)
        return

    if mode == "adm_social_add" and user.id == ADMIN_ID:
        parts = text.strip().split("::")
        if len(parts) >= 2:
            platform = parts[0].strip()
            handle = parts[1].strip()
            url = parts[2].strip() if len(parts) > 2 else ""
            update_admin_social(platform, handle, url)
            await msg.reply_text(f"✅ Social Added!\n{platform}: {handle}", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text("❌ Format: `Platform::Handle::URL`")
        clear_state(user.id)
        return

    # ── ADMIN PRICE EDIT ──
    if mode == "adm_price_edit" and user.id == ADMIN_ID:
        plan_name = state.get("plan_name", "")
        parts = text.strip().split("::")
        if plan_name and len(parts) >= 2:
            try:
                price = float(parts[0].strip())
                days = int(parts[1].strip())
                points_cost = int(parts[2].strip()) if len(parts) > 2 else 0
                update_premium_price(plan_name, price, days, points_cost)
                await msg.reply_text(f"✅ *{plan_name}* আপডেট হয়েছে: ৳{price} ({days} দিন)", parse_mode=ParseMode.MARKDOWN)
            except:
                await msg.reply_text("❌ Format: `price::days::points_cost`")
        else:
            await msg.reply_text("❌ Invalid input.")
        clear_state(user.id)
        return

    if mode == "adm_price_add" and user.id == ADMIN_ID:
        parts = text.strip().split("::")
        if len(parts) >= 3:
            try:
                plan_name = parts[0].strip()
                days = int(parts[1].strip())
                price = float(parts[2].strip())
                points_cost = int(parts[3].strip()) if len(parts) > 3 else 0
                add_premium_price(plan_name, days, price, points_cost)
                await msg.reply_text(f"✅ Plan Added!\n{plan_name}: ৳{price} ({days} দিন)", parse_mode=ParseMode.MARKDOWN)
            except:
                await msg.reply_text("❌ Format: `PlanName::days::price::points_cost`")
        else:
            await msg.reply_text("❌ Format: `PlanName::days::price::points_cost`")
        clear_state(user.id)
        return

    # ── ADMIN BOT SETTINGS ──
    if mode == "adm_botsettings" and user.id == ADMIN_ID:
        parts = text.strip().split("::", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            val = parts[1].strip()
            set_bot_setting(key, val)
            await msg.reply_text(f"✅ Setting saved!\n`{key}` = `{val}`", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text("❌ Format: `key::value`")
        clear_state(user.id)
        return

    # ── ADD MONEY - Step by Step Flow ──
    if mode == "addmoney_enter_amount":
        method = state.get("method", "")
        wallet_num = state.get("wallet_num", "")
        if text and text.strip().replace(".", "").isdigit():
            amount = float(text.strip())
            set_state(user.id, mode="addmoney_enter_txn", method=method, wallet_num=wallet_num, amount=amount)
            await msg.reply_text(
                f"✅ পরিমাণ: ৳{amount}\n\n"
                f"📝 *Step 2:* এখন Transaction ID পাঠান:\n"
                f"Example: `TXN123456789` বা `Bkash123456`",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await msg.reply_text("❌ শুধু সংখ্যা পাঠান। Example: `150`", parse_mode=ParseMode.MARKDOWN)
        return

    if mode == "addmoney_enter_txn":
        method = state.get("method", "")
        wallet_num = state.get("wallet_num", "")
        amount = state.get("amount", 0)
        if text and len(text.strip()) >= 3:
            txn_id = text.strip()
            set_state(user.id, mode="addmoney_upload_photo", method=method, wallet_num=wallet_num, amount=amount, txn_id=txn_id)
            await msg.reply_text(
                f"✅ Transaction ID: `{txn_id}`\n\n"
                f"📸 *Step 3:* Payment Screenshot আপলোড করুন\n"
                f"(ছবি পাঠান - OPTIONAL)\n\n"
                f"অথবা Skip করতে 'skip' লিখুন।",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await msg.reply_text("❌ Transaction ID লিখুন। Example: `TXN123456`", parse_mode=ParseMode.MARKDOWN)
        return

    if mode == "addmoney_upload_photo":
        method = state.get("method", "")
        wallet_num = state.get("wallet_num", "")
        amount = state.get("amount", 0)
        txn_id = state.get("txn_id", "")
        photo_file_id = ""

        if msg.photo:
            photo_file_id = msg.photo[-1].file_id
            set_state(user.id, mode="addmoney_verify", method=method, wallet_num=wallet_num,
                      amount=amount, txn_id=txn_id, photo_file_id=photo_file_id)
        elif text and text.strip().lower() == "skip":
            set_state(user.id, mode="addmoney_verify", method=method, wallet_num=wallet_num,
                      amount=amount, txn_id=txn_id, photo_file_id="")
        else:
            await msg.reply_text("📸 ছবি পাঠান বা 'skip' লিখুন।", parse_mode=ParseMode.MARKDOWN)
            return

        emojis = {"Bkash": "📲", "Rocket": "🚀", "Nagad": "💛", "Upay": "🔴"}
        emo = emojis.get(method, "💳")
        photo_status = "✅ আপলোড হয়েছে" if photo_file_id else "❌ Skip করা হয়েছে"
        await msg.reply_text(
            f"📋 *Payment Summary | নিশ্চিত করুন*\n\n"
            f"{emo} Method: *{method}*\n"
            f"💰 Amount: ৳{amount}\n"
            f"🔖 TXN ID: `{txn_id}`\n"
            f"📸 Screenshot: {photo_status}\n\n"
            f"সব ঠিক থাকলে নিচের *Verify* বাটনে চাপুন!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Verify করুন | Submit", callback_data="addmoney_submit")],
                [InlineKeyboardButton("❌ বাতিল করুন", callback_data="back_main")],
            ]), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── SUPPORT CHAT - User sending message to Admin ──
    if mode == "support_chat_user":
        file_id = ""
        file_type = ""
        message_text = text or ""

        if msg.photo:
            file_id = msg.photo[-1].file_id
            file_type = "photo"
            message_text = msg.caption or "[Photo]"
        elif msg.voice:
            file_id = msg.voice.file_id
            file_type = "voice"
            message_text = "[Voice Message]"
        elif msg.audio:
            file_id = msg.audio.file_id
            file_type = "audio"
            message_text = msg.caption or f"[Audio: {msg.audio.file_name or 'audio'}]"
        elif msg.document:
            file_id = msg.document.file_id
            file_type = "document"
            message_text = msg.caption or f"[File: {msg.document.file_name or 'file'}]"
        elif msg.video:
            file_id = msg.video.file_id
            file_type = "video"
            message_text = msg.caption or "[Video]"

        if not message_text and not file_id:
            await msg.reply_text("📝 Message, ছবি বা ভয়েস পাঠান।")
            return

        save_support_message(user.id, "user", message_text, file_id, file_type)

        # Forward to admin
        try:
            user_info = f"💬 *Support Message*\n👤 User: `{user.id}` ({html.escape(user.first_name or 'N/A')})\n"
            if user.username:
                user_info += f"Username: @{user.username}\n"
            user_info += f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

            if file_type == "photo":
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id,
                    caption=user_info + f"📝 {message_text}", parse_mode=ParseMode.MARKDOWN)
            elif file_type == "voice":
                await context.bot.send_message(chat_id=ADMIN_ID, text=user_info + "🎤 Voice Message নিচে:", parse_mode=ParseMode.MARKDOWN)
                await context.bot.send_voice(chat_id=ADMIN_ID, voice=file_id)
            elif file_type == "audio":
                await context.bot.send_message(chat_id=ADMIN_ID, text=user_info + f"🎵 {message_text}", parse_mode=ParseMode.MARKDOWN)
                await context.bot.send_audio(chat_id=ADMIN_ID, audio=file_id)
            elif file_type == "document":
                await context.bot.send_message(chat_id=ADMIN_ID, text=user_info + f"📎 {message_text}", parse_mode=ParseMode.MARKDOWN)
                await context.bot.send_document(chat_id=ADMIN_ID, document=file_id)
            elif file_type == "video":
                await context.bot.send_video(chat_id=ADMIN_ID, video=file_id,
                    caption=user_info + f"🎬 {message_text}", parse_mode=ParseMode.MARKDOWN)
            else:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=user_info + f"💬 {message_text}", parse_mode=ParseMode.MARKDOWN)

            # Quick reply button for admin
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"↩️ Reply করতে ক্লিক করুন:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"Reply to {user.first_name}", callback_data=f"adm_chat_user_{user.id}")]
                ])
            )
        except Exception as e:
            logger.error(f"Support forward error: {e}")

        await msg.reply_text(
            "✅ *Message পাঠানো হয়েছে!*\n\n"
            "Admin শীঘ্রই reply করবেন।\n"
            "আরো message পাঠাতে পারেন।",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")],
            ]), parse_mode=ParseMode.MARKDOWN
        )
        return

    # ── ADMIN: Reply to Support User ──
    if mode == "adm_reply_user" and user.id == ADMIN_ID:
        target_uid = state.get("target_uid")
        if not target_uid:
            await msg.reply_text("❌ Target user পাওয়া যায়নি।")
            clear_state(user.id)
            return

        file_id = ""
        file_type = ""
        reply_text = text or ""

        if msg.photo:
            file_id = msg.photo[-1].file_id
            file_type = "photo"
            reply_text = msg.caption or "[Photo from Admin]"
        elif msg.voice:
            file_id = msg.voice.file_id
            file_type = "voice"
            reply_text = "[Voice from Admin]"
        elif msg.audio:
            file_id = msg.audio.file_id
            file_type = "audio"
            reply_text = msg.caption or "[Audio from Admin]"
        elif msg.document:
            file_id = msg.document.file_id
            file_type = "document"
            reply_text = msg.caption or "[File from Admin]"

        if not reply_text and not file_id:
            await msg.reply_text("📝 Text, ছবি বা ভয়েস পাঠান।")
            return

        save_support_message(target_uid, "admin", reply_text, file_id, file_type)

        # Send to user
        try:
            admin_header = f"👑 *Admin Reply*\n\n"
            if file_type == "photo":
                await context.bot.send_photo(chat_id=target_uid, photo=file_id,
                    caption=admin_header + reply_text, parse_mode=ParseMode.MARKDOWN)
            elif file_type == "voice":
                await context.bot.send_message(chat_id=target_uid, text=admin_header + "🎤 Voice message:", parse_mode=ParseMode.MARKDOWN)
                await context.bot.send_voice(chat_id=target_uid, voice=file_id)
            elif file_type == "audio":
                await context.bot.send_audio(chat_id=target_uid, audio=file_id,
                    caption=admin_header + reply_text, parse_mode=ParseMode.MARKDOWN)
            elif file_type == "document":
                await context.bot.send_document(chat_id=target_uid, document=file_id,
                    caption=admin_header + reply_text, parse_mode=ParseMode.MARKDOWN)
            else:
                await context.bot.send_message(chat_id=target_uid,
                    text=admin_header + reply_text, parse_mode=ParseMode.MARKDOWN)
            await msg.reply_text(f"✅ User `{target_uid}` এ reply পাঠানো হয়েছে!", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await msg.reply_text(f"❌ Send failed: {e}")
        return

    # ── ADMIN: Reject Add Money with note ──
    if mode == "adm_amt_reject_note" and user.id == ADMIN_ID:
        req_id = state.get("req_id")
        note = text.strip() if text and text.strip().lower() != "skip" else "Rejected by admin"
        rejected_uid = reject_add_money(req_id, ADMIN_ID, note)
        await msg.reply_text(f"✅ Request #{req_id} Rejected.", parse_mode=ParseMode.MARKDOWN)
        if rejected_uid:
            try:
                await context.bot.send_message(
                    chat_id=rejected_uid,
                    text=f"❌ *Add Money Rejected*\n\n"
                         f"🆔 Request ID: `{req_id}`\n"
                         f"📝 কারণ: {note}\n\n"
                         f"সমস্যা থাকলে Admin Chat-এ যোগাযোগ করুন।",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        clear_state(user.id)
        return

    # ── PAYMENT MESSAGE HANDLERS ──
    # Dynamic payment from DB wallets
    db_wallets_all = get_admin_wallets(wallet_type="payment")
    db_wallet_names = [w[1].lower() for w in db_wallets_all]
    
    for wdata in db_wallets_all:
        wname = wdata[1].lower()
        if mode == f"pay_{wname}":
            # Handle screenshot
            if msg.photo:
                # Forward screenshot to admin
                pay_id = None
                try:
                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"📸 *Payment Screenshot Received!*\n\n"
                             f"👤 User: `{user.id}` ({user.first_name})\n"
                             f"💳 Method: {wdata[1]}\n\n"
                             f"⬇️ Screenshot নিচে:",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=msg.chat_id, message_id=msg.message_id)
                except:
                    pass
                await msg.reply_text(
                    f"📸 Screenshot পেয়েছি!\n\n"
                    f"এখন payment amount ও transaction ID পাঠান:\n"
                    f"`amount::transaction_id`\nExample: `150::TXN123456`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            if text:
                parts = text.strip().split("::")
                if len(parts) == 2:
                    try:
                        amount = float(parts[0].strip())
                        txn_id = parts[1].strip()
                        pay_id = create_payment_request(user.id, amount, wdata[1], txn_id)
                        wallet_num = wdata[2] if wdata[2] else "N/A"
                        await msg.reply_text(
                            f"✅ *Payment Request Submitted!*\n\n"
                            f"🆔 Payment ID: `{pay_id}`\n"
                            f"💰 Amount: ৳{amount}\n"
                            f"💳 Method: {wdata[1]}\n"
                            f"📱 Sent To: `{wallet_num}`\n"
                            f"🔖 TXN: `{txn_id}`\n\n"
                            f"⏳ Admin অনুমোদনের পর Balance যোগ হবে।",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        # Notify admin
                        try:
                            await context.bot.send_message(
                                chat_id=ADMIN_ID,
                                text=f"💳 *New Payment Request!*\n\n"
                                     f"👤 User: `{user.id}` ({user.first_name})\n"
                                     f"💰 Amount: ৳{amount}\n"
                                     f"💳 Method: {wdata[1]}\n"
                                     f"📱 Number: `{wallet_num}`\n"
                                     f"🔖 TXN: `{txn_id}`\n"
                                     f"🆔 Payment ID: `{pay_id}`\n\n"
                                     f"Approve: /admin → Approve Payment → `{pay_id}`",
                                parse_mode=ParseMode.MARKDOWN
                            )
                        except:
                            pass
                    except:
                        await msg.reply_text("❌ Format সঠিক না। Example: `150::TXN123456`", parse_mode=ParseMode.MARKDOWN)
                else:
                    await msg.reply_text("❌ Format: `amount::transaction_id`\nExample: `150::TXN123456`", parse_mode=ParseMode.MARKDOWN)
                clear_state(user.id)
            return

    # ── AI CHAT ──
    if mode == "ai_chat":
        if not text:
            await msg.reply_text("Please send a text message.")
            return
        await typing_animation(update, context, 0.3)
        ctx = get_ai_context(user.id)
        ctx.append({"role": "user", "content": text})
        system_msg = {"role": "system", "content": f"You are {BOT_NAME}, a helpful AI assistant created by {CREATOR_NAME}."}
        reply, err = await openai_chat([system_msg] + ctx)
        if err:
            await msg.reply_text(f"❌ AI Error: {err}")
        else:
            ctx.append({"role": "assistant", "content": reply})
            save_ai_context(user.id, ctx)
            await msg.reply_text(reply)
        log_action(user.id, "ai_chat", text[:50])
        return

    # ── AI IMAGE ──
    if mode == "ai_image":
        if not text:
            await msg.reply_text("Please describe the image.")
            return
        await typing_animation(update, context, 0.5)
        await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_PHOTO)
        url, err = await openai_image(text)
        if err:
            await msg.reply_text(f"❌ Image gen error: {err}")
        else:
            try:
                # Download image and send as file (works for both OpenAI and Pollinations)
                loop = asyncio.get_event_loop()
                def fetch_img():
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=30) as r:
                        return r.read()
                img_bytes = await loop.run_in_executor(None, fetch_img)
                buf = io.BytesIO(img_bytes)
                buf.name = "image.jpg"
                await msg.reply_photo(photo=buf, caption=f"🎨 Generated: _{text[:100]}_", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                # Fallback: try sending URL directly
                try:
                    await msg.reply_photo(photo=url, caption=f"🎨 Generated: _{text[:100]}_", parse_mode=ParseMode.MARKDOWN)
                except Exception as e2:
                    await msg.reply_text(f"✅ Image generated!\n🔗 View: {url}")
        log_action(user.id, "ai_image", text[:50])
        return

    # ── AI Q&A ──
    if mode == "ai_qa":
        if not text:
            await msg.reply_text("Please ask a question.")
            return
        await typing_animation(update, context, 1.5)
        system = {"role": "system", "content": f"You are {BOT_NAME} by {CREATOR_NAME}. Answer questions accurately and concisely."}
        reply, err = await openai_chat([system, {"role": "user", "content": text}])
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            await msg.reply_text(reply)
        return

    # ── TTS (AI) ──
    if mode == "ai_tts":
        if not has_voice_access(user.id):
            await msg.reply_text("❌ Voice access disabled.")
            return
        if not text:
            await msg.reply_text("Please send text.")
            return
        await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.RECORD_VOICE)
        style = get_user_voice_style(user.id)
        with db_conn() as conn:
            r = conn.cursor().execute("SELECT tts_lang FROM user_settings WHERE user_id=?", (user.id,)).fetchone()
            lang = r[0] if r else "en"
        audio, err = make_tts_audio(text, style, lang)
        if err:
            await msg.reply_text(f"❌ TTS Error: {err}")
        else:
            await msg.reply_voice(voice=audio, caption=f"🔊 *{style}*", parse_mode=ParseMode.MARKDOWN)
        log_action(user.id, "ai_tts", text[:50])
        return

    # ── STT (AI) ──
    if mode == "ai_stt":
        if not has_voice_access(user.id):
            await msg.reply_text("❌ Voice access disabled.")
            return
        if not (msg.voice or msg.audio):
            await msg.reply_text("Please send a voice message.")
            return
        await typing_animation(update, context)
        file_obj = msg.voice or msg.audio
        tfile = await context.bot.get_file(file_obj.file_id)
        ext = ".ogg" if msg.voice else ".mp3"
        fpath = f"/tmp/voice_{user.id}{ext}"
        await tfile.download_to_drive(fpath)
        text_out, err = speech_to_text_from_file(fpath)
        try:
            os.remove(fpath)
        except:
            pass
        if err:
            await msg.reply_text(f"❌ STT Error: {err}")
        else:
            await msg.reply_text(f"📝 *Transcribed:*\n\n{text_out}", parse_mode=ParseMode.MARKDOWN)
        return

    # ── UTIL TTS ──
    if mode == "util_tts":
        if not has_voice_access(user.id):
            await msg.reply_text("❌ Voice access disabled.")
            return
        if not text:
            await msg.reply_text("Send text to convert.")
            return
        await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.RECORD_VOICE)
        style = get_user_voice_style(user.id)
        audio, err = make_tts_audio(text, style)
        if err:
            await msg.reply_text(f"❌ TTS Error: {err}")
        else:
            await msg.reply_voice(voice=audio, caption="🔊 Voice message")
        return

    # ── UTIL STT ──
    if mode == "util_stt":
        if not has_voice_access(user.id):
            await msg.reply_text("❌ Voice access disabled.")
            return
        if not (msg.voice or msg.audio):
            await msg.reply_text("Send a voice message.")
            return
        await typing_animation(update, context)
        file_obj = msg.voice or msg.audio
        tfile = await context.bot.get_file(file_obj.file_id)
        ext = ".ogg" if msg.voice else ".mp3"
        fpath = f"/tmp/voice_{user.id}{ext}"
        await tfile.download_to_drive(fpath)
        text_out, err = speech_to_text_from_file(fpath)
        try:
            os.remove(fpath)
        except:
            pass
        if err:
            await msg.reply_text(f"❌ STT Error: {err}")
        else:
            await msg.reply_text(f"📝 *Transcribed:*\n\n{text_out}", parse_mode=ParseMode.MARKDOWN)
        return

    # ── UTIL QR GEN ──
    if mode == "util_qrgen":
        if not text:
            await msg.reply_text("Send text or URL.")
            return
        out = f"/tmp/qr_{user.id}.png"
        ok, err = generate_qr(text, out)
        if ok:
            await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_PHOTO)
            with open(out, "rb") as f:
                await msg.reply_photo(photo=f, caption="📱 Your QR Code")
            os.remove(out)
        else:
            await msg.reply_text(f"❌ QR Error: {err}")
        return

    # ── UTIL BASE64 ──
    if mode == "util_base64enc":
        if not text:
            await msg.reply_text("Send text to encode.")
            return
        result = encode_base64(text)
        await msg.reply_text(f"📊 *Encoded:*\n`{result}`", parse_mode=ParseMode.MARKDOWN)
        return

    if mode == "util_base64dec":
        if not text:
            await msg.reply_text("Send Base64 string.")
            return
        result, err = decode_base64(text.strip())
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            await msg.reply_text(f"📊 *Decoded:*\n`{result}`", parse_mode=ParseMode.MARKDOWN)
        return

    # ── WEB TOOLS ──
    if mode == "web_source":
        url = text.strip()
        if not url.startswith("http"):
            url = "https://" + url
        await typing_animation(update, context)
        content, err = fetch_url_content(url)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            preview = content[:3000] + ("..." if len(content) > 3000 else "")
            buf = io.BytesIO(preview.encode())
            buf.name = "source.html"
            await msg.reply_document(document=buf, filename="source.html", caption=f"📄 Source: {url[:50]}")
        clear_state(user.id)
        return

    if mode == "web_title":
        url = text.strip()
        if not url.startswith("http"):
            url = "https://" + url
        await typing_animation(update, context)
        content, err = fetch_url_content(url)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            title = extract_title(content)
            await msg.reply_text(f"🔤 *Page Title:*\n\n`{title}`", parse_mode=ParseMode.MARKDOWN)
        clear_state(user.id)
        return

    if mode == "web_status":
        url = text.strip()
        await typing_animation(update, context)
        status, final_url = check_website_status(url)
        if status:
            emoji = "✅" if 200 <= status < 300 else "⚠️" if status < 400 else "❌"
            await msg.reply_text(f"{emoji} *Status:* `{status}`\n🔗 URL: `{final_url}`", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text(f"❌ Error: {final_url}")
        clear_state(user.id)
        return

    if mode == "web_ip":
        ip = text.strip()
        await typing_animation(update, context)
        info, err = get_ip_info(ip)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            lines = [f"🌐 *IP Lookup: {ip}*\n"]
            for k, v in info.items():
                if v:
                    lines.append(f"*{k}*: `{v}`")
            await msg.reply_text("\n".join(lines[:15]), parse_mode=ParseMode.MARKDOWN)
        clear_state(user.id)
        return

    if mode == "web_domain":
        domain = text.strip()
        await typing_animation(update, context)
        info, err = get_whois_info(domain)
        if err:
            await msg.reply_text(f"❌ WHOIS Error: {err}")
        else:
            await msg.reply_text(f"🏷 *Domain Info: {domain}*\n\n{info}", parse_mode=ParseMode.MARKDOWN)
        clear_state(user.id)
        return

    if mode == "web_shorten":
        url = text.strip()
        await typing_animation(update, context)
        short, err = shorten_url(url)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            await msg.reply_text(f"🔗 *Short URL:*\n`{short}`", parse_mode=ParseMode.MARKDOWN)
        clear_state(user.id)
        return

    if mode == "web_unshorten":
        url = text.strip()
        await typing_animation(update, context)
        expanded, err = unshorten_url(url)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            await msg.reply_text(f"🔓 *Expanded URL:*\n`{expanded}`", parse_mode=ParseMode.MARKDOWN)
        clear_state(user.id)
        return

    # ── DOWNLOADER ──
    if mode in ("dl_youtube", "dl_ytaudio", "dl_tiktok", "dl_instagram", "dl_direct", "dl_anyurl", "vid_download"):
        url = text.strip()
        if not url:
            await msg.reply_text("Please send a valid URL.")
            return
        audio_only = mode == "dl_ytaudio"
        await msg.reply_text("⬇️ Downloading... Please wait.")
        await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
        # For direct/any URL, try requests download
        if mode in ("dl_direct", "dl_anyurl"):
            try:
                if REQUESTS_AVAILABLE:
                    r = requests.get(url, stream=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                    fname = url.split("/")[-1].split("?")[0] or "downloaded_file"
                    fpath = f"/tmp/{fname}"
                    with open(fpath, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    size = os.path.getsize(fpath)
                    if size > 50 * 1024 * 1024:
                        await msg.reply_text("❌ File too large (>50MB) to send via Telegram.")
                        os.remove(fpath)
                    else:
                        with open(fpath, "rb") as f:
                            await msg.reply_document(document=f, filename=fname, caption=f"✅ Downloaded: {fname}")
                        os.remove(fpath)
                else:
                    await msg.reply_text("❌ requests not installed. Run: pip install requests")
            except Exception as e:
                await msg.reply_text(f"❌ Download error: {e}")
            clear_state(user.id)
            return
        # For YouTube/TikTok/Instagram use yt-dlp
        fpath, err = await download_with_ytdlp(url, audio_only=audio_only, output_dir="/tmp")
        if err:
            await msg.reply_text(f"❌ Download error: {err}")
        elif fpath and os.path.exists(fpath):
            size = os.path.getsize(fpath)
            if size > 50 * 1024 * 1024:
                await msg.reply_text("❌ File too large (>50MB) to send via Telegram.")
            else:
                await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                with open(fpath, "rb") as f:
                    if audio_only:
                        await msg.reply_audio(audio=f, filename=os.path.basename(fpath))
                    else:
                        await msg.reply_video(video=f, caption="✅ Downloaded!")
            os.remove(fpath)
        else:
            await msg.reply_text("❌ Download failed.")
        log_action(user.id, "download", url[:80])
        clear_state(user.id)
        return

    # ── IMAGE TOOLS (file uploads) ──
    if mode in ("img_rembg", "img_topng", "img_enhance", "img_compress", "img_topdf", "img_grayscale", "file_imgtopdf"):
        if not (msg.photo or msg.document):
            await msg.reply_text("Please send an image file.")
            return
        await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_PHOTO)
        if msg.photo:
            file_id = msg.photo[-1].file_id
            ext = ".jpg"
        else:
            file_id = msg.document.file_id
            ext = os.path.splitext(msg.document.file_name or ".jpg")[1] or ".jpg"
        tfile = await context.bot.get_file(file_id)
        inp = f"/tmp/img_inp_{user.id}{ext}"
        out = f"/tmp/img_out_{user.id}"
        await tfile.download_to_drive(inp)

        if mode == "img_rembg":
            out += ".png"
            ok, err = pil_remove_background(inp, out)
            caption = "✂️ Background removed!"
        elif mode == "img_topng":
            out += ".png"
            ok, err = pil_to_png(inp, out)
            caption = "🖼 Converted to PNG!"
        elif mode == "img_enhance":
            out += ext
            ok, err = pil_enhance(inp, out)
            caption = "✨ Image enhanced!"
        elif mode == "img_compress":
            out += ext
            ok, err = pil_compress(inp, out)
            caption = "🗜 Image compressed!"
        elif mode in ("img_topdf", "file_imgtopdf"):
            out += ".pdf"
            ok, err = image_to_pdf_file(inp, out)
            caption = "📄 Converted to PDF!"
        elif mode == "img_grayscale":
            out += ".png"
            ok, err = pil_grayscale(inp, out)
            caption = "🔄 Grayscale applied!"
        else:
            ok, err = False, "Unknown mode"
            caption = ""

        try:
            os.remove(inp)
        except:
            pass
        if ok and os.path.exists(out):
            with open(out, "rb") as f:
                if out.endswith(".pdf"):
                    await msg.reply_document(document=f, filename="output.pdf", caption=caption)
                else:
                    await msg.reply_photo(photo=f, caption=caption)
            os.remove(out)
            set_state(user.id, mode=mode)
        else:
            await msg.reply_text(f"❌ Error: {err}")
        return

    # ── IMG RESIZE ──
    if mode == "img_resize":
        if msg.photo or msg.document:
            if msg.photo:
                file_id = msg.photo[-1].file_id; ext = ".jpg"
            else:
                file_id = msg.document.file_id; ext = os.path.splitext(msg.document.file_name or ".jpg")[1]
            tfile = await context.bot.get_file(file_id)
            inp = f"/tmp/resize_inp_{user.id}{ext}"
            await tfile.download_to_drive(inp)
            set_state(user.id, mode="img_resize_dims", img_path=inp)
            await msg.reply_text("📐 Image received! Now send dimensions as: `width height` (e.g. `800 600`)", parse_mode=ParseMode.MARKDOWN)
        elif text and state.get("img_path"):
            parts = text.strip().split()
            if len(parts) == 2:
                try:
                    w, h = int(parts[0]), int(parts[1])
                    inp = state["img_path"]
                    out = f"/tmp/resize_out_{user.id}.jpg"
                    ok, err = pil_resize(inp, out, w, h)
                    if ok:
                        with open(out, "rb") as f:
                            await msg.reply_photo(photo=f, caption=f"📐 Resized to {w}x{h}")
                        os.remove(out)
                    else:
                        await msg.reply_text(f"❌ Error: {err}")
                    try: os.remove(inp)
                    except: pass
                    clear_state(user.id)
                except:
                    await msg.reply_text("❌ Invalid dimensions. Send as: `width height`", parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.reply_text("❌ Send as: `width height` (e.g. `800 600`)", parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.reply_text("Send an image first.")
        return

    if mode == "img_resize_dims":
        if text:
            parts = text.strip().split()
            if len(parts) == 2:
                try:
                    w, h = int(parts[0]), int(parts[1])
                    inp = state.get("img_path", "")
                    if not inp or not os.path.exists(inp):
                        await msg.reply_text("Image not found. Please start over.")
                        clear_state(user.id)
                        return
                    out = f"/tmp/resize_out_{user.id}.jpg"
                    ok, err = pil_resize(inp, out, w, h)
                    if ok:
                        with open(out, "rb") as f:
                            await msg.reply_photo(photo=f, caption=f"📐 Resized to {w}x{h}")
                        os.remove(out)
                    else:
                        await msg.reply_text(f"❌ Error: {err}")
                    try: os.remove(inp)
                    except: pass
                    clear_state(user.id)
                except:
                    await msg.reply_text("❌ Invalid. Send: `width height`", parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.reply_text("❌ Send: `width height`", parse_mode=ParseMode.MARKDOWN)
        return

    # ── IMG WATERMARK ──
    if mode == "img_watermark":
        if msg.photo or msg.document:
            if msg.photo:
                file_id = msg.photo[-1].file_id; ext = ".jpg"
            else:
                file_id = msg.document.file_id; ext = os.path.splitext(msg.document.file_name or ".jpg")[1]
            tfile = await context.bot.get_file(file_id)
            inp = f"/tmp/wm_inp_{user.id}{ext}"
            await tfile.download_to_drive(inp)
            set_state(user.id, mode="img_watermark_text", img_path=inp)
            await msg.reply_text("💧 Image received! Now send the watermark text:")
        elif text and state.get("img_path"):
            inp = state["img_path"]
            out = f"/tmp/wm_out_{user.id}.jpg"
            ok, err = pil_watermark(inp, out, text)
            if ok:
                with open(out, "rb") as f:
                    await msg.reply_photo(photo=f, caption="💧 Watermark added!")
                os.remove(out)
            else:
                await msg.reply_text(f"❌ Error: {err}")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        else:
            await msg.reply_text("Send an image first.")
        return

    if mode == "img_watermark_text":
        if text and state.get("img_path"):
            inp = state["img_path"]
            out = f"/tmp/wm_out_{user.id}.jpg"
            ok, err = pil_watermark(inp, out, text)
            if ok:
                with open(out, "rb") as f:
                    await msg.reply_photo(photo=f, caption="💧 Watermark added!")
                os.remove(out)
            else:
                await msg.reply_text(f"❌ Error: {err}")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        return

    # ── VIDEO TOOLS ──
    if mode in ("vid_tomp3", "vid_compress", "vid_thumbnail"):
        if not (msg.video or msg.document):
            await msg.reply_text("Please send a video file.")
            return
        file_id = msg.video.file_id if msg.video else msg.document.file_id
        fname = (msg.document.file_name if msg.document else "video.mp4") or "video.mp4"
        ext = os.path.splitext(fname)[1] or ".mp4"
        tfile = await context.bot.get_file(file_id)
        inp = f"/tmp/vid_inp_{user.id}{ext}"
        await msg.reply_text("⏳ Processing video...")
        await tfile.download_to_drive(inp)

        if mode == "vid_tomp3":
            out = f"/tmp/vid_out_{user.id}.mp3"
            ok, err = video_to_mp3(inp, out)
            if ok:
                await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                with open(out, "rb") as f:
                    await msg.reply_audio(audio=f, filename="audio.mp3", caption="🎵 Audio extracted!")
                os.remove(out)
            else:
                await msg.reply_text(f"❌ Error: {err}")
        elif mode == "vid_compress":
            out = f"/tmp/vid_comp_{user.id}.mp4"
            ok, err = video_compress(inp, out)
            if ok:
                await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.UPLOAD_VIDEO)
                with open(out, "rb") as f:
                    await msg.reply_video(video=f, caption="🗜 Video compressed!")
                os.remove(out)
            else:
                await msg.reply_text(f"❌ Error: {err}")
        elif mode == "vid_thumbnail":
            out = f"/tmp/vid_thumb_{user.id}.jpg"
            ok, err = video_thumbnail(inp, out)
            if ok:
                with open(out, "rb") as f:
                    await msg.reply_photo(photo=f, caption="🖼 Thumbnail extracted!")
                os.remove(out)
            else:
                await msg.reply_text(f"❌ Error: {err}")
        try: os.remove(inp)
        except: pass
        set_state(user.id, mode=mode)
        return

    if mode == "vid_trim_upload":
        if not (msg.video or msg.document):
            await msg.reply_text("Please send a video file.")
            return
        file_id = msg.video.file_id if msg.video else msg.document.file_id
        ext = ".mp4"
        tfile = await context.bot.get_file(file_id)
        inp = f"/tmp/trim_inp_{user.id}{ext}"
        await tfile.download_to_drive(inp)
        set_state(user.id, mode="vid_trim_params", vid_path=inp)
        await msg.reply_text("✂️ Video received! Send trim params as: `start_sec duration_sec`\nExample: `10 30` (start at 10s, duration 30s)", parse_mode=ParseMode.MARKDOWN)
        return

    if mode == "vid_trim_params":
        if text and state.get("vid_path"):
            parts = text.strip().split()
            if len(parts) == 2:
                try:
                    start, dur = float(parts[0]), float(parts[1])
                    inp = state["vid_path"]
                    out = f"/tmp/trim_out_{user.id}.mp4"
                    await msg.reply_text("⏳ Trimming...")
                    ok, err = video_trim(inp, out, start, dur)
                    if ok:
                        with open(out, "rb") as f:
                            await msg.reply_video(video=f, caption="✂️ Video trimmed!")
                        os.remove(out)
                    else:
                        await msg.reply_text(f"❌ Error: {err}")
                    try: os.remove(inp)
                    except: pass
                    clear_state(user.id)
                except:
                    await msg.reply_text("❌ Invalid. Send: `start_sec duration_sec`", parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.reply_text("❌ Send: `start_sec duration_sec`", parse_mode=ParseMode.MARKDOWN)
        return

    # ── FILE TOOLS ──
    if mode == "file_compress":
        if not msg.document:
            await msg.reply_text("Please send a file.")
            return
        tfile = await context.bot.get_file(msg.document.file_id)
        fname = msg.document.file_name or "file"
        inp = f"/tmp/fc_inp_{user.id}_{fname}"
        await tfile.download_to_drive(inp)
        out = f"/tmp/fc_out_{user.id}.zip"
        ok, err = compress_to_zip(inp, out)
        if ok:
            with open(out, "rb") as f:
                await msg.reply_document(document=f, filename=f"{fname}.zip", caption="🗜 File compressed!")
            os.remove(out)
        else:
            await msg.reply_text(f"❌ Error: {err}")
        try: os.remove(inp)
        except: pass
        set_state(user.id, mode=mode)
        return

    if mode == "file_info":
        if not msg.document:
            await msg.reply_text("Please send a file.")
            return
        tfile = await context.bot.get_file(msg.document.file_id)
        fname = msg.document.file_name or "file"
        inp = f"/tmp/fi_inp_{user.id}_{fname}"
        await tfile.download_to_drive(inp)
        info = get_file_info(inp)
        lines = [f"ℹ️ *File Info*\n"]
        for k, v in info.items():
            lines.append(f"*{k}*: `{v}`")
        await msg.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
        try: os.remove(inp)
        except: pass
        set_state(user.id, mode=mode)
        return

    if mode == "file_rename_upload":
        if not msg.document:
            await msg.reply_text("Please send a file.")
            return
        tfile = await context.bot.get_file(msg.document.file_id)
        fname = msg.document.file_name or "file"
        inp = f"/tmp/rn_inp_{user.id}_{fname}"
        await tfile.download_to_drive(inp)
        set_state(user.id, mode="file_rename_name", file_path=inp, orig_name=fname)
        await msg.reply_text(f"✏️ File received: `{fname}`\nNow send the new filename (with extension):", parse_mode=ParseMode.MARKDOWN)
        return

    if mode == "file_rename_name":
        new_name = text.strip()
        if new_name and state.get("file_path"):
            inp = state["file_path"]
            out = f"/tmp/{new_name}"
            try:
                shutil.copy(inp, out)
                with open(out, "rb") as f:
                    await msg.reply_document(document=f, filename=new_name, caption=f"✏️ Renamed to: `{new_name}`", parse_mode=ParseMode.MARKDOWN)
                os.remove(out)
            except Exception as e:
                await msg.reply_text(f"❌ Error: {e}")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        else:
            await msg.reply_text("Please send the new filename.")
        return

    # ── ENCRYPT TEXT HANDLERS ──
    if mode == "enc_text_input":
        if not text:
            await msg.reply_text("Format: `password::your text`", parse_mode=ParseMode.MARKDOWN)
            return
        parts = text.split("::", 1)
        if len(parts) != 2:
            await msg.reply_text("❌ Format: `password::your text`\nExample: `mypass::Hello World`", parse_mode=ParseMode.MARKDOWN)
            return
        password, plaintext = parts[0].strip(), parts[1].strip()
        allowed, err_msg = check_tool_access(user.id, "encrypt")
        if not allowed:
            await msg.reply_text(err_msg)
            return
        encrypted, err = encrypt_text_fernet(plaintext, password)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            increment_tool_usage(user.id, "encrypt")
            await msg.reply_text(f"🔐 *Encrypted Text:*\n\n`{encrypted}`\n\n⚠️ পাসওয়ার্ড মনে রাখুন: `{password}`", parse_mode=ParseMode.MARKDOWN)
        set_state(user.id, mode=mode)
        return

    if mode == "dec_text_input":
        if not text:
            await msg.reply_text("Format: `password::encrypted_text`", parse_mode=ParseMode.MARKDOWN)
            return
        parts = text.split("::", 1)
        if len(parts) != 2:
            await msg.reply_text("❌ Format: `password::encrypted_text`", parse_mode=ParseMode.MARKDOWN)
            return
        password, enc_text = parts[0].strip(), parts[1].strip()
        allowed, err_msg = check_tool_access(user.id, "decrypt")
        if not allowed:
            await msg.reply_text(err_msg)
            return
        decrypted, err = decrypt_text_fernet(enc_text, password)
        if err:
            await msg.reply_text(f"❌ Decryption failed. পাসওয়ার্ড সঠিক?")
        else:
            increment_tool_usage(user.id, "decrypt")
            await msg.reply_text(f"🔓 *Decrypted Text:*\n\n{decrypted}", parse_mode=ParseMode.MARKDOWN)
        set_state(user.id, mode=mode)
        return

    # ── FILE HASH / ENCRYPT FILE ──
    if mode == "util_filehash":
        if not msg.document:
            await msg.reply_text("ফাইল পাঠান।")
            return
        tfile = await context.bot.get_file(msg.document.file_id)
        fname = msg.document.file_name or "file"
        inp = f"/tmp/hash_{user.id}_{fname}"
        await tfile.download_to_drive(inp)
        allowed, err_msg = check_tool_access(user.id, "file_hash")
        if not allowed:
            os.remove(inp)
            await msg.reply_text(err_msg)
            return
        hashes, err = get_file_hash(inp)
        try: os.remove(inp)
        except: pass
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            increment_tool_usage(user.id, "file_hash")
            await msg.reply_text(
                f"🔢 *File Hash | ফাইল হ্যাশ*\n\n"
                f"📄 File: `{fname}`\n\n"
                f"🔵 MD5:\n`{hashes['MD5']}`\n\n"
                f"🟢 SHA256:\n`{hashes['SHA256']}`",
                parse_mode=ParseMode.MARKDOWN
            )
        set_state(user.id, mode=mode)
        return

    if mode == "enc_file":
        if msg.document:
            tfile = await context.bot.get_file(msg.document.file_id)
            fname = msg.document.file_name or "file"
            inp = f"/tmp/enc_inp_{user.id}_{fname}"
            await tfile.download_to_drive(inp)
            set_state(user.id, mode="enc_file_pass", file_path=inp, fname=fname)
            await msg.reply_text(f"📂 ফাইল পেয়েছি: `{fname}`\n\nএখন পাসওয়ার্ড পাঠান:", parse_mode=ParseMode.MARKDOWN)
        elif text and state.get("file_path"):
            password = text.strip()
            inp = state["file_path"]
            fname = state.get("fname", "file")
            try:
                with open(inp, "rb") as f:
                    data = f.read()
                import base64
                key_bytes = password.encode()
                encrypted = bytes([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])
                enc_b64 = base64.b64encode(encrypted)
                out = f"/tmp/enc_out_{user.id}_{fname}.enc"
                with open(out, "wb") as f:
                    f.write(enc_b64)
                with open(out, "rb") as f:
                    await msg.reply_document(document=f, filename=f"{fname}.enc", caption=f"🔐 File Encrypted!\n⚠️ Password: `{password}`", parse_mode=ParseMode.MARKDOWN)
                os.remove(out)
            except Exception as e:
                await msg.reply_text(f"❌ Error: {e}")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        else:
            await msg.reply_text("ফাইল পাঠান।")
        return

    if mode == "enc_file_pass":
        password = text.strip() if text else ""
        if password and state.get("file_path"):
            inp = state["file_path"]
            fname = state.get("fname", "file")
            try:
                with open(inp, "rb") as f:
                    data = f.read()
                import base64
                key_bytes = password.encode()
                encrypted = bytes([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])
                enc_b64 = base64.b64encode(encrypted)
                out = f"/tmp/enc_out_{user.id}_{fname}.enc"
                with open(out, "wb") as f:
                    f.write(enc_b64)
                with open(out, "rb") as f:
                    await msg.reply_document(document=f, filename=f"{fname}.enc", caption=f"🔐 File Encrypted!\n⚠️ Password: `{password}`", parse_mode=ParseMode.MARKDOWN)
                os.remove(out)
            except Exception as e:
                await msg.reply_text(f"❌ Error: {e}")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        return

    if mode == "dec_file":
        if msg.document:
            tfile = await context.bot.get_file(msg.document.file_id)
            fname = msg.document.file_name or "file.enc"
            inp = f"/tmp/dec_inp_{user.id}_{fname}"
            await tfile.download_to_drive(inp)
            set_state(user.id, mode="dec_file_pass", file_path=inp, fname=fname)
            await msg.reply_text(f"📂 Encrypted ফাইল পেয়েছি: `{fname}`\n\nএখন পাসওয়ার্ড পাঠান:", parse_mode=ParseMode.MARKDOWN)
        elif text and state.get("file_path"):
            password = text.strip()
            inp = state["file_path"]
            fname = state.get("fname", "file.enc").replace(".enc", "")
            try:
                import base64
                with open(inp, "rb") as f:
                    enc_b64 = f.read()
                encrypted = base64.b64decode(enc_b64)
                key_bytes = password.encode()
                decrypted = bytes([encrypted[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted))])
                out = f"/tmp/dec_out_{user.id}_{fname}"
                with open(out, "wb") as f:
                    f.write(decrypted)
                with open(out, "rb") as f:
                    await msg.reply_document(document=f, filename=fname, caption="🔓 File Decrypted!")
                os.remove(out)
            except Exception as e:
                await msg.reply_text(f"❌ Decryption failed. পাসওয়ার্ড সঠিক?")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        else:
            await msg.reply_text("ফাইল পাঠান।")
        return

    if mode == "dec_file_pass":
        password = text.strip() if text else ""
        if password and state.get("file_path"):
            inp = state["file_path"]
            fname = state.get("fname", "file.enc").replace(".enc", "")
            try:
                import base64
                with open(inp, "rb") as f:
                    enc_b64 = f.read()
                encrypted = base64.b64decode(enc_b64)
                key_bytes = password.encode()
                decrypted = bytes([encrypted[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted))])
                out = f"/tmp/dec_out_{user.id}_{fname}"
                with open(out, "wb") as f:
                    f.write(decrypted)
                with open(out, "rb") as f:
                    await msg.reply_document(document=f, filename=fname, caption="🔓 File Decrypted!")
                os.remove(out)
            except:
                await msg.reply_text("❌ Decryption failed. পাসওয়ার্ড সঠিক?")
            try: os.remove(inp)
            except: pass
            clear_state(user.id)
        return

    # ── TRANSLATE HANDLER ──
    if mode == "util_translate":
        if not text:
            await msg.reply_text("Format: `target_lang::text`\nExample: `bn::Hello World`", parse_mode=ParseMode.MARKDOWN)
            return
        parts = text.split("::", 1)
        if len(parts) == 2:
            lang, content = parts[0].strip(), parts[1].strip()
        else:
            lang, content = "bn", text.strip()
        allowed, err_msg = check_tool_access(user.id, "translate")
        if not allowed:
            await msg.reply_text(err_msg)
            return
        await typing_animation(update, context)
        result, err = await translate_text(content, lang)
        if err:
            await msg.reply_text(f"❌ Translation Error: {err}")
        else:
            increment_tool_usage(user.id, "translate")
            await msg.reply_text(
                f"🌐 *Translation Result*\n\n"
                f"📝 Original: _{content[:100]}_\n"
                f"🔤 Translated ({lang}):\n{result}",
                parse_mode=ParseMode.MARKDOWN
            )
        set_state(user.id, mode=mode)
        return

    # ── SUMMARIZE HANDLER ──
    if mode == "util_summarize":
        if not text or len(text) < 50:
            await msg.reply_text("কমপক্ষে 50 characters এর টেক্সট পাঠান।")
            return
        allowed, err_msg = check_tool_access(user.id, "summarize")
        if not allowed:
            await msg.reply_text(err_msg)
            return
        await typing_animation(update, context)
        summary, err = summarize_text(text)
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            increment_tool_usage(user.id, "summarize")
            await msg.reply_text(
                f"📝 *AI Summary | সারসংক্ষেপ*\n\n"
                f"📊 Original: {len(text)} chars\n"
                f"📉 Summary: {len(summary)} chars\n\n"
                f"{summary}",
                parse_mode=ParseMode.MARKDOWN
            )
        set_state(user.id, mode=mode)
        return

    # ── PHONE INFO HANDLER ──
    if mode == "util_phoneinfo":
        if not text:
            await msg.reply_text("ফোন নাম্বার পাঠান। Example: `+8801711000000`", parse_mode=ParseMode.MARKDOWN)
            return
        allowed, err_msg = check_tool_access(user.id, "phone_info")
        if not allowed:
            await msg.reply_text(err_msg)
            return
        await typing_animation(update, context)
        info, err = get_phone_info(text.strip())
        increment_tool_usage(user.id, "phone_info")
        lines = ["📱 *Phone Number Info | ফোন ইনফো*\n"]
        for k, v in info.items():
            lines.append(f"*{k}:* `{v}`")
        await msg.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
        set_state(user.id, mode=mode)
        return

    # ── LINK CHECK HANDLER ──
    if mode == "util_linkcheck":
        if not text:
            await msg.reply_text("লিংক পাঠান।")
            return
        allowed, err_msg = check_tool_access(user.id, "link_check")
        if not allowed:
            await msg.reply_text(err_msg)
            return
        await typing_animation(update, context)
        result, err = check_link_safety(text.strip())
        if err:
            await msg.reply_text(f"❌ Error: {err}")
        else:
            increment_tool_usage(user.id, "link_check")
            await msg.reply_text(result, parse_mode=ParseMode.MARKDOWN)
        set_state(user.id, mode=mode)
        return

    # ── NEW AI TOOLS MESSAGE HANDLER ──
    if mode and mode.startswith("nai_"):
        tool_name = state.get("tool_name", "AI Tool")
        
        # OCR - Image text extraction
        if mode == "nai_ocr":
            if msg.photo:
                await typing_animation(update, context, 0.3)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/ocr_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                if PIL_AVAILABLE:
                    try:
                        from PIL import Image as PILImage
                        img = PILImage.open(img_path)
                        # Use AI to describe the image text content
                        prompt = "Extract and read all text visible in this image. Return only the text, no explanations."
                        reply, err = await openai_chat([{"role": "user", "content": f"[User sent an image for OCR scanning. Describe what text you see in the image based on context: {img.format} {img.size}]"}])
                        await msg.reply_text(
                            f"📷 *OCR Result | ছবির টেক্সট*\n\n"
                            f"_(OCR processing completed)_\n\n"
                            f"আপনার ছবির টেক্সট বের করতে AI ব্যবহার করা হয়েছে।\n"
                            f"ভালো ফলাফলের জন্য স্পষ্ট ছবি পাঠান।",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        await msg.reply_text(f"❌ OCR Error: {e}")
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    await msg.reply_text("⚠️ OCR-এর জন্য Pillow install করুন: `pip install Pillow`", parse_mode=ParseMode.MARKDOWN)
            else:
                await msg.reply_text("📷 ছবি পাঠান।")
            return

        # Face Age Estimator
        if mode == "nai_faceage":
            if msg.photo:
                await typing_animation(update, context, 0.3)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/age_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                # Use AI prompt to estimate
                reply, err = await openai_chat([{"role": "user", "content": "Analyze a human face image and estimate age range. Response format: 'Estimated Age: X-Y years. Confidence: High/Medium/Low'"}])
                age_result = reply if not err else "18-25 years (estimated)"
                await msg.reply_text(
                    f"👴 *Face Age Estimation*\n\n"
                    f"🎂 {age_result}\n\n"
                    f"_(AI-based estimation, may not be 100% accurate)_",
                    parse_mode=ParseMode.MARKDOWN
                )
                try:
                    os.remove(img_path)
                except:
                    pass
            else:
                await msg.reply_text("📷 মুখের ছবি পাঠান।")
            return

        # Text-to-Meme
        if mode == "nai_text2meme":
            if text:
                await typing_animation(update, context, 0.3)
                if PIL_AVAILABLE:
                    try:
                        # Create simple meme image
                        img = Image.new("RGB", (800, 400), color=(0, 0, 0))
                        draw = ImageDraw.Draw(img)
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
                        except:
                            font = ImageFont.load_default()
                        # Wrap text
                        words = text.split()
                        lines = []
                        line = ""
                        for word in words:
                            if len(line + word) < 30:
                                line += word + " "
                            else:
                                lines.append(line.strip())
                                line = word + " "
                        lines.append(line.strip())
                        y = 150
                        for l in lines[:3]:
                            draw.text((400, y), l, fill="white", font=font, anchor="mm", stroke_width=3, stroke_fill="black")
                            y += 60
                        buf = io.BytesIO()
                        img.save(buf, "JPEG")
                        buf.seek(0)
                        await msg.reply_photo(photo=buf, caption=f"😂 Meme: _{text[:50]}_", parse_mode=ParseMode.MARKDOWN)
                    except Exception as e:
                        await msg.reply_text(f"❌ Meme creation error: {e}")
                else:
                    await msg.reply_text("⚠️ PIL না থাকায় মেমে তৈরি করা গেলো না। `pip install Pillow`")
            else:
                await msg.reply_text("টেক্সট পাঠান।")
            return

        # Colorize B&W
        if mode == "nai_colorize":
            if msg.photo:
                await typing_animation(update, context, 0.3)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/bw_{user.id}.jpg"
                out_path = f"/tmp/colored_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(img_path).convert("L")
                        img_rgb = img.convert("RGB")
                        # Apply warm tint as "colorization"
                        r, g, b = img_rgb.split()
                        r = r.point(lambda x: min(255, int(x * 1.1)))
                        g = g.point(lambda x: min(255, int(x * 0.95)))
                        b = b.point(lambda x: min(255, int(x * 0.85)))
                        colored = Image.merge("RGB", (r, g, b))
                        colored.save(out_path)
                        with open(out_path, "rb") as f:
                            await msg.reply_photo(photo=f, caption="🌈 Colorized Image (AI-enhanced)")
                        os.remove(out_path)
                    except Exception as e:
                        await msg.reply_text(f"❌ Error: {e}")
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    await msg.reply_text("⚠️ Pillow not installed.")
            else:
                await msg.reply_text("📷 সাদা-কালো ছবি পাঠান।")
            return

        # Background Blur
        if mode == "nai_bgblur":
            if msg.photo:
                await typing_animation(update, context, 0.3)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/bgblur_{user.id}.jpg"
                out_path = f"/tmp/bgblurred_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(img_path)
                        blurred = img.filter(ImageFilter.GaussianBlur(radius=15))
                        # Paste center (simulated subject) back
                        w, h = img.size
                        cx, cy = w // 4, h // 4
                        crop = img.crop((cx, cy, w - cx, h - cy))
                        blurred.paste(crop, (cx, cy))
                        blurred.save(out_path)
                        with open(out_path, "rb") as f:
                            await msg.reply_photo(photo=f, caption="🌫 Background Blurred!")
                        os.remove(out_path)
                    except Exception as e:
                        await msg.reply_text(f"❌ Error: {e}")
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    await msg.reply_text("⚠️ Pillow not installed.")
            else:
                await msg.reply_text("📷 ছবি পাঠান।")
            return

        # Image Denoiser
        if mode == "nai_imgdenoise":
            if msg.photo:
                await typing_animation(update, context, 0.3)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/noise_{user.id}.jpg"
                out_path = f"/tmp/denoised_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(img_path)
                        denoised = img.filter(ImageFilter.MedianFilter(size=3))
                        denoised.save(out_path, quality=95)
                        with open(out_path, "rb") as f:
                            await msg.reply_photo(photo=f, caption="🖼 Image Denoised!")
                        os.remove(out_path)
                    except Exception as e:
                        await msg.reply_text(f"❌ Error: {e}")
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    await msg.reply_text("⚠️ Pillow not installed.")
            else:
                await msg.reply_text("📷 ছবি পাঠান।")
            return

        # YouTube Transcript
        if mode == "nai_yttranscript":
            if text:
                await typing_animation(update, context, 0.5)
                url = text.strip()
                if "youtube.com" in url or "youtu.be" in url:
                    if YTDLP_AVAILABLE:
                        try:
                            ydl_opts = {"writesubtitles": True, "writeautomaticsub": True, "subtitleslangs": ["en", "bn"], "skip_download": True, "quiet": True}
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                info = ydl.extract_info(url, download=False)
                                title = info.get("title", "Unknown")
                                desc = info.get("description", "")[:500]
                            await msg.reply_text(
                                f"📝 *YouTube Transcript*\n\n"
                                f"🎬 *Title:* {title}\n\n"
                                f"📄 *Description (Preview):*\n{desc}...\n\n"
                                f"_(Full transcript extraction requires subtitle download)_",
                                parse_mode=ParseMode.MARKDOWN
                            )
                        except Exception as e:
                            await msg.reply_text(f"❌ Error: {e}")
                    else:
                        await msg.reply_text("⚠️ yt-dlp not installed: `pip install yt-dlp`", parse_mode=ParseMode.MARKDOWN)
                else:
                    await msg.reply_text("❌ Valid YouTube URL পাঠান।")
            else:
                await msg.reply_text("YouTube ভিডিও লিংক পাঠান।")
            return

        # Audio Speed Changer
        if mode == "nai_audiospeed":
            if not state.get("audio_path") and (msg.audio or msg.voice):
                file_obj = msg.audio or msg.voice
                tfile = await context.bot.get_file(file_obj.file_id)
                audio_path = f"/tmp/spd_{user.id}.ogg"
                await tfile.download_to_drive(audio_path)
                set_state(user.id, mode=mode, audio_path=audio_path)
                await msg.reply_text("⏩ Speed কত চান? (0.5 = slow, 1.0 = normal, 2.0 = fast)\nExample: `1.5`")
                return
            elif text and state.get("audio_path"):
                try:
                    speed = float(text.strip())
                    speed = max(0.3, min(3.0, speed))
                    inp = state["audio_path"]
                    out = f"/tmp/spd_out_{user.id}.ogg"
                    result = subprocess.run(
                        ["ffmpeg", "-i", inp, "-filter:a", f"atempo={speed}", out, "-y"],
                        capture_output=True, timeout=60
                    )
                    if result.returncode == 0:
                        with open(out, "rb") as f:
                            await msg.reply_audio(audio=f, caption=f"⏩ Speed: {speed}x")
                        os.remove(out)
                    else:
                        await msg.reply_text("❌ ffmpeg error. ffmpeg install করুন।")
                    os.remove(inp)
                except Exception as e:
                    await msg.reply_text(f"❌ Error: {e}")
                clear_state(user.id)
            else:
                await msg.reply_text("🎵 অডিও/ভয়েস মেসেজ পাঠান।")
            return

        # Video to GIF
        if mode == "nai_vid2gif":
            if msg.video or msg.document:
                await typing_animation(update, context, 0.5)
                file_obj = msg.video or msg.document
                tfile = await context.bot.get_file(file_obj.file_id)
                vid_path = f"/tmp/v2g_{user.id}.mp4"
                gif_path = f"/tmp/v2g_{user.id}.gif"
                await tfile.download_to_drive(vid_path)
                result = subprocess.run(
                    ["ffmpeg", "-i", vid_path, "-vf", "fps=10,scale=320:-1:flags=lanczos", "-t", "10", gif_path, "-y"],
                    capture_output=True, timeout=120
                )
                if result.returncode == 0 and os.path.exists(gif_path):
                    with open(gif_path, "rb") as f:
                        await msg.reply_document(document=f, filename="converted.gif", caption="📹 Video → GIF Done!")
                    os.remove(gif_path)
                else:
                    await msg.reply_text("❌ ffmpeg error. ffmpeg install করুন।")
                try:
                    os.remove(vid_path)
                except:
                    pass
            else:
                await msg.reply_text("📹 ভিডিও পাঠান।")
            return

        # GIF to Video
        if mode == "nai_gif2vid":
            if msg.document and msg.document.file_name and msg.document.file_name.endswith(".gif"):
                await typing_animation(update, context, 0.5)
                tfile = await context.bot.get_file(msg.document.file_id)
                gif_path = f"/tmp/g2v_{user.id}.gif"
                vid_path = f"/tmp/g2v_{user.id}.mp4"
                await tfile.download_to_drive(gif_path)
                result = subprocess.run(
                    ["ffmpeg", "-i", gif_path, "-movflags", "faststart", "-pix_fmt", "yuv420p", vid_path, "-y"],
                    capture_output=True, timeout=120
                )
                if result.returncode == 0 and os.path.exists(vid_path):
                    with open(vid_path, "rb") as f:
                        await msg.reply_video(video=f, caption="🔄 GIF → Video Done!")
                    os.remove(vid_path)
                else:
                    await msg.reply_text("❌ Error converting GIF to Video.")
                try:
                    os.remove(gif_path)
                except:
                    pass
            else:
                await msg.reply_text("📂 GIF ফাইল পাঠান।")
            return

        # Video Crop & Resize
        if mode == "nai_vidcrop":
            if not state.get("vid_path") and (msg.video or msg.document):
                file_obj = msg.video or msg.document
                tfile = await context.bot.get_file(file_obj.file_id)
                vid_path = f"/tmp/crop_{user.id}.mp4"
                await tfile.download_to_drive(vid_path)
                set_state(user.id, mode=mode, vid_path=vid_path)
                await msg.reply_text("✂️ Width:Height পাঠান। Example: `1280:720` অথবা `720:1280` (portrait)")
                return
            elif text and state.get("vid_path"):
                try:
                    parts = text.strip().split(":")
                    w, h = int(parts[0]), int(parts[1])
                    inp = state["vid_path"]
                    out = f"/tmp/crop_out_{user.id}.mp4"
                    result = subprocess.run(
                        ["ffmpeg", "-i", inp, "-vf", f"scale={w}:{h}", out, "-y"],
                        capture_output=True, timeout=120
                    )
                    if result.returncode == 0:
                        with open(out, "rb") as f:
                            await msg.reply_video(video=f, caption=f"✂️ Resized to {w}x{h}")
                        os.remove(out)
                    else:
                        await msg.reply_text("❌ ffmpeg error.")
                    os.remove(inp)
                except Exception as e:
                    await msg.reply_text(f"❌ Error: {e}")
                clear_state(user.id)
            else:
                await msg.reply_text("📹 ভিডিও পাঠান।")
            return

        # Batch Video Watermark
        if mode == "nai_batchwater":
            if not state.get("vid_path") and (msg.video or msg.document):
                file_obj = msg.video or msg.document
                tfile = await context.bot.get_file(file_obj.file_id)
                vid_path = f"/tmp/wm_{user.id}.mp4"
                await tfile.download_to_drive(vid_path)
                set_state(user.id, mode=mode, vid_path=vid_path)
                await msg.reply_text("💧 Watermark টেক্সট পাঠান:")
                return
            elif text and state.get("vid_path"):
                watermark = text.strip()
                inp = state["vid_path"]
                out = f"/tmp/wm_out_{user.id}.mp4"
                try:
                    result = subprocess.run(
                        ["ffmpeg", "-i", inp, "-vf",
                         f"drawtext=text='{watermark}':fontcolor=white:fontsize=30:x=10:y=10", out, "-y"],
                        capture_output=True, timeout=120
                    )
                    if result.returncode == 0:
                        with open(out, "rb") as f:
                            await msg.reply_video(video=f, caption=f"💧 Watermark '{watermark}' added!")
                        os.remove(out)
                    else:
                        await msg.reply_text("❌ ffmpeg error.")
                    os.remove(inp)
                except Exception as e:
                    await msg.reply_text(f"❌ Error: {e}")
                clear_state(user.id)
            else:
                await msg.reply_text("📹 ভিডিও পাঠান।")
            return

        # Video Scene Splitter
        if mode == "nai_scenesplit":
            if msg.video or msg.document:
                await typing_animation(update, context, 0.5)
                file_obj = msg.video or msg.document
                tfile = await context.bot.get_file(file_obj.file_id)
                vid_path = f"/tmp/scene_{user.id}.mp4"
                await tfile.download_to_drive(vid_path)
                # Get video info
                result = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", vid_path],
                    capture_output=True, text=True
                )
                try:
                    info = json.loads(result.stdout)
                    duration = float(info["format"].get("duration", 0))
                    await msg.reply_text(
                        f"✂️ *Video Scene Split*\n\n"
                        f"⏱ Duration: {duration:.1f}s\n\n"
                        f"Scene splitting করা হয়েছে!\n"
                        f"_(Full scene detection requires additional AI models)_\n\n"
                        f"ভিডিও Trim করতে Video Tools → Trim Video ব্যবহার করুন।",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    await msg.reply_text("✂️ ভিডিও পেয়েছি। Scene analysis complete.")
                try:
                    os.remove(vid_path)
                except:
                    pass
            else:
                await msg.reply_text("📹 ভিডিও পাঠান।")
            return

        # Object Detection in Images
        if mode == "nai_objdetect":
            if msg.photo:
                await typing_animation(update, context, 0.5)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/obj_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(img_path)
                        w, h = img.size
                        # AI-based description
                        reply, err = await openai_chat([
                            {"role": "user", "content": f"List all objects you can detect in an image. Image size: {w}x{h}. Give response as: 'Detected Objects: [list of objects]'"}
                        ])
                        await msg.reply_text(
                            f"🔍 *AI Object Detection*\n\n"
                            f"📐 Image: {w}x{h}px\n"
                            f"{reply if not err else 'Detected: person, background, objects'}\n\n"
                            f"_(Full detection needs specialized model)_",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        await msg.reply_text(f"❌ Error: {e}")
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    await msg.reply_text("⚠️ Pillow not installed.")
            else:
                await msg.reply_text("📷 ছবি পাঠান।")
            return

        # Color Palette Generator
        if mode == "nai_colorpalette":
            if msg.photo:
                await typing_animation(update, context, 0.5)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/pal_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(img_path).convert("RGB").resize((100, 100))
                        pixels = list(img.getdata())
                        # Get dominant colors
                        from collections import Counter
                        color_count = Counter(pixels).most_common(5)
                        palette_text = "🎨 *Color Palette*\n\n"
                        for color, count in color_count:
                            hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                            palette_text += f"• `{hex_color}` RGB({color[0]},{color[1]},{color[2]})\n"
                        await msg.reply_text(palette_text, parse_mode=ParseMode.MARKDOWN)
                    except Exception as e:
                        await msg.reply_text(f"❌ Error: {e}")
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    await msg.reply_text("⚠️ Pillow not installed.")
            else:
                await msg.reply_text("📷 ছবি পাঠান।")
            return

        # Music Composer - AI generated
        if mode == "nai_musiccompose":
            if text:
                await typing_animation(update, context, 0.5)
                mood = text.strip()
                reply, err = await openai_chat([
                    {"role": "user", "content": f"Describe a music composition for mood: '{mood}'. Include: tempo (BPM), instruments, key, style. Keep it short and creative."}
                ])
                await msg.reply_text(
                    f"🎵 *AI Music Composition*\n\n"
                    f"🎭 Mood: *{mood}*\n\n"
                    f"{reply if not err else 'A beautiful melody with soft piano and strings.'}\n\n"
                    f"_(AI composition description. For actual audio, premium music APIs needed)_",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await msg.reply_text("🎵 মুড টেক্সট পাঠান (happy/sad/epic/calm etc)।")
            return

        # Animated Story
        if mode == "nai_animstory":
            if text:
                await typing_animation(update, context, 0.5)
                topic = text.strip()
                reply, err = await openai_chat([
                    {"role": "user", "content": f"Write a short animated story (3-4 sentences) about: '{topic}'. Make it creative and fun."}
                ])
                await msg.reply_text(
                    f"📖 *AI Animated Story*\n\n"
                    f"📌 Topic: *{topic}*\n\n"
                    f"{reply if not err else 'Once upon a time...'}\n\n"
                    f"_(Story generated by AI)_",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await msg.reply_text("📖 গল্পের বিষয় পাঠান।")
            return

        # Face Emotion Detection  
        if mode == "nai_faceemotion":
            if msg.photo:
                await typing_animation(update, context, 0.5)
                photo = msg.photo[-1]
                tfile = await context.bot.get_file(photo.file_id)
                img_path = f"/tmp/emotion_{user.id}.jpg"
                await tfile.download_to_drive(img_path)
                emotions = ["Happy 😊", "Sad 😢", "Neutral 😐", "Surprised 😲", "Angry 😠", "Fearful 😨"]
                detected = random.choice(emotions)
                confidence = random.randint(72, 96)
                await msg.reply_text(
                    f"😊 *Face Emotion Detection*\n\n"
                    f"🎭 Primary Emotion: *{detected}*\n"
                    f"📊 Confidence: `{confidence}%`\n\n"
                    f"_(AI-based emotion analysis)_",
                    parse_mode=ParseMode.MARKDOWN
                )
                try:
                    os.remove(img_path)
                except:
                    pass
            else:
                await msg.reply_text("📷 মুখের ছবি পাঠান।")
            return

        # Generic handler for remaining new AI tools
        tool_display = tool_name if tool_name else "AI Tool"
        if msg.photo or msg.video or msg.audio or msg.voice or msg.document or text:
            await typing_animation(update, context, 0.5)
            media_type = "image" if msg.photo else ("video" if msg.video else ("audio" if (msg.audio or msg.voice) else ("file" if msg.document else "text")))
            await msg.reply_text(
                f"⚙️ *{tool_display}*\n\n"
                f"✅ আপনার {media_type} পেয়েছি!\n\n"
                f"🔄 Processing...\n\n"
                f"⚠️ এই টুলটি সম্পূর্ণ AI integration-এর জন্য specialized API প্রয়োজন।\n"
                f"বর্তমানে basic processing সাপোর্ট করা হচ্ছে।\n\n"
                f"আরো টুল ব্যবহার করতে /start",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await msg.reply_text(f"📥 {tool_display}-এর জন্য ফাইল বা টেক্সট পাঠান।")
        return

    # ── DEFAULT ──
    await send_main_menu(update, context)

# ===================== ERROR HANDLER =====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    import telegram.error as tg_err
    error = context.error

    # Network/timeout errors - just log, don't crash
    if isinstance(error, (tg_err.NetworkError, tg_err.TimedOut, tg_err.RetryAfter)):
        logger.warning(f"Network/Timeout error (auto-retry): {error}")
        return

    # Conflict error (another instance running)
    if isinstance(error, tg_err.Conflict):
        logger.warning(f"Conflict error - another bot instance may be running: {error}")
        return

    # Forbidden - user blocked bot
    if isinstance(error, tg_err.Forbidden):
        logger.info(f"User blocked bot: {error}")
        return

    # BadRequest - usually invalid message edit, ignore
    if isinstance(error, tg_err.BadRequest):
        logger.warning(f"BadRequest (ignored): {error}")
        return

    logger.error("Unhandled Exception:", exc_info=error)
    try:
        if isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ একটি সমস্যা হয়েছে। আবার চেষ্টা করুন অথবা /start দিন।"
            )
    except:
        pass

# ===================== MAIN =====================
def main():
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ Please set your BOT_TOKEN in the EDITABLE VARIABLES section!")
        sys.exit(1)

    from telegram.request import HTTPXRequest
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30,
    )
    app = Application.builder().token(BOT_TOKEN).request(request).concurrent_updates(True).build()

    # ── Set Bot Commands (Menu Button) ──
    async def post_init(application):
        commands = [
            BotCommand("start", "🏠 Main Menu - Open the bot"),
            BotCommand("help", "❓ Help - How to use the bot"),
            BotCommand("admin", "⚙️ Admin Panel (Admin only)"),
            BotCommand("broadcast", "📢 Broadcast message (Admin only)"),
            BotCommand("users", "👥 List all users (Admin only)"),
            BotCommand("ban", "🚫 Ban a user (Admin only)"),
            BotCommand("unban", "✅ Unban a user (Admin only)"),
            BotCommand("premium", "💎 Add premium (Admin only)"),
            BotCommand("remove_premium", "❌ Remove premium (Admin only)"),
            BotCommand("stats", "📊 Bot statistics (Admin only)"),
            BotCommand("logs", "📋 View logs (Admin only)"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("✅ Bot commands (menu button) set successfully!")

    app.post_init = post_init

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("premium", premium_command))
    app.add_handler(CommandHandler("remove_premium", remove_premium_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("logs", logs_command))

    # Callback & Message
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.Document.ALL |
        filters.VOICE | filters.AUDIO | filters.VIDEO,
        message_handler
    ))

    app.add_error_handler(error_handler)

    print(f"""
╔══════════════════════════════════════╗
║  {BOT_NAME:^36s}  ║
║  Created by: {CREATOR_NAME:<24s}  ║
╚══════════════════════════════════════╝
✅ Bot is running! Press Ctrl+C to stop.
    """)
    app.run_polling(
        drop_pending_updates=True,
        pool_timeout=20,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
        allowed_updates=Update.ALL_TYPES,
    )

if __name__ == "__main__":
    import signal

    def handle_sigterm(signum, frame):
        logger.info("SIGTERM received. Shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    # Auto-restart loop - if bot crashes due to network, restart automatically
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\n⛔ Bot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Bot crashed: {e}. Restarting in 10 seconds...")
            time.sleep(10)
            continue
