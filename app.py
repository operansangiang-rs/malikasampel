import streamlit as st
import pandas as pd
import json
import os
import time
import io
import requests
from datetime import datetime, timedelta
from fpdf import FPDF

# Konfigurasi Halaman
st.set_page_config(page_title="Ops Trafo - Malika", layout="wide")

# --- FUNGSI UTAMA ---
def save_and_sort_df(df):
    """Fungsi pembantu untuk menyimpan data dan selalu mengurutkan berdasarkan Tanggal Proyek"""
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df = df.sort_values(by="Tanggal", ascending=False)
    df.to_csv("proyek_data.csv", index=False)

def send_telegram_msg(message):
    token = "ISI_TOKEN_BOT_ANDA" 
    chat_id = "ISI_CHAT_ID_ANDA" 
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    try: requests.get(url)
    except: pass

def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="LAPORAN OPERASIONAL TRAFO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    labels = [("Nama Proyek", row['Nama Proyek']), ("Teknisi", row['Teknisi']), ("Tanggal", row['Tanggal'])]
    for label, val in labels:
        pdf.cell(40, 10, label, 0, 0); pdf.cell(5, 10, ":", 0, 0)
        pdf.set_font("Arial", '', 12); pdf.cell(0, 10, str(val), ln=True); pdf.set_font("Arial", 'B', 12)
    pdf.ln(5)
    def create_table(header, data):
        pdf.set_font("Arial", 'B', 11); pdf.set_fill_color(230, 230, 230)
        col_w = 190 / len(header)
        for h in header: pdf.cell(col_w, 10, h, 1, 0, 'C', True)
        pdf.ln()
        pdf.set_font("Arial", '', 11)
        for _, item in data.iterrows():
            for col in header:
                val = str(item[col]) if pd.notna(item[col]) else ""
                pdf.cell(col_w, 10, val, 1)
            pdf.ln()
    pdf.cell(0, 10, "Rincian Jobdesk:", ln=True)
    job_df = pd.DataFrame(json.loads(row['Job']))
    if not job_df.empty: create_table(job_df.columns.tolist(), job_df)
    pdf.ln(5); pdf.cell(0, 10, "Kebutuhan Material:", ln=True)
    mat_df = pd.DataFrame(json.loads(row['Material']))
    if not mat_df.empty: create_table(mat_df.columns.tolist(), mat_df)
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

st.sidebar.title("👤 Profil")
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
            new_data = {"ID": time.time(), "Nama Proyek": n, "Teknisi": t, "Tanggal": str(tg), 
                        "Job": json.dumps(dj.to_dict(orient='records')), 
                        "Material": json.dumps(dm.to_dict(orient='records'))}
            if os.path.exists("proyek_data.csv"):
                df = pd.read_csv("proyek_data.csv")
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])
            save_and_sort_df(df)
            send_telegram_msg(f"✅ Proyek Baru: {n} oleh {t}")
            st.success("✅ Data berhasil disimpan!")
            time.sleep(1); st.rerun()

