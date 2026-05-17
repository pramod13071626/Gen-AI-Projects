import os
import json
import pickle
import threading
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
BACKUP_DIR = os.path.join(MODEL_DIR, "backups")

retrain_status = {
    "running": False,
    "last_run": None,
    "results": {},
    "error": None,
}

MODEL_FEATURES = {
    "diabetes": ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'],
    "heart": ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'],
    "kidney": ['age', 'bp', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'bgr', 'bu', 'sc', 'pot', 'wc', 'htn', 'dm', 'cad', 'pe', 'ane'],
    "liver": ['Age', 'Total_Bilirubin', 'Direct_Bilirubin', 'Alkaline_Phosphotase', 'Alamine_Aminotransferase', 'Aspartate_Aminotransferase', 'Total_Protiens', 'Albumin', 'Albumin_and_Globulin_Ratio', 'Gender_Male'],
    "cancer": ['radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean', 'compactness_mean', 'concavity_mean', 'concave points_mean', 'symmetry_mean', 'radius_se', 'perimeter_se', 'area_se', 'compactness_se', 'concavity_se', 'concave points_se', 'fractal_dimension_se', 'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst', 'smoothness_worst', 'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst', 'fractal_dimension_worst'],
}

FIELD_MAPPINGS = {
    "diabetes": {
        'pregnancies': 'Pregnancies', 'glucose': 'Glucose', 'bloodpressure': 'BloodPressure',
        'skinthickness': 'SkinThickness', 'insulin': 'Insulin', 'bmi': 'BMI',
        'dpf': 'DiabetesPedigreeFunction', 'age': 'Age',
    },
    "liver": {
        'age': 'Age', 'total_bilirubin': 'Total_Bilirubin', 'direct_bilirubin': 'Direct_Bilirubin',
        'alkaline_phosphotase': 'Alkaline_Phosphotase', 'alamine_aminotransferase': 'Alamine_Aminotransferase',
        'aspartate_aminotransferase': 'Aspartate_Aminotransferase', 'total_proteins': 'Total_Protiens',
        'albumin': 'Albumin', 'albumin_and_globulin_ratio': 'Albumin_and_Globulin_Ratio',
        'gender': 'Gender_Male',
    },
    "cancer": {
        'concave_points_mean': 'concave points_mean',
        'concave_points_se': 'concave points_se',
        'concave_points_worst': 'concave points_worst',
    },
}


def _extract_features(form_data_json, disease):
    if not form_data_json:
        return None
    try:
        data = json.loads(form_data_json) if isinstance(form_data_json, str) else form_data_json
    except (json.JSONDecodeError, TypeError):
        return None

    features = MODEL_FEATURES.get(disease)
    if not features:
        return None

    field_map = FIELD_MAPPINGS.get(disease, {})
    reverse_map = {v: k for k, v in field_map.items()}

    row = []
    for f in features:
        val = data.get(f) or data.get(reverse_map.get(f, "")) or data.get(f.lower())
        if val is None:
            return None
        try:
            row.append(float(val))
        except (ValueError, TypeError):
            return None
    return row


def _get_db_data(app, disease):
    from models import DiseasePrediction
    with app.app_context():
        preds = DiseasePrediction.query.filter_by(disease_name=disease).all()

    rows = []
    labels = []
    for p in preds:
        row = _extract_features(p.form_data, disease)
        if row and p.prediction_result in ('0', '1'):
            rows.append(row)
            labels.append(int(p.prediction_result))
    return rows, labels


def _retrain_single(app, disease):
    features = MODEL_FEATURES.get(disease)
    if not features:
        return {"status": "skipped", "reason": "no feature config"}

    new_rows, new_labels = _get_db_data(app, disease)

    if len(new_rows) < 5:
        return {"status": "skipped", "reason": f"only {len(new_rows)} samples (need 5+)"}

    model_path = os.path.join(MODEL_DIR, f"{disease}.pkl")
    if not os.path.exists(model_path):
        return {"status": "error", "reason": "model file not found"}

    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"{disease}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
    with open(model_path, 'rb') as f:
        with open(backup_path, 'wb') as bf:
            bf.write(f.read())

    X = np.array(new_rows)
    y = np.array(new_labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=20, random_state=42)
    model.feature_names_in_ = np.array(features)
    model.fit(X_train, y_train)

    accuracy = round(model.score(X_test, y_test) * 100, 2)

    if accuracy < 50:
        return {"status": "rejected", "reason": f"accuracy too low ({accuracy}%)", "samples": len(new_rows)}

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    return {"status": "success", "accuracy": accuracy, "samples": len(new_rows), "backup": backup_path}


def retrain_all(app):
    global retrain_status

    if retrain_status["running"]:
        return False

    def _run():
        global retrain_status
        retrain_status["running"] = True
        retrain_status["error"] = None
        retrain_status["results"] = {}

        try:
            for disease in MODEL_FEATURES:
                retrain_status["results"][disease] = _retrain_single(app, disease)
        except Exception as e:
            retrain_status["error"] = str(e)
        finally:
            retrain_status["running"] = False
            retrain_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    threading.Thread(target=_run, daemon=True).start()
    return True
