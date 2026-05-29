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
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Teknisi: {row['Teknisi']}", ln=True)
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
        col1, col2 = st.columns(2)
        nama = col1.text_input("Nama Proyek")
        teknisi = col2.text_input("Teknisi")
        tgl = st.date_input("Tanggal")
        # Inisialisasi editor data
        df_j = st.data_editor(pd.DataFrame(columns=["Deskripsi"]), num_rows="dynamic")
        df_m = st.data_editor(pd.DataFrame(columns=["Material"]), num_rows="dynamic")
        if st.button("Simpan Data"):
            new_entry = {"Nama Proyek": nama, "Teknisi": teknisi, "Tanggal": str(tgl), 
                         "Job": json.dumps(df_j.to_dict()), "Material": json.dumps(df_m.to_dict())}
            pd.DataFrame([new_entry]).to_csv("proyek_data.csv", mode='a', header=not os.path.exists("proyek_data.csv"), index=False)
            st.success("Tersimpan!")

# --- TAB CARI & LIHAT DATA ---
idx_lihat = 1 if st.session_state.role == "admin" else 0
with tab_list[idx_lihat]:
    st.header("Daftar Proyek")
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        for idx, row in df.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {row['Tanggal']}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.write("**Jobdesk:**")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])), use_container_width=True)
                st.write("**Material:**")
                st.dataframe(pd.DataFrame(json.loads(row['Material'])), use_container_width=True)
                
                if st.session_state.role == "admin":
                    col1, col2, col3 = st.columns([1, 1, 4])
                    if col1.button("✏️ Edit", key=f"e_{idx}"): st.session_state[f"edit_{idx}"] = True
                    if col2.button("🗑️ Hapus", key=f"d_{idx}"): 
                        df.drop(idx).to_csv("proyek_data.csv", index=False); st.rerun()
                    
                    if st.session_state.get(f"edit_{idx}", False):
                        with st.form(key=f"f_{idx}"):
                            new_n = st.text_input("Ubah Nama:", value=row['Nama Proyek'])
                            if st.form_submit_button("Update"):
                                df.at[idx, 'Nama Proyek'] = new_n
                                df.to_csv("proyek_data.csv", index=False)
                                st.session_state[f"edit_{idx}"] = False; st.rerun()
    else: st.info("Data belum tersedia.")

# --- TAB NOTIFIKASI ---
idx_notif = 2 if st.session_state.role == "admin" else 1
with tab_list[idx_notif]:
    st.header("🔔 Proyek Mendatang (7 Hari)")
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        upcoming = df[(df['Tanggal'] >= pd.Timestamp(datetime.now().date())) & (df['Tanggal'] <= pd.Timestamp(datetime.now().date()) + timedelta(days=7))]
        for _, row in upcoming.iterrows():
            st.info(f"📅 {row['Tanggal'].date()}: {row['Nama Proyek']}")
