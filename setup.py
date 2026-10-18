# -*- coding: utf-8 -*-
from pathlib import Path

BASE = Path("safqa-belabbes-platform")
FILES = {}

FILES["requirements.txt"] = """Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.1
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
gunicorn==21.2.0
"""

FILES[".env.example"] = """SECRET_KEY=change-this-to-a-long-random-string
FLASK_ENV=production
DATABASE_URL=sqlite:///safqa.db
TELEGRAM_TOKEN=
CHAT_ID=
FREE_PLAN_DELAY_HOURS=48
PREMIUM_PRICE_DZD=1500
ADMIN_EMAIL=admin@safqa.dz
ADMIN_PASSWORD=admin123456
"""

FILES["config.py"] = '''# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
load_dotenv()

APP_NAME = "\\u0635\\u0641\\u0642\\u0629 \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "\\u0645\\u0646\\u0635\\u0629 \\u0634\\u0641\\u0627\\u0641\\u0629 \\u0644\\u0644\\u0635\\u0641\\u0642\\u0627\\u062a \\u0627\\u0644\\u0639\\u0645\\u0648\\u0645\\u064a\\u0629 \\u0641\\u064a \\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633"

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///safqa.db")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
FREE_PLAN_DELAY_HOURS = int(os.getenv("FREE_PLAN_DELAY_HOURS", "48"))
PREMIUM_PRICE_DZD = int(os.getenv("PREMIUM_PRICE_DZD", "1500"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@safqa.dz")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123456")
'''

FILES["database.py"] = '''# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(150))
    sector_interest = db.Column(db.String(50))
    role = db.Column(db.String(20), default="user")
    plan = db.Column(db.String(20), default="free")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, p):
        self.password_hash = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

    @property
    def is_premium(self):
        return self.plan == "premium" or self.role == "admin"

    @property
    def is_admin(self):
        return self.role == "admin"


class Tender(db.Model):
    __tablename__ = "tenders"
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(200), unique=True, index=True)
    title = db.Column(db.String(500), nullable=False)
    agency = db.Column(db.String(200), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    commune = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.String(100))
    deadline = db.Column(db.String(100), nullable=False)
    source_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
'''

