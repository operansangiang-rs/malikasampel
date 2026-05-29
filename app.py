import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF

# Konfigurasi Halaman
st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

# --- FUNGSI GENERATE PDF A4 ---
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="LAPORAN OPERASIONAL TRAFO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=f"Nama Proyek : {row['Nama Proyek']}", ln=True)
    pdf.cell(0, 10, txt=f"Teknisi     : {row['Teknisi']}", ln=True)
    pdf.cell(0, 10, txt=f"Tanggal     : {row['Tanggal']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Rincian Jobdesk:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, txt=pd.DataFrame(json.loads(row['Job'])).to_string(index=False))
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Kebutuhan Material:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, txt=pd.DataFrame(json.loads(row['Material'])).to_string(index=False))
    return pdf.output(dest='S').encode('latin-1')

# --- SISTEM LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🔐 Login Sistem Operasional")
    role = st.selectbox("Pilih Akses:", ["Pilih...", "Admin", "User"])
    if role != "Pilih...":
        pwd = st.text_input("Password:", type="password")
        if st.button("Login"):
            if (role == "Admin" and pwd == "1234") or (role == "User" and pwd == "2222"):
                st.session_state.logged_in = True; st.session_state.role = role.lower(); st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("👤 Profil")
st.sidebar.write(f"Status: **{st.session_state.role.upper()}**")
if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

# --- TAMPILAN UTAMA ---
st.title("📦 Sistem Operasional Trafo")
tabs = ["🔍 Cari & Lihat Data", "🔔 Notifikasi"]
if st.session_state.role == "admin": tabs.insert(0, "➕ Input Data Baru")
tab_list = st.tabs(tabs)

# --- TAB INPUT ---
if st.session_state.role == "admin":
    with tab_list[0]:
        st.header("Tambah Proyek")
        col1, col2 = st.columns(2)
        n = col1.text_input("Nama Proyek"); t = col2.text_input("Teknisi"); tg = st.date_input("Tanggal")
        dj = st.data_editor(pd.DataFrame(columns=["Deskripsi"]), num_rows="dynamic")
        dm = st.data_editor(pd.DataFrame(columns=["Material", "Qty", "Satuan"]), num_rows="dynamic")
        if st.button("Simpan Data"):
            pd.DataFrame([{"Nama Proyek": n, "Teknisi": t, "Tanggal": str(tg), "Job": json.dumps(dj.to_dict()), "Material": json.dumps(dm.to_dict())}]).to_csv("proyek_data.csv", mode='a', header=not os.path.exists("proyek_data.csv"), index=False)
            st.success("Tersimpan!")

# --- TAB CARI & LIHAT ---
idx = 1 if st.session_state.role == "admin" else 0
with tab_list[idx]:
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        for i, row in df.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {row['Tanggal']}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])), use_container_width=True)
                st.dataframe(pd.DataFrame(json.loads(row['Material'])), use_container_width=True)
                
                # Tombol Aksi
                col1, col2 = st.columns([1, 4])
                col1.download_button("📄 PDF A4", generate_pdf(row), f"{row['Nama Proyek']}.pdf")
                if st.session_state.role == "admin":
                    if st.button("🗑️ Hapus", key=f"del_{i}"): df.drop(i).to_csv("proyek_data.csv", index=False); st.rerun()

# --- TAB NOTIFIKASI ---
with tab_list[-1]:
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        up = df[(df['Tanggal'] >= pd.Timestamp(datetime.now().date())) & (df['Tanggal'] <= pd.Timestamp(datetime.now().date()) + timedelta(days=7))]
        for _, row in up.iterrows(): st.info(f"📅 {row['Tanggal'].date()}: {row['Nama Proyek']}")
