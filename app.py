import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
from fpdf import FPDF

# Konfigurasi Halaman
st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

# --- FUNGSI PDF ---
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    
    # Judul
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="LAPORAN OPERASIONAL TRAFO", ln=True, align='C')
    pdf.ln(10)
    
    # Informasi Proyek
    pdf.set_font("Arial", 'B', 12)
    label_width = 35
    
    for label, val in [("Nama Proyek", row['Nama Proyek']), ("Teknisi", row['Teknisi']), ("Tanggal", row['Tanggal'])]:
        pdf.cell(label_width, 10, label, 0, 0)
        pdf.cell(5, 10, ":", 0, 0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, str(val), ln=True)
        pdf.set_font("Arial", 'B', 12)
    
    pdf.ln(5)
    
    # Fungsi pembantu dengan penanganan nilai kosong
    def create_table(header, data):
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(230, 230, 230)
        
        # Hitung lebar kolom otomatis
        col_width = 190 / len(header)
        
        for h in header:
            pdf.cell(col_width, 10, h, 1, 0, 'C', True)
        pdf.ln()
        
        pdf.set_font("Arial", '', 11)
        for _, item in data.iterrows():
            for col in header:
                # Ganti nan/None menjadi string kosong
                val = item[col]
                if pd.isna(val) or val is None:
                    val = ""
                pdf.cell(col_width, 10, str(val), 1)
            pdf.ln()

    # Rincian Jobdesk
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Rincian Jobdesk:", ln=True)
    job_df = pd.DataFrame(json.loads(row['Job']))
    if not job_df.empty:
        create_table(job_df.columns.tolist(), job_df)
    
    pdf.ln(5)
    
    # Kebutuhan Material
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Kebutuhan Material:", ln=True)
    mat_df = pd.DataFrame(json.loads(row['Material']))
    if not mat_df.empty:
        create_table(mat_df.columns.tolist(), mat_df)

    return pdf.output(dest='S').encode('latin-1')

# --- SISTEM LOGIN & SIDEBAR ---
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

st.sidebar.title("👤 Profil Akun")
st.sidebar.write(f"Status: **{st.session_state.role.upper()}**")
if st.sidebar.button("Logout"): st.session_state.logged_in = False; st.rerun()

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
        dj = st.data_editor(pd.DataFrame(columns=["Deskripsi Pekerjaan"]), num_rows="dynamic")
        dm = st.data_editor(pd.DataFrame(columns=["Material", "Qty", "Satuan"]), num_rows="dynamic")
        if st.button("Simpan Data"):
            new_row = pd.DataFrame([{"ID": time.time(), "Nama Proyek": n, "Teknisi": t, "Tanggal": str(tg), 
                                     "Job": json.dumps(dj.to_dict(orient='records')), 
                                     "Material": json.dumps(dm.to_dict(orient='records'))}])
            if os.path.exists("proyek_data.csv"):
                new_row.to_csv("proyek_data.csv", mode='a', header=False, index=False)
            else:
                new_row.to_csv("proyek_data.csv", index=False)
            st.success("✅ Data berhasil disimpan!")

# --- TAB CARI & LIHAT (REVISI PENTING) ---
idx = 1 if st.session_state.role == "admin" else 0
with tab_list[idx]:
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        # Loop dengan memuat ulang DataFrame dari CSV setiap iterasi untuk keamanan data
        for i, row in df.iterrows():
            r_id = row['ID']
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {row['Tanggal']}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])), use_container_width=True)
                st.dataframe(pd.DataFrame(json.loads(row['Material'])), use_container_width=True)
                
                if st.session_state.role == "admin":
                    c1, c2, c3 = st.columns([1, 1, 4])
                    c1.download_button("📄 PDF A4", generate_pdf(row), f"{row['Nama Proyek']}.pdf")
                    if c2.button("🗑️ Hapus", key=f"del_{r_id}"):
                        df.drop(i).to_csv("proyek_data.csv", index=False); st.success("Data dihapus!"); st.rerun()
                    
                    if st.button("✏️ Edit", key=f"edit_{r_id}"): st.session_state[f"show_{r_id}"] = True
                    if st.session_state.get(f"show_{r_id}", False):
                        with st.form(key=f"f_{r_id}"):
                            n_n = st.text_input("Edit Nama Proyek:", value=row['Nama Proyek'])
                            n_t = st.text_input("Edit Teknisi:", value=row['Teknisi'])
                            n_j = st.data_editor(pd.DataFrame(json.loads(row['Job'])), num_rows="dynamic")
                            n_m = st.data_editor(pd.DataFrame(json.loads(row['Material'])), num_rows="dynamic")
                            if st.form_submit_button("Simpan Semua Perubahan"):
                                # Update DataFrame langsung
                                df.loc[i, 'Nama Proyek'] = n_n
                                df.loc[i, 'Teknisi'] = n_t
                                df.loc[i, 'Job'] = json.dumps(n_j.to_dict(orient='records'))
                                df.loc[i, 'Material'] = json.dumps(n_m.to_dict(orient='records'))
                                df.to_csv("proyek_data.csv", index=False)
                                st.success(f"✅ Data '{n_n}' berhasil diupdate!")
                                time.sleep(1) # Jeda agar notifikasi terbaca
                                st.session_state[f"show_{r_id}"] = False; st.rerun()
    else: st.info("Belum ada data.")