FILES["scraper.py"] = '''# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from database import db, Tender
import logging
logger = logging.getLogger(__name__)


def sync_tenders(app):
    with app.app_context():
        if Tender.query.count() > 0:
            return 0
        now = datetime.utcnow()
        data = [
            {"title": "\\u062a\\u0647\\u064a\\u0626\\u0629 \\u0627\\u0644\\u0637\\u0631\\u064a\\u0642 \\u0627\\u0644\\u0631\\u0627\\u0628\\u0637 \\u0628\\u064a\\u0646 \\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633 \\u0648\\u062a\\u0644\\u0627\\u063a",
             "agency": "\\u0645\\u062f\\u064a\\u0631\\u064a\\u0629 \\u0627\\u0644\\u0623\\u0634\\u063a\\u0627\\u0644 \\u0627\\u0644\\u0639\\u0645\\u0648\\u0645\\u064a\\u0629",
             "sector": "\\u0623\\u0634\\u063a\\u0627\\u0644", "commune": "\\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633",
             "budget": "45,000,000 \\u062f\\u062c", "deadline": "2026-03-15",
             "source_url": "https://www.marches-publics.gov.dz/",
             "description": "\\u0623\\u0634\\u063a\\u0627\\u0644 \\u062a\\u0647\\u064a\\u0626\\u0629 \\u0648\\u062a\\u0639\\u0628\\u064a\\u062f \\u0627\\u0644\\u0637\\u0631\\u064a\\u0642",
             "created_at": now - timedelta(days=10)},
            {"title": "\\u0627\\u0642\\u062a\\u0646\\u0627\\u0621 \\u062a\\u062c\\u0647\\u064a\\u0632\\u0627\\u062a \\u0645\\u0639\\u0644\\u0648\\u0645\\u0627\\u062a\\u064a\\u0629 \\u0644\\u062c\\u0627\\u0645\\u0639\\u0629 \\u062c\\u064a\\u0644\\u0627\\u0644\\u064a \\u0627\\u0644\\u064a\\u0627\\u0628\\u0633",
             "agency": "\\u062c\\u0627\\u0645\\u0639\\u0629 \\u062c\\u064a\\u0644\\u0627\\u0644\\u064a \\u0627\\u0644\\u064a\\u0627\\u0628\\u0633",
             "sector": "\\u062a\\u0648\\u0631\\u064a\\u062f", "commune": "\\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633",
             "budget": "8,500,000 \\u062f\\u062c", "deadline": "2026-02-28",
             "source_url": "https://www.marches-publics.gov.dz/",
             "description": "\\u062a\\u0648\\u0631\\u064a\\u062f \\u062d\\u0648\\u0627\\u0633\\u064a\\u0628",
             "created_at": now - timedelta(days=5)},
            {"title": "\\u062e\\u062f\\u0645\\u0627\\u062a \\u0627\\u0644\\u0646\\u0638\\u0627\\u0641\\u0629 \\u0648\\u0627\\u0644\\u062d\\u0631\\u0627\\u0633\\u0629 \\u0644\\u0644\\u0645\\u0633\\u062a\\u0634\\u0641\\u0649",
             "agency": "\\u0627\\u0644\\u0645\\u0633\\u062a\\u0634\\u0641\\u0649 \\u0627\\u0644\\u062c\\u0627\\u0645\\u0639\\u064a",
             "sector": "\\u062e\\u062f\\u0645\\u0627\\u062a", "commune": "\\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633",
             "budget": "12,000,000 \\u062f\\u062c", "deadline": "2026-04-10",
             "source_url": "https://www.marches-publics.gov.dz/",
             "description": "\\u0639\\u0642\\u062f \\u0633\\u0646\\u0648\\u064a",
             "created_at": now - timedelta(days=3)},
            {"title": "\\u0625\\u0646\\u062c\\u0627\\u0632 \\u0634\\u0628\\u0643\\u0629 \\u0627\\u0644\\u0635\\u0631\\u0641 \\u0627\\u0644\\u0635\\u062d\\u064a",
             "agency": "\\u0628\\u0644\\u062f\\u064a\\u0629 \\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633",
             "sector": "\\u0623\\u0634\\u063a\\u0627\\u0644", "commune": "\\u0633\\u064a\\u062f\\u064a \\u0628\\u0644\\u0639\\u0628\\u0627\\u0633",
             "budget": "18,750,000 \\u062f\\u062c", "deadline": "2026-03-30",
             "source_url": "https://www.marches-publics.gov.dz/",
             "description": "\\u0634\\u0628\\u0643\\u0629 \\u0635\\u0631\\u0641 \\u0635\\u062d\\u064a 3 \\u0643\\u0645",
             "created_at": now - timedelta(hours=30)},
            {"title": "\\u0627\\u0633\\u062a\\u0634\\u0627\\u0631\\u0629 18/2026: \\u0623\\u0634\\u063a\\u0627\\u0644 \\u0643\\u0627\\u0628\\u0644 \\u0627\\u0644\\u0623\\u0644\\u064a\\u0627\\u0641 \\u0627\\u0644\\u0628\\u0635\\u0631\\u064a\\u0629",
             "agency": "\\u0627\\u062a\\u0635\\u0627\\u0644\\u0627\\u062a \\u0627\\u0644\\u062c\\u0632\\u0627\\u0626\\u0631",
             "sector": "\\u0623\\u0634\\u063a\\u0627\\u0644", "commune": "\\u0628\\u0646 \\u0639\\u0645\\u0631",
             "budget": "\\u063a\\u064a\\u0631 \\u0645\\u062d\\u062f\\u062f", "deadline": "2026-02-20",
             "source_url": "https://www.safqatic.dz/",
             "description": "\\u0643\\u0627\\u0628\\u0644 \\u0627\\u0644\\u0623\\u0644\\u064a\\u0627\\u0641 \\u0627\\u0644\\u0628\\u0635\\u0631\\u064a\\u0629",
             "created_at": now - timedelta(hours=10)},
            {"title": "\\u062a\\u0648\\u0631\\u064a\\u062f \\u0645\\u0648\\u0627\\u062f \\u063a\\u0630\\u0627\\u0626\\u064a\\u0629 \\u0644\\u0644\\u0645\\u0637\\u0627\\u0639\\u0645 \\u0627\\u0644\\u0645\\u062f\\u0631\\u0633\\u064a\\u0629",
             "agency": "\\u0645\\u062f\\u064a\\u0631\\u064a\\u0629 \\u0627\\u0644\\u062a\\u0631\\u0628\\u064a\\u0629",
             "sector": "\\u062a\\u0648\\u0631\\u064a\\u062f", "commune": "\\u0633\\u064a\\u062f\\u064a \\u0644\\u062d\\u0633\\u0646",
             "budget": "6,200,000 \\u062f\\u062c", "deadline": "2026-03-05",
             "source_url": "https://www.marches-publics.gov.dz/",
             "description": "\\u0645\\u0648\\u0627\\u062f \\u063a\\u0630\\u0627\\u0626\\u064a\\u0629",
             "created_at": now - timedelta(hours=5)},
        ]
        added = 0
        for i, item in enumerate(data):
            ext = f"seed-{i}"
            if Tender.query.filter_by(external_id=ext).first():
                continue
            t = Tender(external_id=ext, **item)
            db.session.add(t)
            added += 1
        db.session.commit()
        return added
'''

