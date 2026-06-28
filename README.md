# Home Credit Loan Prediction V4

Portfolio project untuk credit risk scoring berbasis Home Credit dataset.

## Streamlit Product Demo

App demo berada di folder `app/` dan dapat dijalankan dengan:

```powershell
pip install -r app\requirements.txt
streamlit run app\streamlit_app.py
```

App membaca model artifact V4 dari:

```text
app/artifacts/model_artifacts
```

Demo ini menampilkan:

- input calon debitur,
- probability of default,
- risk band,
- rekomendasi bisnis,
- reason codes sederhana,
- responsible AI disclaimer.

Catatan: app ini adalah portfolio decision-support demo, bukan sistem persetujuan kredit otomatis.
