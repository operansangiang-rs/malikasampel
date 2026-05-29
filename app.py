import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF

st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

# --- SISTEM LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.title("🔐 Login Sistem Operasional")
    password = st.text_input("Masukkan Password", type="password")
    if st.button("Login"):
        if password == "1234":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        elif password == "2222":
            st.session_state.logged_in = True
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Password Salah!")
    st.stop()

# --- FUNGSI PDF ---
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Laporan Proyek: {row['Nama Proyek']}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Tanggal: {row['Tanggal']}", ln=True)
    pdf.cell(200, 10, txt=f"Teknisi: {row['Teknisi']}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Rincian Jobdesk:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=pd.DataFrame(json.loads(row['Job'])).to_string(index=False))
    return pdf.output(dest='S').encode('latin-1')

# --- TAMPILAN UTAMA SETELAH LOGIN ---
st.title("📦 Sistem Operasional Trafo")
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Inisialisasi Data
if 'df_job' not in st.session_state: st.session_state.df_job = pd.DataFrame(columns=["Deskripsi Pekerjaan"])
if 'df_material' not in st.session_state: st.session_state.df_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

# Navigasi Tab (Admin bisa lihat semua, User tidak bisa lihat Input)
tabs = ["🔍 Cari & Lihat Data", "🔔 Notifikasi"]
if st.session_state.role == "admin":
    tabs.insert(0, "➕ Input Data Baru")

tab1, tab2, tab3 = st.tabs(tabs)

# --- TAB 1: INPUT (Hanya Admin) ---
if st.session_state.role == "admin":
    with tab1:
        # (Kode Input Data Baru sama seperti sebelumnya)
        nama_proyek = st.text_input("Nama Proyek")
        teknisi = st.text_input("Nama Teknisi")
        tanggal_kerja = st.date_input("Tanggal")
        st.session_state.df_job = st.data_editor(st.session_state.df_job, num_rows="dynamic")
        st.session_state.df_material = st.data_editor(st.session_state.df_material, num_rows="dynamic")
        if st.button("Simpan"):
            new_entry = {"Nama Proyek": nama_proyek, "Teknisi": teknisi, "Tanggal": str(tanggal_kerja), 
                         "Job": json.dumps(st.session_state.df_job.to_dict()), 
                         "Material": json.dumps(st.session_state.df_material.to_dict())}
            pd.DataFrame([new_entry]).to_csv("proyek_data.csv", mode='a', header=not os.path.exists("proyek_data.csv"), index=False)
            st.success("Tersimpan!")

# --- TAB 2 & 3: LIHAT & NOTIFIKASI (Bisa diakses keduanya) ---
with tab2: # Cari & Lihat
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        for _, row in df.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']}"):
                st.write(f"Teknisi: {row['Teknisi']}")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])))
                st.dataframe(pd.DataFrame(json.loads(row['Material'])))
                st.download_button("📄 Download PDF", generate_pdf(row), f"{row['Nama Proyek']}.pdf", "application/pdf")

# (Tambahkan logika Notifikasi di Tab 3 seperti sebelumnya)