FILES["telegram_bot.py"] = '''# -*- coding: utf-8 -*-
import requests
from config import TELEGRAM_TOKEN, CHAT_ID
import logging
logger = logging.getLogger(__name__)


def send_telegram_alert(tender):
    if not TELEGRAM_TOKEN:
        return False
    msg = f"*{tender.title}*\\n{tender.agency}\\n{tender.deadline}"
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        logger.error(e)
        return False
'''

FILES["app.py"] = '''# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Tender
from scraper import sync_tenders
from telegram_bot import send_telegram_alert
from config import (APP_NAME, APP_VERSION, APP_DESCRIPTION, SECRET_KEY,
                    DATABASE_URL, FREE_PLAN_DELAY_HOURS, PREMIUM_PRICE_DZD,
                    ADMIN_EMAIL, ADMIN_PASSWORD)
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=DATABASE_URL,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(uid):
    return db.session.get(User, int(uid))


@app.context_processor
def globals_inj():
    return {"app_name": APP_NAME, "app_version": APP_VERSION,
            "app_description": APP_DESCRIPTION, "premium_price": PREMIUM_PRICE_DZD}


@app.route("/")
def index():
    sector = request.args.get("sector", "")
    commune = request.args.get("commune", "")
    q = Tender.query.filter_by(is_active=True)
    if not current_user.is_authenticated or not current_user.is_premium:
        cutoff = datetime.utcnow() - timedelta(hours=FREE_PLAN_DELAY_HOURS)
        q = q.filter(Tender.created_at <= cutoff)
    if sector:
        q = q.filter(Tender.sector == sector)
    if commune:
        q = q.filter(Tender.commune == commune)
    tenders = q.order_by(Tender.created_at.desc()).all()
    sectors = [s[0] for s in db.session.query(Tender.sector).distinct().all()]
    communes = [c[0] for c in db.session.query(Tender.commune).distinct().all()]
    hidden = 0
    if not current_user.is_authenticated or not current_user.is_premium:
        cutoff = datetime.utcnow() - timedelta(hours=FREE_PLAN_DELAY_HOURS)
        hidden = Tender.query.filter(Tender.created_at > cutoff, Tender.is_active == True).count()
    return render_template("index.html", tenders=tenders, sectors=sectors,
                           communes=communes, selected_sector=sector,
                           selected_commune=commune, hidden_count=hidden)


@app.route("/tender/<int:tid>")
@login_required
def tender_detail(tid):
    t = Tender.query.get_or_404(tid)
    if not current_user.is_premium:
        cutoff = datetime.utcnow() - timedelta(hours=FREE_PLAN_DELAY_HOURS)
        if t.created_at > cutoff:
            flash("\\u0645\\u062a\\u0627\\u062d \\u0644\\u0645\\u0634\\u062a\\u0631\\u0643\\u064a Premium \\u0641\\u0642\\u0637.", "warning")
            return redirect(url_for("dashboard"))
    return render_template("detail.html", tender=t)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        fn = request.form.get("full_name", "").strip()
        em = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        cf = request.form.get("confirm", "")
        errs = []
        if not fn: errs.append("Name required")
        if "@" not in em: errs.append("Email invalid")
        if len(pw) < 6: errs.append("Password 6+")
        if pw != cf: errs.append("Passwords differ")
        if User.query.filter_by(email=em).first(): errs.append("Email taken")
        if errs:
            for e in errs: flash(e, "error")
            return render_template("register.html"), 400
        u = User(full_name=fn, email=em, phone=request.form.get("phone"),
                 company=request.form.get("company"),
                 sector_interest=request.form.get("sector_interest"), plan="free")
        u.set_password(pw)
        db.session.add(u); db.session.commit()
        login_user(u)
        flash("OK", "success")
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        em = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        u = User.query.filter_by(email=em).first()
        if u and u.check_password(pw) and u.is_active:
            login_user(u, remember=True)
            return redirect(request.args.get("next") or url_for("index"))
        flash("Invalid credentials", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@app.route("/upgrade", methods=["POST"])
@login_required
def upgrade():
    current_user.plan = "premium"
    db.session.commit()
    flash("Premium activated!", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/notify/<int:tid>")
@login_required
def notify(tid):
    if not current_user.is_premium:
        return redirect(url_for("dashboard"))
    t = Tender.query.get_or_404(tid)
    ok = send_telegram_alert(t)
    flash("Sent" if ok else "Failed (config Telegram)", "success" if ok else "error")
    return redirect(url_for("index"))


def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


@app.route("/admin")
@login_required
def admin_panel():
    require_admin()
    stats = {"users": User.query.count(), "premium": User.query.filter_by(plan="premium").count(),
             "tenders": Tender.query.count(), "active": Tender.query.filter_by(is_active=True).count()}
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    tenders = Tender.query.order_by(Tender.created_at.desc()).limit(50).all()
    return render_template("admin.html", stats=stats, users=users, tenders=tenders)


@app.route("/admin/sync")
@login_required
def admin_sync():
    require_admin()
    n = sync_tenders(app)
    flash(f"{n} new tenders", "success")
    return redirect(url_for("admin_panel"))


@app.route("/api/tenders")
def api_tenders():
    return jsonify([{"id": t.id, "title": t.title, "agency": t.agency, "sector": t.sector,
                     "commune": t.commune, "budget": t.budget, "deadline": t.deadline}
                    for t in Tender.query.filter_by(is_active=True).all()])


@app.route("/api/stats")
def api_stats():
    return jsonify({"users": User.query.count(),
                    "premium": User.query.filter_by(plan="premium").count(),
                    "tenders": Tender.query.filter_by(is_active=True).count(),
                    "version": APP_VERSION})


@app.route("/manifest.json")
def manifest():
    return jsonify({"name": APP_NAME, "short_name": "Safqa", "start_url": "/",
                    "display": "standalone", "background_color": "#f4f6f9",
                    "theme_color": "#0f3460", "lang": "ar", "dir": "rtl"})


def init_app(app):
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email=ADMIN_EMAIL).first():
            a = User(full_name="Admin", email=ADMIN_EMAIL, role="admin", plan="premium")
            a.set_password(ADMIN_PASSWORD)
            db.session.add(a); db.session.commit()
        sync_tenders(app)


if __name__ == "__main__":
    init_app(app)
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

FILES["templates/index.html"] = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ app_name }}</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
<header><div class="nav-bar"><h1><a href="/" style="color:white;text-decoration:none;">{{ app_name }}</a></h1>
<nav class="user-nav">
{% if current_user.is_authenticated %}
<span class="user-name">{{ current_user.full_name }}
{% if current_user.is_premium %}<span class="badge-premium">Premium</span>{% endif %}</span>
{% if current_user.is_admin %}<a href="/admin">Admin</a>{% endif %}
<a href="/dashboard">My account</a><a href="/logout">Logout</a>
{% else %}<a href="/login">Login</a><a href="/register" class="btn-register">Sign up</a>{% endif %}
</nav></div><p>{{ app_description }}</p></header>
<main>
{% with messages = get_flashed_messages(with_categories=true) %}{% for c,m in messages %}<div class="flash flash-{{c}}">{{m}}</div>{% endfor %}{% endwith %}
{% if hidden_count > 0 %}<div class="premium-banner"><strong>{{ hidden_count }} hidden tenders</strong><span>Recent tenders available to Premium members only.</span>{% if current_user.is_authenticated %}<a href="/dashboard">Upgrade</a>{% else %}<a href="/register">Register</a>{% endif %}</div>{% endif %}
<form method="GET" class="filter-bar">
<select name="sector"><option value="">All sectors</option>{% for s in sectors %}<option value="{{s}}" {% if s==selected_sector %}selected{% endif %}>{{s}}</option>{% endfor %}</select>
<select name="commune"><option value="">All communes</option>{% for c in communes %}<option value="{{c}}" {% if c==selected_commune %}selected{% endif %}>{{c}}</option>{% endfor %}</select>
<button type="submit">Filter</button><a href="/" class="reset-btn">Reset</a></form>
<div class="tender-grid">
{% for t in tenders %}
<div class="tender-card">
<div class="tender-header"><span class="sector-badge">{{t.sector}}</span><span class="deadline">{{t.deadline}}</span></div>
<h2><a href="/tender/{{t.id}}">{{t.title}}</a></h2>
<p class="agency">{{t.agency}}</p><p class="meta">{{t.commune}} | {{t.budget}}</p>
<div class="actions"><a href="{{t.source_url}}" target="_blank" class="btn-source">Source</a>
{% if current_user.is_authenticated and current_user.is_premium %}<a href="/admin/notify/{{t.id}}" class="btn-notify">Alert</a>{% endif %}</div>
</div>
{% else %}<p class="empty">No tenders match.</p>{% endfor %}
</div></main>
<footer><p>&copy; 2026 {{ app_name }} — v{{ app_version }}</p></footer>
</body></html>
'''

