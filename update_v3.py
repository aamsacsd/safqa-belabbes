# -*- coding: utf-8 -*-
"""
Script de mise à jour v3 pour Safqa Belabbes.
Ajoute : récupération mot de passe par téléphone, publicités gratuites,
mise en relation (groupement), profils publics.
"""
from pathlib import Path
import re

BASE = Path("safqa-belabbes-platform")

def read(f):
    return (BASE / f).read_text(encoding="utf-8")

def write(f, c):
    (BASE / f).write_text(c, encoding="utf-8")

def replace(f, old, new, count=1):
    content = read(f)
    if old not in content:
        print(f"! Motif non trouvé dans {f}: {old[:50]}...")
        return False
    write(f, content.replace(old, new, count))
    print(f"OK {f}")
    return True

def append(f, c):
    write(f, read(f) + c)
    print(f"OK {f} (append)")

# ========== 1. DATABASE ==========
print("--- Mise à jour database.py ---")
replace("database.py",
    "phone = db.Column(db.String(20), nullable=True)",
    "phone = db.Column(db.String(20), unique=True, nullable=False)"
)

# Ajout des nouveaux modèles à la fin de database.py
append("database.py", '''

class Ad(db.Model):
    """Publicité soumise par un organisme (gratuite)."""
    __tablename__ = "ads"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500))
    is_approved = db.Column(db.Boolean, default=False) # modéré par l'admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PartnershipAd(db.Model):
    """Annonce de recherche de partenaire pour un groupement."""
    __tablename__ = "partnership_ads"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tender_title = db.Column(db.String(300), nullable=False)
    looking_for = db.Column(db.String(300), nullable=False) # le profil recherché
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PasswordReset(db.Model):
    """Code de réinitialisation de mot de passe par téléphone."""
    __tablename__ = "password_resets"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
''')

# ========== 2. APP ==========
print("--- Mise à jour app.py ---")
replace("app.py",
    "from database import db, User, Tender, Notification",
    "from database import db, User, Tender, Notification, Ad, PartnershipAd, PasswordReset"
)
replace("app.py",
    "import logging",
    "import random\nimport string\nfrom datetime import datetime, timedelta\nimport logging"
)

# Routes pour mot de passe oublié
new_routes = '''

# ============ MOT DE PASSE OUBLIÉ (par téléphone) ============
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        user = User.query.filter_by(phone=phone).first()
        if not user:
            flash("Numéro non trouvé.", "error")
            return render_template("forgot_password.html")
        code = "".join(random.choices(string.digits, k=6))
        expires = datetime.utcnow() + timedelta(minutes=15)
        reset = PasswordReset(phone=phone, code=code, expires_at=expires)
        db.session.add(reset)
        db.session.commit()
        # En production : envoyer par SMS. Ici : affiché pour la démo.
        flash(f"Code (démo) : {code}", "success")
        return redirect(url_for("reset_password", phone=phone))
    return render_template("forgot_password.html")

@app.route("/reset-password/<phone>", methods=["GET", "POST"])
def reset_password(phone):
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        new_pass = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        reset = PasswordReset.query.filter_by(phone=phone, code=code, used=False).first()
        if not reset or reset.expires_at < datetime.utcnow():
            flash("Code invalide ou expiré.", "error")
            return render_template("reset_password.html", phone=phone)
        if len(new_pass) < 6 or new_pass != confirm:
            flash("Mot de passe invalide.", "error")
            return render_template("reset_password.html", phone=phone)
        user = User.query.filter_by(phone=phone).first()
        if user:
            user.set_password(new_pass)
            reset.used = True
            db.session.commit()
            flash("Mot de passe réinitialisé. Connectez-vous.", "success")
            return redirect(url_for("login"))
    return render_template("reset_password.html", phone=phone)

# ============ PUBLICITÉS (annonceurs) ============
@app.route("/ads", methods=["GET", "POST"])
@login_required
def ads():
    if request.method == "POST":
        ad = Ad(user_id=current_user.id, title=request.form["title"],
                description=request.form["description"], link=request.form.get("link"))
        db.session.add(ad)
        db.session.commit()
        flash("Publicité soumise. En attente d'approbation.", "success")
        return redirect(url_for("ads"))
    my_ads = Ad.query.filter_by(user_id=current_user.id).order_by(Ad.created_at.desc()).all()
    approved = Ad.query.filter_by(is_approved=True).order_by(Ad.created_at.desc()).limit(20).all()
    return render_template("ads.html", my_ads=my_ads, approved=approved)

# ============ MISE EN RELATION (groupement) ============
@app.route("/partners", methods=["GET", "POST"])
@login_required
def partners():
    if request.method == "POST":
        p = PartnershipAd(user_id=current_user.id, tender_title=request.form["tender_title"],
                          looking_for=request.form["looking_for"], message=request.form.get("message"))
        db.session.add(p)
        db.session.commit()
        flash("Annonce publiée.", "success")
        return redirect(url_for("partners"))
    all_ads = PartnershipAd.query.order_by(PartnershipAd.created_at.desc()).all()
    return render_template("partners.html", partners=all_ads)

# ============ PROFIL PUBLIC ============
@app.route("/profile/<int:uid>")
def public_profile(uid):
    user = User.query.get_or_404(uid)
    user_ads = Ad.query.filter_by(user_id=uid, is_approved=True).all()
    return render_template("profile.html", user=user, ads=user_ads)

# ============ ADMIN : APPROUVER LES PUBS ============
@app.route("/admin/approve-ad/<int:aid>")
@login_required
def admin_approve_ad(aid):
    require_admin()
    ad = Ad.query.get_or_404(aid)
    ad.is_approved = not ad.is_approved
    db.session.commit()
    flash("Statut de la publicité modifié.", "success")
    return redirect(url_for("admin_panel"))
'''

