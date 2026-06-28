from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


def _artifact_candidates() -> list[Path]:
    candidates: list[Path] = []
    env_path = os.environ.get("MODEL_ARTIFACT_DIR")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            Path(__file__).resolve().parent / "artifacts" / "model_artifacts",
            Path(r"D:\home-credit-data\model_artifacts"),
        ]
    )
    return candidates


@dataclass
class CreditRiskArtifacts:
    artifact_dir: Path
    model_lgbm: Any
    model_logreg: Any
    calibrator: Any
    feature_names: list[str]
    categorical_columns: list[str]
    numeric_columns: list[str]
    ensemble_weight_lgbm: float
    model_threshold: float
    recommended_pd_cutoff: float


def find_artifact_dir() -> Path | None:
    for candidate in _artifact_candidates():
        if candidate.exists():
            return candidate
    return None


def load_artifacts(artifact_dir: Path | None = None) -> CreditRiskArtifacts:
    artifact_dir = artifact_dir or find_artifact_dir()
    if artifact_dir is None:
        raise FileNotFoundError(
            "Model artifacts tidak ditemukan. Jalankan notebook sampai cell 'SAVE MODEL DAN FITUR' "
            "atau set environment variable MODEL_ARTIFACT_DIR."
        )

    required_files = [
        "model_lgbm_baseline.pkl",
        "model_logreg_benchmark.pkl",
        "isotonic_calibrator.pkl",
        "lgbm_feature_names.pkl",
        "categorical_columns.pkl",
        "numeric_columns.pkl",
        "best_ensemble_weight_lgbm.pkl",
        "best_threshold_ensemble.pkl",
        "recommended_pd_cutoff.pkl",
    ]
    missing = [name for name in required_files if not (artifact_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Artifact belum lengkap di {artifact_dir}: {missing}")

    return CreditRiskArtifacts(
        artifact_dir=artifact_dir,
        model_lgbm=joblib.load(artifact_dir / "model_lgbm_baseline.pkl"),
        model_logreg=joblib.load(artifact_dir / "model_logreg_benchmark.pkl"),
        calibrator=joblib.load(artifact_dir / "isotonic_calibrator.pkl"),
        feature_names=joblib.load(artifact_dir / "lgbm_feature_names.pkl"),
        categorical_columns=joblib.load(artifact_dir / "categorical_columns.pkl"),
        numeric_columns=joblib.load(artifact_dir / "numeric_columns.pkl"),
        ensemble_weight_lgbm=float(joblib.load(artifact_dir / "best_ensemble_weight_lgbm.pkl")),
        model_threshold=float(joblib.load(artifact_dir / "best_threshold_ensemble.pkl")),
        recommended_pd_cutoff=float(joblib.load(artifact_dir / "recommended_pd_cutoff.pkl")),
    )


def build_feature_row(user_input: dict[str, Any], artifacts: CreditRiskArtifacts) -> pd.DataFrame:
    row: dict[str, Any] = {feature: 0 for feature in artifacts.feature_names}

    for col in artifacts.categorical_columns:
        if col in row:
            row[col] = "Unknown"

    row.update(_derive_application_features(user_input))
    row.update(_derive_credit_history_features(user_input))

    frame = pd.DataFrame([row], columns=artifacts.feature_names)

    for col in artifacts.numeric_columns:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce").fillna(0)

    for col in artifacts.categorical_columns:
        if col in frame.columns:
            frame[col] = frame[col].fillna("Unknown").astype("category")

    return frame


def predict_credit_risk(user_input: dict[str, Any], artifacts: CreditRiskArtifacts) -> dict[str, Any]:
    features = build_feature_row(user_input, artifacts)

    lgbm_pd = float(artifacts.model_lgbm.predict_proba(features)[:, 1][0])
    logreg_pd = float(artifacts.model_logreg.predict_proba(features)[:, 1][0])
    raw_pd = (
        artifacts.ensemble_weight_lgbm * lgbm_pd
        + (1 - artifacts.ensemble_weight_lgbm) * logreg_pd
    )
    calibrated_pd = float(artifacts.calibrator.transform(np.asarray([raw_pd]))[0])

    business_decision = decision_from_pd(calibrated_pd, artifacts.recommended_pd_cutoff)
    model_flag = int(raw_pd >= artifacts.model_threshold)

    return {
        "pd_raw": raw_pd,
        "pd_calibrated": calibrated_pd,
        "pd_lgbm": lgbm_pd,
        "pd_logreg": logreg_pd,
        "risk_band": risk_band(calibrated_pd),
        "business_decision": business_decision,
        "model_flag": model_flag,
        "model_threshold": artifacts.model_threshold,
        "recommended_pd_cutoff": artifacts.recommended_pd_cutoff,
        "reason_codes": reason_codes(user_input),
        "feature_frame": features,
    }


def decision_from_pd(pd_value: float, cutoff: float) -> str:
    if pd_value < cutoff * 0.75:
        return "Disetujui"
    if pd_value < cutoff * 1.35:
        return "Perlu Review Manual"
    return "Tidak Disarankan / Review Risiko Tinggi"


def risk_band(pd_value: float) -> str:
    if pd_value < 0.03:
        return "Risiko Rendah"
    if pd_value < 0.08:
        return "Risiko Sedang"
    if pd_value < 0.15:
        return "Risiko Tinggi"
    return "Risiko Sangat Tinggi"


def reason_codes(user_input: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    income = max(float(user_input.get("AMT_INCOME_TOTAL", 0)), 1)
    credit = float(user_input.get("AMT_CREDIT", 0))
    annuity = float(user_input.get("AMT_ANNUITY", 0))
    ext2 = user_input.get("EXT_SOURCE_2")
    ext3 = user_input.get("EXT_SOURCE_3")

    if credit / income > 4:
        reasons.append("Credit-to-income ratio tinggi")
    if annuity / income > 0.35:
        reasons.append("Annuity-to-income ratio tinggi")
    if float(user_input.get("CREDIT_DAY_OVERDUE", 0)) > 0:
        reasons.append("Ada indikasi keterlambatan pembayaran historis")
    if float(user_input.get("ADV_CC_UTILIZATION", 0)) > 0.75:
        reasons.append("Utilization kartu kredit tinggi")
    if ext2 is not None and float(ext2) < 0.35:
        reasons.append("External score 2 relatif rendah")
    if ext3 is not None and float(ext3) < 0.35:
        reasons.append("External score 3 relatif rendah")
    if not reasons:
        reasons.append("Tidak ada red flag utama dari input sederhana")
    return reasons


def _derive_application_features(user_input: dict[str, Any]) -> dict[str, Any]:
    age = int(user_input.get("AGE_YEARS", 35))
    employment_years = float(user_input.get("EMPLOYMENT_YEARS", 5))
    income = float(user_input.get("AMT_INCOME_TOTAL", 180_000))
    credit = float(user_input.get("AMT_CREDIT", 600_000))
    annuity = float(user_input.get("AMT_ANNUITY", 30_000))
    goods_price = float(user_input.get("AMT_GOODS_PRICE", credit))

    values = {
        "NAME_CONTRACT_TYPE": user_input.get("NAME_CONTRACT_TYPE", "Cash loans"),
        "CODE_GENDER": user_input.get("CODE_GENDER", "F"),
        "FLAG_OWN_CAR": user_input.get("FLAG_OWN_CAR", "N"),
        "FLAG_OWN_REALTY": user_input.get("FLAG_OWN_REALTY", "Y"),
        "CNT_CHILDREN": int(user_input.get("CNT_CHILDREN", 0)),
        "AMT_INCOME_TOTAL": income,
        "AMT_CREDIT": credit,
        "AMT_ANNUITY": annuity,
        "AMT_GOODS_PRICE": goods_price,
        "NAME_INCOME_TYPE": user_input.get("NAME_INCOME_TYPE", "Working"),
        "NAME_EDUCATION_TYPE": user_input.get("NAME_EDUCATION_TYPE", "Secondary / secondary special"),
        "NAME_FAMILY_STATUS": user_input.get("NAME_FAMILY_STATUS", "Married"),
        "NAME_HOUSING_TYPE": user_input.get("NAME_HOUSING_TYPE", "House / apartment"),
        "OCCUPATION_TYPE": user_input.get("OCCUPATION_TYPE", "Laborers"),
        "DAYS_BIRTH": -365 * age,
        "DAYS_EMPLOYED": -365 * employment_years,
        "DAYS_REGISTRATION": -365 * float(user_input.get("REGISTRATION_YEARS", 5)),
        "EXT_SOURCE_1": float(user_input.get("EXT_SOURCE_1", 0.5)),
        "EXT_SOURCE_2": float(user_input.get("EXT_SOURCE_2", 0.5)),
        "EXT_SOURCE_3": float(user_input.get("EXT_SOURCE_3", 0.5)),
        "CNT_FAM_MEMBERS": int(user_input.get("CNT_FAM_MEMBERS", 2)),
    }

    values["CREDIT_INCOME_RATIO"] = credit / income if income else 0
    values["ANNUITY_INCOME_RATIO"] = annuity / income if income else 0
    values["CREDIT_GOODS_RATIO"] = credit / goods_price if goods_price else 0
    values["ANNUITY_CREDIT_RATIO"] = annuity / credit if credit else 0
    return values


def _derive_credit_history_features(user_input: dict[str, Any]) -> dict[str, Any]:
    overdue = float(user_input.get("CREDIT_DAY_OVERDUE", 0))
    cc_util = float(user_input.get("ADV_CC_UTILIZATION", 0.35))
    late_rate = float(user_input.get("ADV_INST_LATE_PAYMENT_RATE", 0))

    return {
        "CREDIT_DAY_OVERDUE": overdue,
        "ADV_BUREAU_3M_DPD_GT0_COUNT": int(overdue > 0),
        "ADV_BUREAU_6M_DPD_GT0_COUNT": int(overdue > 0),
        "ADV_BUREAU_12M_DPD_GT0_COUNT": int(overdue > 0),
        "ADV_BUREAU_3M_MAX_DPD": overdue,
        "ADV_BUREAU_6M_MAX_DPD": overdue,
        "ADV_BUREAU_12M_MAX_DPD": overdue,
        "ADV_INST_3M_LATE_PAYMENT_RATE": late_rate,
        "ADV_INST_6M_LATE_PAYMENT_RATE": late_rate,
        "ADV_INST_12M_LATE_PAYMENT_RATE": late_rate,
        "ADV_CC_3M_UTILIZATION_MEAN": cc_util,
        "ADV_CC_6M_UTILIZATION_MEAN": cc_util,
        "ADV_CC_12M_UTILIZATION_MEAN": cc_util,
        "ADV_CC_UTILIZATION": cc_util,
    }