FILES["templates/detail.html"] = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>{{ tender.title }}</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><div class="nav-bar"><h1><a href="/" style="color:white;text-decoration:none;">{{ app_name }}</a></h1></div></header>
<main class="detail-container">
<h1>{{ tender.title }}</h1>
<div class="detail-meta">
<p><strong>Agency:</strong> {{ tender.agency }}</p>
<p><strong>Sector:</strong> {{ tender.sector }}</p>
<p><strong>Commune:</strong> {{ tender.commune }}</p>
<p><strong>Budget:</strong> {{ tender.budget }}</p>
<p><strong>Deadline:</strong> {{ tender.deadline }}</p></div>
<p class="description">{{ tender.description or "No description" }}</p>
<div class="actions"><a href="{{ tender.source_url }}" target="_blank" class="btn-source">Original</a>
<a href="/" class="btn-notify">Back</a></div></main></body></html>
'''

FILES["templates/register.html"] = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Sign up</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><h1>{{ app_name }}</h1><p>Sign up</p></header>
<main class="auth-container">
{% with messages = get_flashed_messages(with_categories=true) %}{% for c,m in messages %}<div class="flash flash-{{c}}">{{m}}</div>{% endfor %}{% endwith %}
<form method="POST" class="auth-form">
<label>Full name *<input type="text" name="full_name" required></label>
<label>Email *<input type="email" name="email" required></label>
<label>Phone<input type="tel" name="phone"></label>
<label>Company<input type="text" name="company"></label>
<label>Sector<select name="sector_interest"><option value="">All</option><option>Works</option><option>Supply</option><option>Services</option></select></label>
<label>Password *<input type="password" name="password" minlength="6" required></label>
<label>Confirm *<input type="password" name="confirm" minlength="6" required></label>
<button type="submit">Create account</button></form>
<p class="auth-switch">Already registered? <a href="/login">Login</a></p></main></body></html>
'''

