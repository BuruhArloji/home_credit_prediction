# Home Credit Risk Scoring Streamlit Demo

Demo ini mengubah notebook V4 menjadi product-style credit risk scoring app.

## Cara Menjalankan

1. Jalankan notebook V4 sampai cell `SAVE MODEL DAN FITUR`.
2. Pastikan folder artifact tersedia, contoh:

```powershell
D:\home-credit-data\model_artifacts
```

3. Install dependency:

```powershell
pip install -r app\requirements.txt
```

4. Jalankan Streamlit:

```powershell
streamlit run app\streamlit_app.py
```

Jika artifact disimpan di folder lain:

```powershell
$env:MODEL_ARTIFACT_DIR="C:\path\to\model_artifacts"
streamlit run app\streamlit_app.py
```

## Catatan

- App ini memakai model artifact V4 yang sudah diekspor dari notebook.
- Input user disederhanakan agar cocok sebagai portfolio demo.
- Fitur yang tidak diisi user diberi default aman agar shape tetap sesuai dengan 1.647 fitur model.
- Output adalah decision-support demo, bukan automated credit approval system.