# Insérer les routes avant la fonction init_app
marker = "def init_app(app):"
content = read("app.py")
if marker in content:
    content = content.replace(marker, new_routes + "\n" + marker, 1)
    write("app.py", content)
    print("OK Routes ajoutées à app.py")

# Ajouter l'affichage des pubs approuvées sur l'index (dans le template plus tard)
# ========== 3. TEMPLATES ==========
print("--- Création des nouveaux templates ---")

# forgot_password.html
write("templates/forgot_password.html", '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Mot de passe oublié</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><h1>{{ app_name }}</h1></header>
<main class="auth-container">
{% with messages = get_flashed_messages(with_categories=true) %}{% for c,m in messages %}<div class="flash flash-{{c}}">{{m}}</div>{% endfor %}{% endwith %}
<h2>Réinitialiser par téléphone</h2>
<form method="POST" class="auth-form">
<label>Numéro de téléphone<input type="tel" name="phone" required placeholder="05XXXXXXXX"></label>
<button type="submit">Envoyer le code</button>
</form>
<p class="auth-switch"><a href="/login">← Retour à la connexion</a></p>
</main></body></html>
''')

# reset_password.html
write("templates/reset_password.html", '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Nouveau mot de passe</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><h1>{{ app_name }}</h1></header>
<main class="auth-container">
{% with messages = get_flashed_messages(with_categories=true) %}{% for c,m in messages %}<div class="flash flash-{{c}}">{{m}}</div>{% endfor %}{% endwith %}
<h2>Code de vérification</h2>
<form method="POST" class="auth-form">
<label>Code à 6 chiffres<input type="text" name="code" maxlength="6" required></label>
<label>Nouveau mot de passe<input type="password" name="password" minlength="6" required></label>
<label>Confirmer<input type="password" name="confirm" minlength="6" required></label>
<button type="submit">Valider</button>
</form>
</main></body></html>
''')

