from flask import Flask, render_template, request, redirect, url_for, session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
from functools import wraps
import sqlite3
from werkzeug.security import check_password_hash

from news_fetch import fetch_news
from key import NEWSAPI_KEY

app = Flask(__name__)
app.secret_key = 'your_secret_key_fake_news_detector_2026'

# Load model & tokenizer
model = load_model("model/fake_news_lstm.h5")
with open("model/tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        # Try to authenticate using the local SQLite database
        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            conn.close()

            if row and check_password_hash(row[0], password):
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                # Invalid credentials
                return render_template("login.html", error="Invalid username or password")
        except Exception as e:
            # If there's a DB connection issue, fall back to demo credentials and show helpful message
            demo_creds = {"demo": "demo123", "admin": "admin123", "test": "test123"}
            if username in demo_creds and demo_creds[username] == password:
                session['user'] = username
                return redirect(url_for('dashboard'))
            return render_template("login.html", error=f"Database error: {e} — run create_db.py or use demo credentials")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

def predict_fake_news(text):
    trimmed_text = " ".join(text.split()[:300])
    trimmed_text = clean_text(trimmed_text)

    seq = tokenizer.texts_to_sequences([trimmed_text])
    padded = pad_sequences(seq, maxlen=300)

    pred = model.predict(padded)[0][0]
    label = "REAL" if pred > 0.65 else "FAKE"
    confidence = pred if pred > 0.65 else 1 - pred

    return label, round(float(confidence) * 100, 2)

@app.route("/", methods=["GET"])
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # 🔥 FETCH 50 or 100 ARTICLES
    articles = fetch_news(
        api_key=NEWSAPI_KEY,
        max_articles=50   # change to 100 if you want
    )

    results = []
    for article in articles:
        text = article["title"]
        if article["description"]:
            text += " " + article["description"]

        label, confidence = predict_fake_news(text)
        article["prediction"] = label
        article["confidence"] = confidence
        results.append(article)

    return render_template("dashboard.html", articles=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)