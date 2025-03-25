import streamlit as st
import together
import pandas as pd
import plotly.express as px
import mysql.connector
from datetime import datetime
from textblob import TextBlob
from fpdf import FPDF

# Configure Together AI API
together.api_key = "18c6fa2e02eb288b23fa340015fa36ba5303c242b2debf238b25e15716937ae5"

# Configure MySQL Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Change this
        user="root",  # Change this
        password="Tribal@chief1",  # Change this
        database="wellness_tracker"  # Use the new database name
    )

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_checkin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATETIME NOT NULL,
            mood_level INT NOT NULL,
            energy_level INT NOT NULL,
            stress_level INT NOT NULL,
            sleep_quality VARCHAR(20) NOT NULL,
            social_interaction VARCHAR(20) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATETIME NOT NULL,
            entry TEXT NOT NULL,
            sentiment VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_tables()

def analyze_sentiment(entry):
    sentiment = TextBlob(entry).sentiment.polarity
    if sentiment > 0:
        return "Positive 😊"
    elif sentiment < 0:
        return "Negative 😔"
    else:
        return "Neutral 😐"

def save_mood_checkin(mood, energy, stress, sleep, social):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mood_checkin (date, mood_level, energy_level, stress_level, sleep_quality, social_interaction)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (datetime.now(), mood, energy, stress, sleep, social))
    conn.commit()
    conn.close()

def save_journal_entry(entry):
    sentiment = analyze_sentiment(entry)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journal_entries (date, entry, sentiment)
        VALUES (%s, %s, %s)
    """, (datetime.now(), entry, sentiment))
    conn.commit()
    conn.close()

def fetch_mood_history():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM mood_checkin ORDER BY date DESC", conn)
    conn.close()
    return df

def fetch_journal_entries():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM journal_entries ORDER BY date DESC", conn)
    conn.close()
    return df

def generate_pdf_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM mood_checkin ORDER BY date DESC LIMIT 10")
    mood_data = cursor.fetchall()

    cursor.execute("SELECT * FROM journal_entries ORDER BY date DESC LIMIT 5")
    journal_data = cursor.fetchall()

    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Your Wellness Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, "Mood Check-in History", ln=True)
    pdf.set_font("Arial", size=12)

    if mood_data:
        for entry in mood_data:
            pdf.cell(200, 10, f"Date: {entry['date']}, Mood: {entry['mood_level']}, Energy: {entry['energy_level']}", ln=True)
    else:
        pdf.cell(200, 10, "No mood check-ins recorded yet.", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, "Journal Entries", ln=True)
    pdf.set_font("Arial", size=12)

    if journal_data:
        for entry in journal_data:
            pdf.multi_cell(0, 10, f"Date: {entry['date']}\nEntry: {entry['entry']}\nSentiment: {entry['sentiment']}", border=1)
            pdf.ln(5)
    else:
        pdf.cell(200, 10, "No journal entries recorded yet.", ln=True)

    pdf_path = "wellness_report.pdf"
    pdf.output(pdf_path)
    return pdf_path

def main():
    st.set_page_config(page_title="Emotional Wellness Assistant", layout="wide")
    st.title("🌸 Emotional Wellness Assistant")
    
    tab1, tab2, tab3 = st.tabs(["Mood Tracker", "Journal & Insights", "Coping Strategies"])
    
    with tab1:
        st.subheader("Daily Check-in")
        current_mood = st.slider("Current Mood", 1, 10, 5)
        energy_level = st.slider("Energy Level", 1, 10, 5)
        stress_level = st.slider("Stress Level", 1, 10, 5)
        sleep_quality = st.select_slider("Sleep Quality", ["Poor", "Fair", "Good", "Very Good", "Excellent"])
        social_interaction = st.select_slider("Social Interaction", ["Very Low", "Low", "Moderate", "High", "Very High"])
        
        if st.button("Save Daily Check-in"):
            save_mood_checkin(current_mood, energy_level, stress_level, sleep_quality, social_interaction)
            st.success("Check-in saved!")
        
    with tab2:
        st.subheader("Journal & Insights")
        journal_entry = st.text_area("Write about your day:")
        if st.button("Save Journal Entry"):
            save_journal_entry(journal_entry)
            st.success("Journal entry saved!")
        
        if st.button("Download Wellness Report (PDF)"):
            report_path = generate_pdf_report()
            st.download_button("Download Report", report_path, file_name="wellness_report.pdf")

if __name__ == "__main__":
    main()