# --- TAB CARI & LIHAT ---
idx = 1 if st.session_state.role == "admin" else 0
with tab_list[idx]:
    st.header("Daftar Proyek")
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv")
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        
        if st.session_state.role == "admin":
            with st.expander("📊 Export Laporan Bulanan ke Excel"):
                c_m, c_y = st.columns(2)
                pilih_bulan = c_m.selectbox("Pilih Bulan:", range(1, 13), format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
                pilih_tahun = c_y.selectbox("Pilih Tahun:", [2025, 2026, 2027])
                df_b = df[(df['Tanggal'].dt.month == pilih_bulan) & (df['Tanggal'].dt.year == pilih_tahun)].copy()
                df_b = df_b.sort_values(by='Tanggal', ascending=True)
                df_b['Teknisi'] = df_b['Teknisi'].str.replace(',', '\n')
                df_export = df_b[['Tanggal', 'Nama Proyek', 'Teknisi']]
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_export.to_excel(writer, index=False, sheet_name='Laporan')
                    workbook = writer.book; worksheet = writer.sheets['Laporan']
                    wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
                    worksheet.set_column('A:A', 15, workbook.add_format({'border': 1})); worksheet.set_column('B:B', 30, workbook.add_format({'border': 1})); worksheet.set_column('C:C', 30, wrap_format)
                    for col_num, value in enumerate(df_export.columns.values): worksheet.write(0, col_num, value, header_format)
                st.download_button("📥 Download Excel Ringkas", output.getvalue(), f"Laporan_{pilih_bulan}_{pilih_tahun}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        with st.expander("🔍 Filter Pencarian"):
            c1, c2 = st.columns(2)
            search_nama = c1.text_input("Cari Nama Proyek:")
            use_date = c2.checkbox("Gunakan Filter Tanggal"); search_date = c2.date_input("Pilih Tanggal:") if use_date else None
        
        # Urutan berdasarkan TANGGAL PROYEK (ascending=False -> terbaru di atas)
        f_df = df.sort_values(by="Tanggal", ascending=False)
        if search_nama: f_df = f_df[f_df["Nama Proyek"].str.contains(search_nama, case=False, na=False)]
        if use_date: f_df = f_df[f_df["Tanggal"].dt.date == search_date]
        
        display_df = f_df.head(10) if not search_nama and not use_date else f_df
        if not search_nama and not use_date: st.info("Menampilkan 10 data terbaru.")

        for i, row in display_df.iterrows():
            with st.expander(f"📌 {row['Nama Proyek']} | 📅 {str(row['Tanggal'].date())}"):
                st.write(f"**Teknisi:** {row['Teknisi']}")
                st.dataframe(pd.DataFrame(json.loads(row['Job'])), use_container_width=True)
                st.dataframe(pd.DataFrame(json.loads(row['Material'])), use_container_width=True)
                if st.session_state.role == "admin":
                    c1, c2, c3 = st.columns([1, 1, 4])
                    c1.download_button("📄 PDF A4", generate_pdf(row), f"{row['Nama Proyek']}.pdf")
                    if c2.button("🗑️ Hapus", key=f"del_{row['ID']}"): df = df.drop(i); save_and_sort_df(df); st.rerun()
                    if st.button("✏️ Edit", key=f"edit_{row['ID']}"): st.session_state[f"show_{row['ID']}"] = True
                    if st.session_state.get(f"show_{row['ID']}", False):
                        with st.form(key=f"f_{row['ID']}"):
                            n_n = st.text_input("Nama Proyek:", value=row['Nama Proyek']); n_t = st.text_input("Teknisi:", value=row['Teknisi'])
                            n_j = st.data_editor(pd.DataFrame(json.loads(row['Job'])), num_rows="dynamic")
                            n_m = st.data_editor(pd.DataFrame(json.loads(row['Material'])), num_rows="dynamic")
                            if st.form_submit_button("Simpan Perubahan"):
                                df.loc[df['ID'] == row['ID'], ['Nama Proyek', 'Teknisi', 'Job', 'Material']] = [n_n, n_t, json.dumps(n_j.to_dict(orient='records')), json.dumps(n_m.to_dict(orient='records'))]
                                save_and_sort_df(df); st.success("✅ Data diupdate!"); time.sleep(1); st.session_state[f"show_{row['ID']}"] = False; st.rerun()
                else: st.download_button("📄 Download PDF A4", generate_pdf(row), f"{row['Nama Proyek']}.pdf")
    else: st.info("Belum ada data.")

with tab_list[-1]:
    if os.path.exists("proyek_data.csv"):
        df = pd.read_csv("proyek_data.csv"); df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        up = df[(df['Tanggal'] >= pd.Timestamp(datetime.now().date())) & (df['Tanggal'] <= pd.Timestamp(datetime.now().date()) + timedelta(days=7))]
        for _, row in up.iterrows(): st.info(f"📅 {row['Tanggal'].date()}: {row['Nama Proyek']} (Teknisi: {row['Teknisi']})")
