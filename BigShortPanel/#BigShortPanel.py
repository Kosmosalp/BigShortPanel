# BigShortPanel: Erken Ekonomik Kriz Uyarı Sistemi
# Alp (Kosmosalp) için özel olarak geliştirilmiştir.

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# --- PANEL BAŞLIĞI --- #
st.set_page_config(page_title="BigShortPanel", layout="wide")
st.title("📉 BigShortPanel – 2026 Krizi Erken Uyarı Sistemi")

# --- VERİLERİ ÇEK --- #
@st.cache_data(ttl=3600)
def get_yield_data():
    url = "https://api.tradingeconomics.com/historical/country/united states/indicator/government bond 10y?c=guest:guest&format=json"
    try:
        r = requests.get(url)
        data = pd.DataFrame(r.json())
        data["date"] = pd.to_datetime(data["date"])
        data = data.set_index("date").sort_index()
        return data[["value"]].rename(columns={"value": "10Y Yield"})
    except:
        return pd.DataFrame()

# --- VERİYİ GÖSTER --- #
with st.expander("📈 ABD 10Y Tahvil Verisi (TradingEconomics)", expanded=True):
    data = get_yield_data()
    if not data.empty:
        st.line_chart(data)
    else:
        st.warning("Veri alınamadı. API sınırı dolmuş olabilir.")

# --- UYARI SİSTEMİ --- #
critical_threshold = 3.5  # Örnek eşik değer
def send_email_alert(subject, message):
    from_email = st.secrets["EMAIL_ADDRESS"]
    to_email = st.secrets["EMAIL_ADDRESS"]
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
        st.success("📧 Uyarı e-postası gönderildi.")
    except Exception as e:
        st.error(f"E-posta gönderilemedi: {e}")

if not data.empty and data.iloc[-1, 0] > critical_threshold:
    send_email_alert("BigShortPanel KRİTİK UYARI", f"10Y tahvil getirisi kritik seviyeyi aştı: {data.iloc[-1, 0]}")
    st.error(f"KRİTİK UYARI: Getiri {data.iloc[-1, 0]} seviyesine ulaştı.")
else:
    st.info("📘 Şu anda kritik bir sinyal yok. Panel veri izlemeye devam ediyor.")

# --- NOT --- #
st.caption("Sürüm 1.0 – Kosmos & Alp tarafından geliştirilmiştir. Daha fazla özellik yakında.")
