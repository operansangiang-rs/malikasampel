import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ops Trafo", layout="wide")

st.title("Sistem Operasional Trafo")

# Inisialisasi session state agar data tidak hilang saat input
if 'data_job' not in st.session_state:
    st.session_state.data_job = pd.DataFrame(columns=["Nama Teknisi", "Detail Pekerjaan", "Tanggal"])
if 'data_material' not in st.session_state:
    st.session_state.data_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

# --- BAGIAN INPUT JOB ---
st.subheader("1. Input Jobdesk (Tanpa Qty)")
# st.data_editor membuat tabel bisa diedit seperti Excel
st.session_state.data_job = st.data_editor(
    st.session_state.data_job, 
    num_rows="dynamic", 
    use_container_width=True
)

# --- BAGIAN INPUT MATERIAL ---
st.subheader("2. Input Material & Qty")
st.session_state.data_material = st.data_editor(
    st.session_state.data_material, 
    num_rows="dynamic", 
    use_container_width=True
)

# --- TOMBOL SIMPAN ---
if st.button("Simpan Semua Data Proyek"):
    st.success("Data berhasil disimpan!")
    st.write("Data Job:", st.session_state.data_job)
    st.write("Data Material:", st.session_state.data_material)
    # Di sini nanti bisa ditambahkan fungsi untuk save ke CSV atau Google Sheets