FILES["templates/login.html"] = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Login</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><h1>{{ app_name }}</h1><p>Login</p></header>
<main class="auth-container">
{% with messages = get_flashed_messages(with_categories=true) %}{% for c,m in messages %}<div class="flash flash-{{c}}">{{m}}</div>{% endfor %}{% endwith %}
<form method="POST" class="auth-form">
<label>Email<input type="email" name="email" required></label>
<label>Password<input type="password" name="password" required></label>
<button type="submit">Login</button></form>
<p class="auth-switch">No account? <a href="/register">Sign up</a></p>
<p style="text-align:center;font-size:0.8rem;color:#888;margin-top:1rem;">Admin: admin@safqa.dz / admin123456</p>
</main></body></html>
'''

FILES["templates/dashboard.html"] = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Dashboard</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><div class="nav-bar"><h1><a href="/" style="color:white;text-decoration:none;">{{ app_name }}</a></h1>
<nav class="user-nav"><a href="/">Tenders</a><a href="/logout">Logout</a></nav></div></header>
<main>
{% with messages = get_flashed_messages(with_categories=true) %}{% for c,m in messages %}<div class="flash flash-{{c}}">{{m}}</div>{% endfor %}{% endwith %}
<div class="dashboard-card">
<h2>Hello, {{ user.full_name }}</h2>
<p><strong>Email:</strong> {{ user.email }}</p>
<p><strong>Company:</strong> {{ user.company or "-" }}</p>
<p><strong>Plan:</strong> {% if user.is_premium %}<span class="badge-premium">Premium</span>{% else %}<span class="badge-free">Free</span>{% endif %}</p>
{% if not user.is_premium %}
<form method="POST" action="/upgrade"><button type="submit" class="btn-upgrade">Upgrade to Premium - {{ premium_price }} DZD (simulation)</button></form>
<p class="hint">Free: 48h delay. Premium: instant access + alerts.</p>
{% else %}<p style="color:#155724;font-weight:bold;">Premium active.</p>{% endif %}</div>
<div class="dashboard-actions"><a href="/" class="btn-source">Browse tenders</a></div></main></body></html>
'''

