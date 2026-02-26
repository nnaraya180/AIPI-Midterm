"""
training.py
================================
1. Loads posture_data.csv 
2. trains a Random Forest classifier on pitch/roll angles from all 10 IMU
3. saves a model package

Cite: https://www.datacamp.com/tutorial/random-forests-classifier-python
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report


# -----------------------------
# Configuration
# -----------------------------

CSV_FILE    = "posture_data.csv"
MODEL_FILE  = "model_package.joblib"

# Same segment/column order as data_collection.py
SEGMENTS = [
    "left_thigh", 
    "left_calf",
    "right_thigh", 
    "right_calf",
    "upper_mid_back", 
    "upper_back",
    "right_shoulder", 
    "left_shoulder",
    "lower_mid_back", 
    "lower_back",
]

FEATURE_COLS = [
    f"{seg}_{angle}"
    for seg in SEGMENTS
    for angle in ("pitch", "roll")
]

# Random Forest settings — recycled n_estimators from DataCamp source
N_ESTIMATORS = 100
RANDOM_STATE = 42
TEST_SIZE    = 0.2


# -----------------------------
# Global State
# Recycled: same pattern as wk3day1_lab3.py and wk3day1_lab4.py
# -----------------------------

df         = None
X_train    = None
X_test     = None
y_train    = None
y_test     = None
model      = None
encoder    = None


# -----------------------------
# Steps load, split, train, test
# -----------------------------

def load_data():
    """
    Load CSV into a dataframe and drop rows with missing sensor reads
    """
    global df
    df = pd.read_csv(CSV_FILE)
    before = len(df)
    df = df.dropna(subset=FEATURE_COLS)
    print(f"Loaded {before} rows. {len(df)} remain after dropping incomplete sensor reads.")
    print(f"Label counts:\n{df['label'].value_counts()}\n")


def encode_labels():
    """
    Convert string labels to integers using LabelEncoder.
    Saves the encoder so inference can decode predictions back to strings.
    """
    global df, encoder
    encoder = LabelEncoder()
    df["label_encoded"] = encoder.fit_transform(df["label"])
    print(f"Label encoding: {dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))}\n")


def split_data():
    """
    Split features and encoded labels into train/test sets.
    """
    global df, X_train, X_test, y_train, y_test

    X = df[FEATURE_COLS]
    y = df["label_encoded"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows\n")


def train_model():
    """
    Train a Random Forest classifier.
    """
    global model
    model = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    print(f"Trained Random Forest with {N_ESTIMATORS} trees.\n")


def evaluate_model():
    """
    Print accuracy and a per-label breakdown using classification_report.
    """
    preds = model.predict(X_test)
    accuracy = (preds == y_test).mean()
    print(f"Accuracy: {accuracy:.3f}\n")
    print("Per-label breakdown:")
    print(classification_report(y_test, preds, target_names=encoder.classes_))


def print_feature_importances():
    """
    Print which body segments and angles the model relies on most.
    """
    importances = zip(FEATURE_COLS, model.feature_importances_)
    ranked = sorted(importances, key=lambda x: x[1], reverse=True)
    print("Top 10 most important features:")
    for feat, score in ranked[:10]:
        print(f"  {feat:<30}: {score:.4f}")
    print()


def save_model_package():
    """
    Bundle the model, feature columns, and label encoder into one object and save.
    """
    package = {
        "model":        model,
        "feature_cols": FEATURE_COLS,
        "encoder":      encoder,
    }
    joblib.dump(package, MODEL_FILE)
    print(f"Model package saved to {MODEL_FILE}\n")


# -----------------------------
# Menu
# Recycled: same structure as all class labs
# -----------------------------

def print_menu():
    print("\nMenu:")
    print(f"  1) Load {CSV_FILE}")
    print("  2) Encode labels")
    print("  3) Train/test split")
    print("  4) Train Random Forest")
    print("  5) Evaluate model")
    print("  6) Print feature importances")
    print(f"  7) Save model package ({MODEL_FILE})")
    print("  8) Quit")


def main():
    """
    Step through the full training pipeline in order.
    Recycled: same guard pattern as wk3day1_lab3.py — each step checks
    that the previous step has been completed before running.
    """
    print("Posture Coach — Model Training\n")

    while True:
        print_menu()
        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            try:
                load_data()
            except FileNotFoundError:
                print(f"ERROR: {CSV_FILE} not found.\n")

        elif choice == "2":
            if df is None:
                print("\nLoad data first (option 1).\n")
                continue
            encode_labels()

        elif choice == "3":
            if encoder is None:
                print("\nEncode labels first (option 2).\n")
                continue
            split_data()

        elif choice == "4":
            if X_train is None:
                print("\nSplit data first (option 3).\n")
                continue
            train_model()

        elif choice == "5":
            if model is None:
                print("\nTrain the model first (option 4).\n")
                continue
            evaluate_model()

        elif choice == "6":
            if model is None:
                print("\nTrain the model first (option 4).\n")
                continue
            print_feature_importances()

        elif choice == "7":
            if model is None:
                print("\nTrain the model first (option 4).\n")
                continue
            save_model_package()

        elif choice == "8":
            print("Done.")
            break

        else:
            print("\nInvalid choice. Pick 1-8.\n")


if __name__ == "__main__":
    main()