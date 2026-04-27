import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app)

# =========================
# LOAD MODEL
# =========================
model = joblib.load("models/model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

# =========================
# EMAIL CONFIG
# =========================
EMAIL_ADDRESS = "varshiniash29@gmail.com"
EMAIL_PASSWORD = "tndjqpuljpnfnqiv"  # App Password

# =========================
# OTP STORE
# =========================
otp_store = {}

# =========================
# STORE REPORTS
# =========================
reports = []

# =========================
# HOME
# =========================
@app.route('/')
def home():
    return "Backend is running"

# =========================
# SEND OTP EMAIL FUNCTION
# =========================
def send_otp_email(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "Cyber Portal OTP Verification"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
# =========================
# SEND OTP API
# =========================
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"success": False}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    try:
        send_otp_email(email, otp)
        print(f"✅ OTP sent to {email}: {otp}")
        return jsonify({"success": True})
    except Exception as e:
        print("❌ EMAIL ERROR:", str(e))
        return jsonify({"success": False}), 500


# =========================
# VERIFY OTP API
# =========================
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"success": False}), 400

    if otp_store.get(email) == str(otp):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})    
# =========================
# PREDICT API
# =========================
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "Text required"}), 400

    vect = vectorizer.transform([text])
    prediction = model.predict(vect)[0]
    confidence = max(model.predict_proba(vect)[0])

    if prediction == "fraud":
        risk = "HIGH"
    elif prediction == "phishing":
        risk = "MEDIUM"
    elif prediction == "social_engineering":
        risk = "HIGH"
    else:
        risk = "LOW"

    reports.append({
        "text": text,
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "risk": risk,
        "status": "PENDING"
    })

    return jsonify({
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "risk": risk
    })

# =========================
# GET REPORTS
# =========================
@app.route('/reports', methods=['GET'])
def get_reports():
    return jsonify(reports)

# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)    