FILES["templates/admin.html"] = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Admin</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><div class="nav-bar"><h1><a href="/" style="color:white;text-decoration:none;">{{ app_name }}</a></h1>
<nav class="user-nav"><a href="/">Tenders</a><a href="/logout">Logout</a></nav></div><p>Admin panel</p></header>
<main>
<div class="stats-grid">
<div class="stat-card"><h3>{{ stats.users }}</h3><p>Users</p></div>
<div class="stat-card"><h3>{{ stats.premium }}</h3><p>Premium</p></div>
<div class="stat-card"><h3>{{ stats.tenders }}</h3><p>Tenders</p></div>
<div class="stat-card"><h3>{{ stats.active }}</h3><p>Active</p></div></div>
<div class="admin-actions"><a href="/admin/sync" class="btn-source">Sync tenders</a></div>
<h2 class="section-title">Users</h2>
<div class="table-wrapper"><table class="admin-table"><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Plan</th></tr></thead>
<tbody>{% for u in users %}<tr><td>{{u.id}}</td><td>{{u.full_name}}</td><td>{{u.email}}</td><td>{{u.role}}</td><td>{{u.plan}}</td></tr>{% endfor %}</tbody></table></div>
<h2 class="section-title">Tenders</h2>
<div class="table-wrapper"><table class="admin-table"><thead><tr><th>ID</th><th>Title</th><th>Sector</th><th>Commune</th></tr></thead>
<tbody>{% for t in tenders %}<tr><td>{{t.id}}</td><td>{{t.title[:60]}}</td><td>{{t.sector}}</td><td>{{t.commune}}</td></tr>{% endfor %}</tbody></table></div>
</main></body></html>
'''

FILES["static/style.css"] = '''*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f4f6f9;color:#1a1a2e;line-height:1.6}
header{background:linear-gradient(135deg,#0f3460,#16213e);color:white;padding:1.5rem 1rem;text-align:center}
header h1{font-size:1.8rem}header p{opacity:.85;margin-top:.5rem;font-size:.9rem}
main{max-width:1100px;margin:2rem auto;padding:0 1rem}
.nav-bar{display:flex;justify-content:space-between;align-items:center;max-width:1100px;margin:0 auto .5rem;flex-wrap:wrap;gap:1rem}
.user-nav{display:flex;align-items:center;gap:.75rem;flex-wrap:wrap}
.user-nav a{color:white;text-decoration:none;padding:.35rem .75rem;border-radius:6px;font-size:.9rem}
.user-nav a:hover{background:rgba(255,255,255,.15)}
.btn-register{background:#e94560}
.user-name{font-size:.85rem}
.filter-bar{display:flex;gap:.75rem;flex-wrap:wrap;background:white;padding:1rem;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:1.5rem}
.filter-bar select,.filter-bar button{padding:.6rem 1rem;border:1px solid #ccc;border-radius:6px;font-size:.95rem;font-family:inherit}
.filter-bar button{background:#0f3460;color:white;border:none;cursor:pointer}
.reset-btn{padding:.6rem 1rem;color:#0f3460;text-decoration:none;border:1px solid #0f3460;border-radius:6px;font-size:.95rem}
.tender-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1.5rem}
.tender-card{background:white;border-radius:12px;padding:1.25rem;box-shadow:0 2px 12px rgba(0,0,0,.06);transition:transform .2s;border-right:4px solid #e94560}
.tender-card:hover{transform:translateY(-3px)}
.tender-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem}
.sector-badge{background:#e94560;color:white;padding:.2rem .7rem;border-radius:20px;font-size:.8rem}
.deadline{color:#e94560;font-weight:bold;font-size:.85rem}
.tender-card h2{font-size:1.05rem;margin-bottom:.5rem}
.tender-card h2 a{color:#0f3460;text-decoration:none}
.agency,.meta{font-size:.88rem;color:#555;margin-bottom:.3rem}
.actions{display:flex;gap:.5rem;margin-top:1rem;flex-wrap:wrap}
.btn-source,.btn-notify{padding:.4rem .8rem;border-radius:6px;font-size:.85rem;text-decoration:none;display:inline-block;border:none;cursor:pointer}
.btn-source{background:#0f3460;color:white}
.btn-notify{background:#f0f0f0;color:#333}
.empty{text-align:center;grid-column:1/-1;color:#888;padding:3rem}
.detail-container{background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.detail-container h1{color:#0f3460;margin-bottom:1.5rem;font-size:1.4rem}
.description{margin:1.5rem 0;padding:1rem;background:#f8f9fa;border-radius:8px}
.auth-container{max-width:480px;margin:2rem auto;background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.auth-form{display:flex;flex-direction:column;gap:1rem}
.auth-form label{font-size:.9rem;color:#333;display:flex;flex-direction:column;gap:.35rem}
.auth-form input,.auth-form select{padding:.6rem;border:1px solid #ccc;border-radius:6px;font-size:.95rem;font-family:inherit}
.auth-form button{background:#0f3460;color:white;border:none;padding:.75rem;border-radius:6px;cursor:pointer;font-size:1rem}
.auth-switch{text-align:center;margin-top:1rem;font-size:.9rem}
.auth-switch a{color:#e94560;font-weight:bold}
.flash{padding:.75rem 1rem;border-radius:6px;margin-bottom:1rem;font-size:.9rem}
.flash-success{background:#d4edda;color:#155724}
.flash-error{background:#f8d7da;color:#721c24}
.flash-warning{background:#fff3cd;color:#856404}
.badge-premium{background:#ffc107;color:#333;padding:.15rem .5rem;border-radius:12px;font-size:.75rem;font-weight:bold}
.badge-free{background:#6c757d;color:white;padding:.15rem .5rem;border-radius:12px;font-size:.75rem}
.dashboard-card{background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:1.5rem}
.dashboard-card h2{color:#0f3460;margin-bottom:1rem}
.dashboard-card p{margin-bottom:.5rem}
.btn-upgrade{background:#e94560;color:white;border:none;padding:.75rem 1.5rem;border-radius:8px;font-size:1rem;cursor:pointer;margin-top:1rem;width:100%}
.hint{font-size:.85rem;color:#666;margin-top:.75rem;line-height:1.8}
.premium-banner{background:linear-gradient(135deg,#fff3cd,#ffeaa7);border-right:4px solid #ffc107;padding:1rem 1.25rem;border-radius:8px;margin-bottom:1.5rem;display:flex;flex-direction:column;gap:.35rem}
.premium-banner strong{color:#856404}
.premium-banner a{color:#e94560;font-weight:bold;text-decoration:none;font-size:.9rem}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem}
.stat-card{background:white;padding:1.5rem;border-radius:10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.stat-card h3{color:#0f3460;font-size:2rem;margin-bottom:.5rem}
.admin-actions{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap}
.section-title{color:#0f3460;margin:1.5rem 0 1rem;font-size:1.2rem}
.table-wrapper{background:white;border-radius:10px;overflow-x:auto;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:2rem}
.admin-table{width:100%;border-collapse:collapse;font-size:.88rem}
.admin-table th{background:#0f3460;color:white;padding:.75rem;text-align:right}
.admin-table td{padding:.65rem .75rem;border-bottom:1px solid #eee}
footer{text-align:center;padding:2rem;color:#888;font-size:.85rem}
@media(max-width:600px){header h1{font-size:1.4rem}.nav-bar{justify-content:center}.tender-grid{grid-template-columns:1fr}}'''

FILES["README.md"] = """# Safqa Belabbes

## Run
```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
