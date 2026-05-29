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
    role_choice = st.selectbox("Pilih Akses Masuk:", ["Pilih...", "Admin", "User"])
    if role_choice != "Pilih...":
        password = st.text_input(f"Masukkan Password untuk {role_choice}:", type="password")
        if st.button("Login"):
            if role_choice == "Admin" and password == "1234":
                st.session_state.logged_in = True; st.session_state.role = "admin"; st.rerun()
            elif role_choice == "User" and password == "2222":
                st.session_state.logged_in = True; st.session_state.role = "user"; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# --- FUNGSI PDF ---
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Laporan: {row['Nama Proyek']}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=f"Teknisi: {row['Teknisi']}\nTanggal: {row['Tanggal']}")
    return pdf.output(dest='S').encode('latin-1')

# --- TAMPILAN UTAMA ---
st.title("📦 Sistem Operasional Trafo")
st.sidebar.write(f"Status: **{st.session_state.role.upper()}**")
if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

tabs = ["🔍 Cari & Lihat Data", "🔔 Notifikasi"]
if st.session_state.role == "admin": tabs.insert(0, "➕ Input Data Baru")
tab_list = st.tabs(tabs)

# --- TAB INPUT ---
if st.session_state.role == "admin":
    with tab_list[0]:
        st.header("Tambah Proyek")
        nama = st.text_input("Nama Proyek")
        teknisi = st.text_input("Teknisi")
        tgl = st.date_input("Tanggal")
        if st.button("Simpan Data"):
            new_entry = {"Nama Proyek": nama, "Teknisi": teknisi, "Tanggal": str(tgl), "Job": "{}", "Material": "{}"}
            pd.DataFrame([new_entry]).to_csv("proyek_data.csv", mode='a', header=not os.path.exists("proyek_data.csv"), index=False)
            st.success("Tersimpan!")

# --- TAB LIHAT DATA (DENGAN EDIT & HAPUS) ---
idx_lihat = 1 if st.session_state.role == "admin" else 0
with tab_list[idx_lihat]:
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        for idx, row in df.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']}"):
                st.write(f"Teknisi: {row['Teknisi']} | Tgl: {row['Tanggal']}")
                
                if st.session_state.role == "admin":
                    col_e, col_d, col_p = st.columns([1,1,4])
                    # TOMBOL EDIT
                    if col_e.button("✏️ Edit", key=f"e_{idx}"):
                        st.session_state[f"editing_{idx}"] = True
                    
                    # FORM EDIT
                    if st.session_state.get(f"editing_{idx}", False):
                        with st.form(key=f"form_{idx}"):
                            new_nama = st.text_input("Nama Baru", value=row['Nama Proyek'])
                            if st.form_submit_button("Update"):
                                df.at[idx, 'Nama Proyek'] = new_nama
                                df.to_csv("proyek_data.csv", index=False)
                                st.session_state[f"editing_{idx}"] = False
                                st.rerun()
                    
                    # TOMBOL HAPUS
                    if col_d.button("🗑️ Hapus", key=f"d_{idx}"):
                        df.drop(idx).to_csv("proyek_data.csv", index=False); st.rerun()
                    
                    col_p.download_button("📄 PDF", generate_pdf(row), f"{row['Nama Proyek']}.pdf")
    else: st.info("Belum ada data.")

# --- TAB NOTIFIKASI ---
idx_notif = 2 if st.session_state.role == "admin" else 1
with tab_list[idx_notif]:
    st.header("🔔 Proyek Mendatang")
    # (Logika notifikasi sama seperti sebelumnya)
