import os, sqlite3, secrets
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

APP_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.environ.get("DATABASE_PATH", os.path.join(APP_DIR,"malika.db"))
UPLOAD_DIR=os.path.join(APP_DIR,"static","uploads")
os.makedirs(UPLOAD_DIR,exist_ok=True)
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-key-"+secrets.token_hex(16))
app.config["MAX_CONTENT_LENGTH"]=8*1024*1024
ALLOWED={"png","jpg","jpeg","webp","gif"}

def db():
    c=sqlite3.connect(DB_PATH)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT '');
        CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,description TEXT DEFAULT '',price INTEGER DEFAULT 0,image TEXT DEFAULT '',active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS announcements(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT DEFAULT '',body TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS videos(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,url TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,event_date TEXT NOT NULL,title TEXT NOT NULL,event_type TEXT DEFAULT 'Mashg‘ulot',time TEXT DEFAULT '',place TEXT DEFAULT '',note TEXT DEFAULT '',price INTEGER DEFAULT 0);
        """)
        if not c.execute("SELECT 1 FROM users").fetchone():
            username=os.environ.get("ADMIN_USER","malika")
            password=os.environ.get("ADMIN_PASSWORD","Malika2026!")
            c.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",(username,generate_password_hash(password)))
        defaults={"shop_name":"Malika","about":"Herbalife mahsulotlari – sog‘lom turmush sari birga","phone":"","telegram":"","instagram":"","address":"","hours":"","logo":""}
        for k,v in defaults.items(): c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",(k,v))
        if not c.execute("SELECT 1 FROM products").fetchone():
            c.executemany("INSERT INTO products(name,description,price) VALUES(?,?,?)",[
                ("Formula 1 kokteyli","To‘yimli ovqat o‘rnini bosuvchi kokteyl",0),
                ("Protein Drink Mix","Oqsilli ichimlik kukuni",0),
                ("Aloe Vera ichimligi","Aloe asosidagi ichimlik",0)])
init_db()

def settings():
    with db() as c: return {r["key"]:r["value"] for r in c.execute("SELECT * FROM settings")}
def admin_required(fn):
    @wraps(fn)
    def wrapper(*a,**kw):
        if not session.get("admin"): return redirect(url_for("login",next=request.path))
        return fn(*a,**kw)
    return wrapper
def save_image(file):
    if not file or not file.filename: return ""
    ext=file.filename.rsplit(".",1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED: raise ValueError("Faqat PNG, JPG, WEBP yoki GIF rasm yuklang.")
    name=secrets.token_hex(12)+"."+ext
    file.save(os.path.join(UPLOAD_DIR,name))
    return "uploads/"+name
@app.route("/")
def home():
    with db() as c:
        products=c.execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC").fetchall()
        announcements=c.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        videos=c.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
        events=c.execute("SELECT * FROM events ORDER BY event_date").fetchall()
    return render_template("index.html",s=settings(),products=products,announcements=announcements,videos=videos,events=events)
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        with db() as c: user=c.execute("SELECT * FROM users WHERE username=?",(request.form.get("username",""),)).fetchone()
        if user and check_password_hash(user["password_hash"],request.form.get("password","")):
            session["admin"]=user["id"]; return redirect(url_for("dashboard"))
        flash("Login yoki parol noto‘g‘ri.")
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))
@app.route("/admin")
@admin_required
def dashboard():
    with db() as c:
        products=c.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        announcements=c.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        videos=c.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
        events=c.execute("SELECT * FROM events ORDER BY event_date DESC").fetchall()
    return render_template("admin.html",s=settings(),products=products,announcements=announcements,videos=videos,events=events)
@app.route("/admin/settings",methods=["POST"])
@admin_required
def update_settings():
    keys=["shop_name","about","phone","telegram","instagram","address","hours"]
    with db() as c:
        for k in keys: c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(k,request.form.get(k,"").strip()))
        f=request.files.get("logo")
        if f and f.filename:
            path=save_image(f); c.execute("UPDATE settings SET value=? WHERE key='logo'",(path,))
    flash("Sayt ma’lumotlari saqlandi."); return redirect(url_for("dashboard")+"#settings")
@app.route("/admin/product/save",methods=["POST"])
@admin_required
def save_product():
    pid=request.form.get("id")
    name=request.form.get("name","").strip()
    if not name: flash("Mahsulot nomini kiriting."); return redirect(url_for("dashboard")+"#products")
    image=request.form.get("old_image","")
    f=request.files.get("image")
    if f and f.filename: image=save_image(f)
    values=(name,request.form.get("description","").strip(),max(0,int(request.form.get("price") or 0)),image)
    with db() as c:
        if pid: c.execute("UPDATE products SET name=?,description=?,price=?,image=? WHERE id=?",(*values,pid))
        else: c.execute("INSERT INTO products(name,description,price,image) VALUES(?,?,?,?)",values)
    flash("Mahsulot saqlandi."); return redirect(url_for("dashboard")+"#products")
@app.route("/admin/product/delete/<int:pid>",methods=["POST"])
@admin_required
def delete_product(pid):
    with db() as c: c.execute("DELETE FROM products WHERE id=?",(pid,))
    flash("Mahsulot o‘chirildi."); return redirect(url_for("dashboard")+"#products")
@app.route("/admin/announcement/save",methods=["POST"])
@admin_required
def save_announcement():
    title=request.form.get("title","").strip(); body=request.form.get("body","").strip()
    if body:
        with db() as c: c.execute("INSERT INTO announcements(title,body,created_at) VALUES(?,?,?)",(title,body,datetime.now().strftime("%d.%m.%Y")))
    flash("E’lon qo‘shildi."); return redirect(url_for("dashboard")+"#news")
@app.route("/admin/announcement/delete/<int:i>",methods=["POST"])
@admin_required
def delete_announcement(i):
    with db() as c: c.execute("DELETE FROM announcements WHERE id=?",(i,))
    return redirect(url_for("dashboard")+"#news")
@app.route("/admin/video/save",methods=["POST"])
@admin_required
def save_video():
    title=request.form.get("title","").strip(); url=request.form.get("url","").strip()
    if title and url.startswith(("https://","http://")):
        with db() as c: c.execute("INSERT INTO videos(title,url) VALUES(?,?)",(title,url))
        flash("Video qo‘shildi.")
    else: flash("Video nomi va to‘g‘ri havolani kiriting.")
    return redirect(url_for("dashboard")+"#videos")
@app.route("/admin/video/delete/<int:i>",methods=["POST"])
@admin_required
def delete_video(i):
    with db() as c: c.execute("DELETE FROM videos WHERE id=?",(i,))
    return redirect(url_for("dashboard")+"#videos")
@app.route("/admin/event/save",methods=["POST"])
@admin_required
def save_event():
    date=request.form.get("event_date",""); title=request.form.get("title","").strip()
    if date and title:
        with db() as c: c.execute("INSERT INTO events(event_date,title,event_type,time,place,note,price) VALUES(?,?,?,?,?,?,?)",
          (date,title,request.form.get("event_type","Mashg‘ulot"),request.form.get("time",""),request.form.get("place",""),request.form.get("note",""),max(0,int(request.form.get("price") or 0))))
        flash("Kalendar tadbiri saqlandi.")
    return redirect(url_for("dashboard")+"#calendar")
@app.route("/admin/event/delete/<int:i>",methods=["POST"])
@admin_required
def delete_event(i):
    with db() as c: c.execute("DELETE FROM events WHERE id=?",(i,))
    return redirect(url_for("dashboard")+"#calendar")
@app.route("/admin/password",methods=["POST"])
@admin_required
def change_password():
    old=request.form.get("old",""); new=request.form.get("new","")
    with db() as c:
        u=c.execute("SELECT * FROM users WHERE id=?",(session["admin"],)).fetchone()
        if not check_password_hash(u["password_hash"],old) or len(new)<8:
            flash("Eski parol noto‘g‘ri yoki yangi parol 8 belgidan kam."); return redirect(url_for("dashboard")+"#security")
        c.execute("UPDATE users SET password_hash=? WHERE id=?",(generate_password_hash(new),session["admin"]))
    flash("Parol yangilandi."); return redirect(url_for("dashboard")+"#security")
@app.errorhandler(413)
def too_large(e): return "Rasm hajmi 8 MB dan oshmasin.",413
if __name__=="__main__": app.run(debug=True,port=int(os.environ.get("PORT",5000)),host="0.0.0.0")
