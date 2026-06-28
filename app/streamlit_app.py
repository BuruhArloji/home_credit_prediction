from __future__ import annotations

import streamlit as st

from model_utils import find_artifact_dir, load_artifacts, predict_credit_risk


st.set_page_config(
    page_title="Credit Risk Scoring Demo",
    page_icon="🏦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .score-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 1rem 0 1.2rem 0;
    }
    .score-card {
        border: 1px solid #e6e8ef;
        border-radius: 18px;
        padding: 1rem 1.05rem;
        background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
        min-height: 132px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }
    .score-label {
        color: #5d6472;
        font-size: 0.92rem;
        line-height: 1.25;
        margin-bottom: 0.55rem;
        font-weight: 600;
    }
    .score-value {
        color: #2d3140;
        font-size: clamp(1.75rem, 3.2vw, 2.75rem);
        line-height: 1.05;
        font-weight: 650;
        letter-spacing: -0.03em;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    .score-help {
        color: #7a8190;
        font-size: 0.82rem;
        line-height: 1.3;
        margin-top: 0.65rem;
    }
    @media (max-width: 980px) {
        .score-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 620px) {
        .score-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def cached_artifacts():
    return load_artifacts()


def pct(value: float) -> str:
    return f"{value:.2%}"


st.title("Home Credit Risk Scoring Demo")
st.caption(
    "Portfolio product demo berbasis Machine Learning. Aplikasi ini bersifat decision-support, "
    "bukan sistem persetujuan kredit otomatis."
)

artifact_dir = find_artifact_dir()
if artifact_dir is None:
    st.error("Model artifacts belum ditemukan.")
    st.info(
        "Jalankan notebook V4 sampai section `SAVE MODEL DAN FITUR`, atau set "
        "`MODEL_ARTIFACT_DIR` ke folder artifact model."
    )
    st.stop()

try:
    artifacts = cached_artifacts()
except Exception as exc:
    st.error("Gagal memuat artifact model.")
    st.exception(exc)
    st.stop()

st.sidebar.success(f"Artifact aktif: {artifacts.artifact_dir}")
st.sidebar.metric("Jumlah fitur model", f"{len(artifacts.feature_names):,}")
st.sidebar.metric("PD cutoff bisnis", pct(artifacts.recommended_pd_cutoff))
st.sidebar.metric("Threshold model", f"{artifacts.model_threshold:.2f}")

with st.form("credit_application_form"):
    st.subheader("1. Profil Calon Debitur")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.slider("Usia", 18, 70, 35)
        gender = st.selectbox("Gender", ["F", "M"])
        income = st.number_input("Pendapatan tahunan", min_value=10_000, max_value=5_000_000, value=180_000, step=10_000)
        children = st.number_input("Jumlah anak", min_value=0, max_value=10, value=0, step=1)
    with col2:
        education = st.selectbox(
            "Pendidikan",
            [
                "Secondary / secondary special",
                "Higher education",
                "Incomplete higher",
                "Lower secondary",
                "Academic degree",
            ],
        )
        family_status = st.selectbox(
            "Status keluarga",
            ["Married", "Single / not married", "Civil marriage", "Separated", "Widow"],
        )
        housing = st.selectbox(
            "Tipe tempat tinggal",
            ["House / apartment", "With parents", "Municipal apartment", "Rented apartment", "Office apartment"],
        )
        employment_years = st.slider("Lama bekerja (tahun)", 0.0, 40.0, 5.0, 0.5)
    with col3:
        own_car = st.selectbox("Punya mobil?", ["N", "Y"])
        own_realty = st.selectbox("Punya properti?", ["Y", "N"])
        income_type = st.selectbox("Tipe pendapatan", ["Working", "Commercial associate", "Pensioner", "State servant"])
        occupation = st.selectbox("Pekerjaan", ["Laborers", "Sales staff", "Core staff", "Managers", "Drivers", "High skill tech staff"])

    st.subheader("2. Detail Pinjaman")
    col4, col5, col6 = st.columns(3)
    with col4:
        contract_type = st.selectbox("Tipe kontrak", ["Cash loans", "Revolving loans"])
        credit = st.number_input("Jumlah kredit", min_value=10_000, max_value=5_000_000, value=600_000, step=10_000)
    with col5:
        annuity = st.number_input("Anuitas / cicilan tahunan", min_value=1_000, max_value=1_000_000, value=30_000, step=1_000)
        goods_price = st.number_input("Harga barang", min_value=10_000, max_value=5_000_000, value=600_000, step=10_000)
    with col6:
        ext_source_1 = st.slider(
            "Skor eksternal profil kredit",
            0.0,
            1.0,
            0.50,
            0.01,
            help="Skor dari sumber data eksternal. Makin tinggi biasanya menunjukkan profil risiko yang lebih baik.",
        )
        ext_source_2 = st.slider(
            "Skor eksternal perilaku finansial",
            0.0,
            1.0,
            0.50,
            0.01,
            help="Ringkasan sinyal finansial eksternal. Nilai rendah dapat meningkatkan estimasi risiko gagal bayar.",
        )
        ext_source_3 = st.slider(
            "Skor eksternal stabilitas pembayaran",
            0.0,
            1.0,
            0.50,
            0.01,
            help="Proxy stabilitas/kelayakan dari sumber eksternal. Makin tinggi biasanya lebih aman.",
        )

    st.subheader("3. Ringkasan Histori Kredit")
    col7, col8, col9 = st.columns(3)
    with col7:
        overdue_days = st.number_input("Maksimum hari overdue historis", min_value=0, max_value=365, value=0, step=1)
    with col8:
        late_payment_rate = st.slider("Rasio pembayaran terlambat", 0.0, 1.0, 0.00, 0.01)
    with col9:
        cc_utilization = st.slider("Utilization kartu kredit", 0.0, 1.5, 0.35, 0.01)

    submitted = st.form_submit_button("Hitung Risiko Kredit", use_container_width=True)

if submitted:
    user_input = {
        "AGE_YEARS": age,
        "CODE_GENDER": gender,
        "AMT_INCOME_TOTAL": income,
        "CNT_CHILDREN": children,
        "NAME_EDUCATION_TYPE": education,
        "NAME_FAMILY_STATUS": family_status,
        "NAME_HOUSING_TYPE": housing,
        "EMPLOYMENT_YEARS": employment_years,
        "FLAG_OWN_CAR": own_car,
        "FLAG_OWN_REALTY": own_realty,
        "NAME_INCOME_TYPE": income_type,
        "OCCUPATION_TYPE": occupation,
        "NAME_CONTRACT_TYPE": contract_type,
        "AMT_CREDIT": credit,
        "AMT_ANNUITY": annuity,
        "AMT_GOODS_PRICE": goods_price,
        "EXT_SOURCE_1": ext_source_1,
        "EXT_SOURCE_2": ext_source_2,
        "EXT_SOURCE_3": ext_source_3,
        "CREDIT_DAY_OVERDUE": overdue_days,
        "ADV_INST_LATE_PAYMENT_RATE": late_payment_rate,
        "ADV_CC_UTILIZATION": cc_utilization,
    }

    result = predict_credit_risk(user_input, artifacts)

    st.divider()
    st.subheader("Hasil Scoring")
    st.markdown(
        f"""
        <div class="score-grid">
            <div class="score-card">
                <div class="score-label">Estimasi Risiko Gagal Bayar</div>
                <div class="score-value">{pct(result["pd_calibrated"])}</div>
                <div class="score-help">Probabilitas setelah kalibrasi</div>
            </div>
            <div class="score-card">
                <div class="score-label">Kategori Risiko</div>
                <div class="score-value">{result["risk_band"]}</div>
                <div class="score-help">Segmentasi risiko applicant</div>
            </div>
            <div class="score-card">
                <div class="score-label">Rekomendasi Keputusan</div>
                <div class="score-value">{result["business_decision"]}</div>
                <div class="score-help">Berdasarkan cutoff bisnis</div>
            </div>
            <div class="score-card">
                <div class="score-label">Skor Risiko Awal Model</div>
                <div class="score-value">{pct(result["pd_raw"])}</div>
                <div class="score-help">Sebelum kalibrasi isotonic</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(min(result["pd_calibrated"], 1.0), text="Estimasi peluang gagal bayar")

    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown("#### Alasan Utama")
        for reason in result["reason_codes"]:
            st.write(f"- {reason}")
    with right:
        st.markdown("#### Detail Perhitungan")
        st.write(f"- Skor risiko dari LightGBM: `{pct(result['pd_lgbm'])}`")
        st.write(f"- Skor risiko dari Logistic Regression: `{pct(result['pd_logreg'])}`")
        st.write(f"- Porsi kontribusi LightGBM: `{artifacts.ensemble_weight_lgbm:.2f}`")
        st.write(f"- Batas risiko untuk approve: `{pct(result['recommended_pd_cutoff'])}`")

    with st.expander("Lihat fitur yang dikirim ke model"):
        non_zero = result["feature_frame"].T.reset_index()
        non_zero.columns = ["feature", "value"]
        non_zero = non_zero[non_zero["value"].astype(str).ne("0")]
        st.dataframe(non_zero.head(80), use_container_width=True)

st.divider()
st.caption(
    "Responsible AI note: output ini adalah simulasi portfolio. Keputusan kredit nyata perlu validasi data, "
    "monitoring drift, fairness review, explainability, governance, dan persetujuan kebijakan risiko."
)
