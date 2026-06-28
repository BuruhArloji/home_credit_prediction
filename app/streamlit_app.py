from __future__ import annotations

from html import escape

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
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

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
    :root {
        --ink: #282b3a;
        --muted: #687082;
        --violet: #6147ff;
        --blue: #4592ff;
        --green: #22c55e;
        --orange: #ff8a3d;
        --pink: #ef4cae;
    }

    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(97, 71, 255, 0.18), transparent 24rem),
            radial-gradient(circle at 100% 10%, rgba(69, 146, 255, 0.14), transparent 28rem),
            linear-gradient(135deg, #f9faff 0%, #eef0ff 42%, #f8f9ff 100%);
    }

    .block-container {
        padding-top: 2.1rem;
        padding-bottom: 2.4rem;
        max-width: 1240px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6147ff 0%, #6a5cff 100%);
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.78);
        border-radius: 30px;
        padding: 1.35rem 1.45rem 1.5rem 1.45rem;
        box-shadow: 0 22px 60px rgba(37, 44, 92, 0.12);
        backdrop-filter: blur(12px);
    }

    div[data-testid="stButton"] button {
        border: 0;
        border-radius: 999px;
        background: linear-gradient(135deg, var(--violet), var(--blue));
        color: #ffffff;
        font-weight: 800;
        min-height: 3.1rem;
        box-shadow: 0 16px 30px rgba(97, 71, 255, 0.28);
    }

    .hero-card {
        display: grid;
        grid-template-columns: 1.35fr 0.65fr;
        gap: 1.2rem;
        align-items: stretch;
        margin-bottom: 1.25rem;
    }

    .hero-main {
        position: relative;
        overflow: hidden;
        border-radius: 34px;
        padding: 2rem;
        background: #ffffff;
        box-shadow: 0 24px 70px rgba(37, 44, 92, 0.13);
    }

    .hero-main:after {
        content: "";
        position: absolute;
        right: -5rem;
        top: -5rem;
        width: 16rem;
        height: 16rem;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(97, 71, 255, 0.18), transparent 68%);
    }

    .hero-kicker {
        width: max-content;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        background: #f1efff;
        color: var(--violet);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .hero-title {
        color: var(--ink);
        font-family: 'Space Grotesk', 'Manrope', sans-serif;
        font-size: clamp(2.35rem, 5vw, 4.25rem);
        line-height: 0.94;
        font-weight: 700;
        letter-spacing: -0.055em;
        margin: 0;
        max-width: 760px;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.7;
        max-width: 760px;
        margin-top: 1rem;
    }

    .hero-side {
        border-radius: 34px;
        padding: 1.35rem;
        background: linear-gradient(180deg, #f3f2ff, #ffffff);
        box-shadow: inset 0 0 0 1px rgba(97, 71, 255, 0.08);
    }

    .mini-panel-title {
        color: var(--ink);
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 0.8rem;
    }

    .mix-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(104, 112, 130, 0.12);
        color: var(--muted);
        font-size: 0.86rem;
    }

    .dot {
        width: 0.6rem;
        height: 0.6rem;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.55rem;
    }

    .score-card {
        border: 1px solid rgba(97, 71, 255, 0.08);
        border-radius: 24px;
        padding: 1.15rem 1.2rem;
        background: rgba(255, 255, 255, 0.94);
        min-height: 142px;
        box-shadow: 0 16px 40px rgba(37, 44, 92, 0.10);
    }

    .score-label {
        color: var(--muted);
        font-weight: 750;
    }

    .score-value {
        color: var(--ink);
        font-weight: 800;
    }

    .result-shell {
        display: grid;
        grid-template-columns: 0.82fr 1.18fr;
        gap: 1.15rem;
        margin-top: 0.8rem;
        align-items: stretch;
    }

    .credit-gauge-card, .result-detail-card {
        border-radius: 30px;
        background: #ffffff;
        padding: 1.45rem;
        box-shadow: 0 22px 56px rgba(37, 44, 92, 0.12);
    }

    .credit-gauge-card {
        overflow: visible;
        padding-left: 2.4rem;
        padding-right: 2.4rem;
    }

    .gauge-ring {
        position: relative;
        width: 210px;
        height: 210px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        margin: 1rem auto 1.2rem auto;
        background:
            radial-gradient(circle at center, #ffffff 0 55%, transparent 56%),
            conic-gradient(var(--risk-color) 0 var(--risk-angle), #edf0f6 var(--risk-angle) 100%);
        box-shadow: 0 20px 42px rgba(97, 71, 255, 0.18);
    }

    .gauge-ring:before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
        background:
            conic-gradient(
                transparent 0 calc(var(--low-marker) - 0.35deg),
                rgba(34, 197, 94, 0.95) calc(var(--low-marker) - 0.35deg) calc(var(--low-marker) + 0.35deg),
                transparent calc(var(--low-marker) + 0.35deg) calc(var(--moderate-marker) - 0.35deg),
                rgba(245, 158, 11, 0.95) calc(var(--moderate-marker) - 0.35deg) calc(var(--moderate-marker) + 0.35deg),
                transparent calc(var(--moderate-marker) + 0.35deg) calc(var(--high-marker) - 0.35deg),
                rgba(239, 68, 68, 0.95) calc(var(--high-marker) - 0.35deg) calc(var(--high-marker) + 0.35deg),
                transparent calc(var(--high-marker) + 0.35deg) 360deg
            );
        mask: radial-gradient(circle at center, transparent 0 53%, #000 54% 74%, transparent 75% 100%);
        pointer-events: none;
    }

    .threshold-label {
        position: absolute;
        z-index: 2;
        padding: 0.28rem 0.48rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(104, 112, 130, 0.12);
        box-shadow: 0 8px 22px rgba(37, 44, 92, 0.10);
        color: var(--ink);
        font-size: 0.62rem;
        font-weight: 800;
        line-height: 1.05;
        white-space: nowrap;
    }

    .threshold-label span {
        display: block;
        color: var(--muted);
        font-size: 0.52rem;
        font-weight: 700;
        margin-top: 0.08rem;
    }

    .threshold-low {
        top: 9%;
        right: -2.35rem;
    }

    .threshold-approve {
        right: -2.55rem;
        bottom: 8%;
    }

    .threshold-high {
        left: -2.75rem;
        top: 43%;
    }

    .gauge-inner {
        text-align: center;
    }

    .gauge-value {
        color: var(--ink);
        font-size: clamp(2.3rem, 4vw, 3rem);
        font-weight: 800;
        letter-spacing: -0.06em;
        line-height: 1;
    }

    .gauge-caption {
        color: var(--green);
        font-size: 0.9rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    .section-title {
        color: var(--ink);
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.5rem;
    }

    .reason-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.8rem 1rem;
        border-radius: 18px;
        background: #f6f7ff;
        color: var(--ink);
        margin: 0.4rem 0.4rem 0.4rem 0;
        font-weight: 650;
    }

    .detail-list {
        display: grid;
        gap: 0.65rem;
        margin-top: 0.8rem;
    }

    .detail-item {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.75rem 0.9rem;
        border-radius: 16px;
        background: #f8f9ff;
        color: var(--muted);
        font-weight: 650;
    }

    .detail-value {
        color: #138a43;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-weight: 800;
    }

    @media (max-width: 980px) {
        .hero-card, .result-shell {
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


st.markdown(
    """
    <div class="hero-card">
        <div class="hero-main">
            <div class="hero-kicker">Credit Risk Product Demo</div>
            <h1 class="hero-title">Home Credit<br/>Risk Scoring</h1>
            <div class="hero-copy">
                Simulasi scoring calon debitur berbasis model V4. Isi profil calon kreditur,
                sistem akan menghitung estimasi risiko gagal bayar, kategori risiko,
                dan rekomendasi keputusan bisnis.
            </div>
        </div>
        <div class="hero-side">
            <div class="mini-panel-title">Model Snapshot</div>
            <div class="mix-row"><span><span class="dot" style="background:#6147ff"></span>LightGBM</span><strong>70%</strong></div>
            <div class="mix-row"><span><span class="dot" style="background:#4592ff"></span>Logistic Regression</span><strong>30%</strong></div>
            <div class="mix-row"><span><span class="dot" style="background:#22c55e"></span>Calibration</span><strong>Isotonic</strong></div>
            <div class="mix-row"><span><span class="dot" style="background:#ff8a3d"></span>Decision cutoff</span><strong>8.00%</strong></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
    gauge_max_pd = 0.20
    pd_ratio = min(max(result["pd_calibrated"] / gauge_max_pd, 0), 1)
    risk_angle = f"{pd_ratio * 360:.1f}deg"
    low_marker = f"{0.03 / gauge_max_pd * 360:.1f}deg"
    moderate_marker = f"{0.08 / gauge_max_pd * 360:.1f}deg"
    high_marker = f"{0.15 / gauge_max_pd * 360:.1f}deg"
    if result["pd_calibrated"] < 0.03:
        risk_color = "#22c55e"
    elif result["pd_calibrated"] < 0.08:
        risk_color = "#6147ff"
    elif result["pd_calibrated"] < 0.15:
        risk_color = "#f59e0b"
    else:
        risk_color = "#ef4444"
    cutoff_status = (
        "Di bawah batas"
        if result["pd_calibrated"] < result["recommended_pd_cutoff"]
        else "Di atas batas"
    )
    reason_html = "".join(
        f'<div class="reason-chip">● {escape(reason)}</div>'
        for reason in result["reason_codes"]
    )

    st.divider()
    st.markdown('<div class="section-title">Hasil Scoring</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="result-shell">
            <div class="credit-gauge-card">
                <div class="mini-panel-title">Credit Report</div>
                <div class="gauge-ring" style="--risk-angle:{risk_angle};--risk-color:{risk_color};--low-marker:{low_marker};--moderate-marker:{moderate_marker};--high-marker:{high_marker}">
                    <div class="threshold-label threshold-low">3%<span>rendah</span></div>
                    <div class="threshold-label threshold-approve">8%<span>approve</span></div>
                    <div class="threshold-label threshold-high">15%+<span>tinggi</span></div>
                    <div class="gauge-inner">
                        <div class="gauge-value">{pct(result["pd_calibrated"])}</div>
                        <div class="gauge-caption" style="color:{risk_color}">{result["risk_band"]}</div>
                    </div>
                </div>
            </div>
            <div class="result-detail-card">
                <div class="mini-panel-title">Ringkasan Keputusan</div>
                <div class="detail-list">
                    <div class="detail-item"><span>Estimasi risiko gagal bayar</span><span class="detail-value">{pct(result["pd_calibrated"])}</span></div>
                    <div class="detail-item"><span>Kategori risiko applicant</span><span class="detail-value">{result["risk_band"]}</span></div>
                    <div class="detail-item"><span>Rekomendasi keputusan</span><span class="detail-value">{result["business_decision"]}</span></div>
                    <div class="detail-item"><span>Status terhadap batas approve</span><span class="detail-value">{cutoff_status}</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="result-detail-card" style="margin-top:1rem;margin-bottom:1.25rem">
            <div class="mini-panel-title">Alasan Utama</div>
            {reason_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

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