# ads.html
write("templates/ads.html", '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Publicités</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><div class="nav-bar"><h1><a href="/" style="color:white;text-decoration:none;">{{ app_name }}</a></h1>
<nav class="user-nav"><a href="/">Offres</a><a href="/partners">Partenaires</a><a href="/logout">Déconnexion</a></nav></div></header>
<main>
<h2>Espace publicitaire (gratuit)</h2>
<div class="auth-container" style="max-width:600px;">
<form method="POST" class="auth-form">
<label>Titre<input type="text" name="title" required></label>
<label>Description<textarea name="description" rows="3" required></textarea></label>
<label>Lien (optionnel)<input type="url" name="link"></label>
<button type="submit">Soumettre la publicité</button>
</form>
</div>
<h2 style="margin-top:2rem;">Mes publicités</h2>
{% for ad in my_ads %}<div class="notif-item"><div>{{ ad.title }} <span class="badge-{{ 'premium' if ad.is_approved else 'free' }}">{{ 'Approuvée' if ad.is_approved else 'En attente' }}</span></div></div>{% endfor %}
<h2 style="margin-top:2rem;">Publicités approuvées</h2>
{% for ad in approved %}<div class="notif-item"><div><strong>{{ ad.title }}</strong><p>{{ ad.description }}</p>{% if ad.link %}<a href="{{ ad.link }}" target="_blank">En savoir plus</a>{% endif %}</div></div>{% endfor %}
</main></body></html>
''')

# partners.html
write("templates/partners.html", '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Partenaires</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><div class="nav-bar"><h1><a href="/" style="color:white;text-decoration:none;">{{ app_name }}</a></h1>
<nav class="user-nav"><a href="/">Offres</a><a href="/ads">Publicités</a><a href="/logout">Déconnexion</a></nav></div></header>
<main>
<h2>Rechercher un partenaire pour soumissionner ensemble</h2>
<div class="auth-container" style="max-width:600px;">
<form method="POST" class="auth-form">
<label>Appel d'offres concerné<input type="text" name="tender_title" required></label>
<label>Profil recherché (ex: électricien, génie civil)<input type="text" name="looking_for" required></label>
<label>Message<textarea name="message" rows="2"></textarea></label>
<button type="submit">Publier l'annonce</button>
</form>
</div>
<h2 style="margin-top:2rem;">Annonces de groupement</h2>
{% for p in partners %}
<div class="notif-item">
<div><strong>{{ p.tender_title }}</strong><p>Cherche : {{ p.looking_for }}</p><p style="font-size:0.85rem;color:#555;">{{ p.message }}</p></div>
<a href="/profile/{{ p.user_id }}" class="btn-mark">Voir le profil</a>
</div>
{% endfor %}
</main></body></html>
''')

# profile.html
write("templates/profile.html", '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Profil de {{ user.full_name }}</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"></head>
<body><header><h1>{{ app_name }}</h1></header>
<main class="auth-container">
<h2>{{ user.full_name }}</h2>
<p><strong>Entreprise :</strong> {{ user.company or '-' }}</p>
<p><strong>Secteur :</strong> {{ user.sector_interest or 'Non spécifié' }}</p>
<h3 style="margin-top:1.5rem;">Publicités actives</h3>
{% for ad in ads %}<div class="notif-item"><div>{{ ad.title }}<p>{{ ad.description }}</p></div></div>{% else %}<p>Aucune publicité approuvée.</p>{% endfor %}
<p style="margin-top:1rem;"><a href="/partners">← Retour aux partenaires</a></p>
</main></body></html>
''')

# Mettre à jour login.html pour ajouter le lien "Mot de passe oublié"
content_login = read("templates/login.html")
if "/forgot-password" not in content_login:
    content_login = content_login.replace(
        '<p class="auth-switch">',
        '<p class="auth-switch"><a href="/forgot-password">Mot de passe oublié ?</a></p>\n<p class="auth-switch">',
        1
    )
    write("templates/login.html", content_login)
    print("OK login.html (lien mot de passe oublié)")

# ========== 4. CSS ==========
append("static/style.css", '''
/* Styles pour les nouvelles fonctionnalités */
.badge-premium, .badge-free { font-size: 0.7rem; padding: 0.1rem 0.4rem; margin-left: 0.5rem; }
textarea { font-family: inherit; padding: 0.6rem; border: 1px solid #ccc; border-radius: 6px; resize: vertical; }
''')

print("\n=== Mise à jour v3 terminée avec succès ! ===")
print("Redémarrez l'application : cd safqa-belabbes-platform && python app.py")
