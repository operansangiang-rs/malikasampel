import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ops Trafo - Input", layout="wide")

st.title("Input Operasional Proyek")

# --- BAGIAN 1: IDENTITAS PROYEK & TEKNISI ---
st.subheader("👤 Informasi Dasar")
col1, col2 = st.columns(2)

with col1:
    nama_proyek = st.text_input("Nama Proyek/Lokasi")
with col2:
    # Input teknisi fleksibel: bisa satu, bisa banyak dipisah koma
    teknisi = st.text_input("Nama Teknisi (Pisahkan dengan koma jika lebih dari satu)")

tanggal_kerja = st.date_input("Tanggal Pelaksanaan")

st.divider()

# --- BAGIAN 2: JOBDESK (TABEL) ---
st.subheader("📋 Rincian Pekerjaan")
if 'df_job' not in st.session_state:
    st.session_state.df_job = pd.DataFrame(columns=["Deskripsi Pekerjaan"])

st.session_state.df_job = st.data_editor(
    st.session_state.df_job,
    num_rows="dynamic",
    use_container_width=True
)

st.divider()

# --- BAGIAN 3: MATERIAL (TABEL) ---
st.subheader("🛠️ Kebutuhan Material")
if 'df_material' not in st.session_state:
    st.session_state.df_material = pd.DataFrame(columns=["Nama Material", "Qty", "Satuan"])

st.session_state.df_material = st.data_editor(
    st.session_state.df_material,
    num_rows="dynamic",
    use_container_width=True
)

# --- TOMBOL SIMPAN ---
if st.button("Simpan Data Proyek"):
    if not nama_proyek or not teknisi:
        st.error("Nama Proyek dan Teknisi wajib diisi!")
    else:
        st.success(f"Data Proyek '{nama_proyek}' berhasil diproses.")
        # Di sini nanti kita tambahkan logic save ke database/file
