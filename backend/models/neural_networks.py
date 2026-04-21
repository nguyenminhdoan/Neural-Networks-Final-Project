"""
Neural Network Models for Student Data Analysis.

Four models:
1. PersistenceModel      - Binary classification: predict first-year persistence
2. GPAModel              - Regression: predict second-term GPA from HS + 1st term
3. AtRiskModel           - Binary classification: identify at-risk students
4. StackedAcademicModel  - Regression stage-2: HS + 1st + 2nd term GPA -> overall score
"""

import os
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_squared_error, mean_absolute_error, r2_score,
)
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks
import joblib

# Reproducibility across runs and demos
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Columns treated as numeric (use median imputation);
# everything else in the features list is treated as categorical (mode imputation).
NUMERIC_COLS = {
    'first_term_gpa', 'second_term_gpa',
    'high_school_avg', 'math_score',
}


# ---------------------------------------------------------------------------
# Feature groups
# ---------------------------------------------------------------------------

PERSISTENCE_FEATURES = [
    'first_term_gpa', 'second_term_gpa', 'first_language', 'funding',
    'school', 'fast_track', 'coop', 'residency', 'gender',
    'prev_education', 'age_group', 'high_school_avg', 'math_score',
    'english_grade',
]

GPA_FEATURES = [
    'first_term_gpa', 'first_language', 'funding', 'school', 'fast_track',
    'coop', 'residency', 'gender', 'prev_education', 'age_group',
    'high_school_avg', 'math_score', 'english_grade',
]

AT_RISK_FEATURES = [
    'first_term_gpa', 'first_language', 'funding', 'school', 'fast_track',
    'coop', 'residency', 'gender', 'prev_education', 'age_group',
    'high_school_avg', 'math_score', 'english_grade',
]

# Stage-2 regression features: HS scores + 1st term GPA + 2nd term GPA + demographics.
# Target is an "academic performance score" = mean of 1st and 2nd term GPAs.
STACKED_FEATURES = [
    'first_term_gpa', 'second_term_gpa',
    'high_school_avg', 'math_score', 'english_grade',
    'first_language', 'funding', 'school', 'fast_track',
    'coop', 'residency', 'gender', 'prev_education', 'age_group',
]


# ---------------------------------------------------------------------------
# Helper: prepare data
# ---------------------------------------------------------------------------

def _prepare_dataframe(df, features, target_col):
    """
    Build X/y for training:
      - drop only rows where the target is missing (can't learn without a label),
      - impute missing feature values (median for numeric, mode for categorical)
        so we keep the ~1,400 rows of the dataset instead of ~500.
    """
    subset = df[features + [target_col]].copy()
    subset = subset.dropna(subset=[target_col])

    for col in features:
        if subset[col].isna().any():
            if col in NUMERIC_COLS:
                fill_value = subset[col].median()
            else:
                mode = subset[col].mode(dropna=True)
                fill_value = mode.iloc[0] if not mode.empty else 0
            subset[col] = subset[col].fillna(fill_value)

    X = subset[features].values.astype(np.float32)
    y = subset[target_col].values.astype(np.float32)
    return X, y


# ---------------------------------------------------------------------------
# 1. Persistence Classifier
# ---------------------------------------------------------------------------

class PersistenceModel:
    """Binary classifier predicting first-year persistence (0/1)."""

    def __init__(self, model_dir='saved_models'):
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.history = None
        self.metrics = {}

    def _build_model(self, input_dim):
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,),
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu',
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid'),
        ])
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy'],
        )
        return model

    def train(self, df, epochs=100, batch_size=32, validation_split=0.2):
        X, y = _prepare_dataframe(df, PERSISTENCE_FEATURES, 'first_year_persistence')
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=SEED, stratify=y,
        )

        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        # Handle class imbalance
        n_pos = y_train.sum()
        n_neg = len(y_train) - n_pos
        class_weight = {0: len(y_train) / (2 * n_neg), 1: len(y_train) / (2 * n_pos)}

        self.model = self._build_model(X_train.shape[1])

        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=15, restore_best_weights=True,
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6,
        )

        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            class_weight=class_weight,
            callbacks=[early_stop, reduce_lr],
            verbose=0,
        )

        # Evaluate
        y_pred_prob = self.model.predict(X_test, verbose=0).flatten()
        y_pred = (y_pred_prob >= 0.5).astype(int)

        cm = confusion_matrix(y_test, y_pred)
        self.metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'confusion_matrix': cm.tolist(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'epochs_trained': len(self.history.history['loss']),
            'training_history': {
                'loss': [float(v) for v in self.history.history['loss']],
                'val_loss': [float(v) for v in self.history.history['val_loss']],
                'accuracy': [float(v) for v in self.history.history['accuracy']],
                'val_accuracy': [float(v) for v in self.history.history['val_accuracy']],
            },
        }
        return self.metrics

    def predict(self, input_data):
        if self.model is None or self.scaler is None:
            raise RuntimeError('Model not trained or loaded')
        X = np.array(input_data, dtype=np.float32).reshape(1, -1)
        X = self.scaler.transform(X)
        prob = float(self.model.predict(X, verbose=0).flatten()[0])
        return {
            'prediction': int(prob >= 0.5),
            'probability': round(prob, 4),
            'label': 'Will Persist' if prob >= 0.5 else 'Will Not Persist',
        }

    def save(self):
        os.makedirs(self.model_dir, exist_ok=True)
        self.model.save(os.path.join(self.model_dir, 'persistence_model.keras'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'persistence_scaler.pkl'))
        joblib.dump(self.metrics, os.path.join(self.model_dir, 'persistence_metrics.pkl'))

    def load(self):
        self.model = keras.models.load_model(
            os.path.join(self.model_dir, 'persistence_model.keras'))
        self.scaler = joblib.load(os.path.join(self.model_dir, 'persistence_scaler.pkl'))
        self.metrics = joblib.load(os.path.join(self.model_dir, 'persistence_metrics.pkl'))


# ---------------------------------------------------------------------------
# 2. GPA Regression Model
# ---------------------------------------------------------------------------

class GPAModel:
    """Regression model predicting second-term GPA."""

    def __init__(self, model_dir='saved_models'):
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.history = None
        self.metrics = {}

    def _build_model(self, input_dim):
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,),
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu',
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.1),
            layers.Dense(1, activation='linear'),
        ])
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae'],
        )
        return model

    def train(self, df, epochs=150, batch_size=32, validation_split=0.2):
        X, y = _prepare_dataframe(df, GPA_FEATURES, 'second_term_gpa')
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=SEED,
        )

        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        self.model = self._build_model(X_train.shape[1])

        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=20, restore_best_weights=True,
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=7, min_lr=1e-6,
        )

        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop, reduce_lr],
            verbose=0,
        )

        y_pred = self.model.predict(X_test, verbose=0).flatten()

        self.metrics = {
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'r2_score': float(r2_score(y_test, y_pred)),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'epochs_trained': len(self.history.history['loss']),
            'training_history': {
                'loss': [float(v) for v in self.history.history['loss']],
                'val_loss': [float(v) for v in self.history.history['val_loss']],
                'mae': [float(v) for v in self.history.history['mae']],
                'val_mae': [float(v) for v in self.history.history['val_mae']],
            },
        }
        return self.metrics

    def predict(self, input_data):
        if self.model is None or self.scaler is None:
            raise RuntimeError('Model not trained or loaded')
        X = np.array(input_data, dtype=np.float32).reshape(1, -1)
        X = self.scaler.transform(X)
        prediction = float(self.model.predict(X, verbose=0).flatten()[0])
        prediction = max(0.0, min(4.5, prediction))  # clamp to GPA range
        return {
            'predicted_gpa': round(prediction, 2),
        }

    def save(self):
        os.makedirs(self.model_dir, exist_ok=True)
        self.model.save(os.path.join(self.model_dir, 'gpa_model.keras'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'gpa_scaler.pkl'))
        joblib.dump(self.metrics, os.path.join(self.model_dir, 'gpa_metrics.pkl'))

    def load(self):
        self.model = keras.models.load_model(
            os.path.join(self.model_dir, 'gpa_model.keras'))
        self.scaler = joblib.load(os.path.join(self.model_dir, 'gpa_scaler.pkl'))
        self.metrics = joblib.load(os.path.join(self.model_dir, 'gpa_metrics.pkl'))


# ---------------------------------------------------------------------------
# 3. At-Risk Student Classifier
# ---------------------------------------------------------------------------

class AtRiskModel:
    """
    Binary classifier identifying at-risk students.
    A student is at-risk if first_year_persistence == 0 OR first_term_gpa < 2.0.
    """

    def __init__(self, model_dir='saved_models'):
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.history = None
        self.metrics = {}

    def _build_model(self, input_dim):
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,),
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu',
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid'),
        ])
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy'],
        )
        return model

    def train(self, df, epochs=100, batch_size=32, validation_split=0.2):
        # Build at-risk label: at_risk = 1 if persistence==0 OR first_term_gpa < 2.0
        # We need both first_term_gpa and first_year_persistence non-null to compute the label.
        subset = df.copy()
        subset = subset.dropna(subset=['first_year_persistence', 'first_term_gpa'])
        subset['at_risk'] = (
            (subset['first_year_persistence'] == 0) |
            (subset['first_term_gpa'] < 2.0)
        ).astype(int)

        X, y = _prepare_dataframe(subset, AT_RISK_FEATURES, 'at_risk')

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=SEED, stratify=y,
        )

        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        n_pos = y_train.sum()
        n_neg = len(y_train) - n_pos
        class_weight = {0: len(y_train) / (2 * n_neg), 1: len(y_train) / (2 * n_pos)}

        self.model = self._build_model(X_train.shape[1])

        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=15, restore_best_weights=True,
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6,
        )

        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            class_weight=class_weight,
            callbacks=[early_stop, reduce_lr],
            verbose=0,
        )

        y_pred_prob = self.model.predict(X_test, verbose=0).flatten()
        y_pred = (y_pred_prob >= 0.5).astype(int)

        cm = confusion_matrix(y_test, y_pred)
        self.metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'confusion_matrix': cm.tolist(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'epochs_trained': len(self.history.history['loss']),
            'training_history': {
                'loss': [float(v) for v in self.history.history['loss']],
                'val_loss': [float(v) for v in self.history.history['val_loss']],
                'accuracy': [float(v) for v in self.history.history['accuracy']],
                'val_accuracy': [float(v) for v in self.history.history['val_accuracy']],
            },
        }
        return self.metrics

    def predict(self, input_data):
        if self.model is None or self.scaler is None:
            raise RuntimeError('Model not trained or loaded')
        X = np.array(input_data, dtype=np.float32).reshape(1, -1)
        X = self.scaler.transform(X)
        prob = float(self.model.predict(X, verbose=0).flatten()[0])
        risk_level = 'High Risk' if prob >= 0.7 else ('Medium Risk' if prob >= 0.4 else 'Low Risk')
        return {
            'prediction': int(prob >= 0.5),
            'probability': round(prob, 4),
            'risk_level': risk_level,
            'label': 'At Risk' if prob >= 0.5 else 'Not At Risk',
        }

    def save(self):
        os.makedirs(self.model_dir, exist_ok=True)
        self.model.save(os.path.join(self.model_dir, 'atrisk_model.keras'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'atrisk_scaler.pkl'))
        joblib.dump(self.metrics, os.path.join(self.model_dir, 'atrisk_metrics.pkl'))

    def load(self):
        self.model = keras.models.load_model(
            os.path.join(self.model_dir, 'atrisk_model.keras'))
        self.scaler = joblib.load(os.path.join(self.model_dir, 'atrisk_scaler.pkl'))
        self.metrics = joblib.load(os.path.join(self.model_dir, 'atrisk_metrics.pkl'))


# ---------------------------------------------------------------------------
# 4. Stacked Academic Performance Regression
# ---------------------------------------------------------------------------

class StackedAcademicModel:
    """
    Stage-2 regression: HS scores + 1st term GPA + 2nd term GPA + demographics
    -> overall academic performance score (mean of 1st and 2nd term GPA).

    Used in a pipeline where Stage-1 (GPAModel) first predicts 2nd term GPA
    from 1st term GPA + HS scores, and Stage-2 consumes both GPAs to produce
    a final academic performance estimate.
    """

    def __init__(self, model_dir='saved_models'):
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.history = None
        self.metrics = {}

    def _build_model(self, input_dim):
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,),
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu',
                         kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.1),
            layers.Dense(1, activation='linear'),
        ])
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae'],
        )
        return model

    def train(self, df, epochs=150, batch_size=32, validation_split=0.2):
        # Target is the mean of the two term GPAs (must be known to label a row).
        subset = df.copy()
        subset = subset.dropna(subset=['first_term_gpa', 'second_term_gpa'])
        subset['academic_score'] = (
            subset['first_term_gpa'] + subset['second_term_gpa']
        ) / 2.0

        X, y = _prepare_dataframe(subset, STACKED_FEATURES, 'academic_score')

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=SEED,
        )

        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        self.model = self._build_model(X_train.shape[1])

        early_stop = callbacks.EarlyStopping(
            monitor='val_loss', patience=20, restore_best_weights=True,
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=7, min_lr=1e-6,
        )

        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop, reduce_lr],
            verbose=0,
        )

        y_pred = self.model.predict(X_test, verbose=0).flatten()

        self.metrics = {
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'r2_score': float(r2_score(y_test, y_pred)),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'epochs_trained': len(self.history.history['loss']),
            'training_history': {
                'loss': [float(v) for v in self.history.history['loss']],
                'val_loss': [float(v) for v in self.history.history['val_loss']],
                'mae': [float(v) for v in self.history.history['mae']],
                'val_mae': [float(v) for v in self.history.history['val_mae']],
            },
        }
        return self.metrics

    def predict(self, input_data):
        if self.model is None or self.scaler is None:
            raise RuntimeError('Model not trained or loaded')
        X = np.array(input_data, dtype=np.float32).reshape(1, -1)
        X = self.scaler.transform(X)
        prediction = float(self.model.predict(X, verbose=0).flatten()[0])
        prediction = max(0.0, min(4.5, prediction))
        return {
            'academic_score': round(prediction, 2),
        }

    def save(self):
        os.makedirs(self.model_dir, exist_ok=True)
        self.model.save(os.path.join(self.model_dir, 'stacked_model.keras'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'stacked_scaler.pkl'))
        joblib.dump(self.metrics, os.path.join(self.model_dir, 'stacked_metrics.pkl'))

    def load(self):
        self.model = keras.models.load_model(
            os.path.join(self.model_dir, 'stacked_model.keras'))
        self.scaler = joblib.load(os.path.join(self.model_dir, 'stacked_scaler.pkl'))
        self.metrics = joblib.load(os.path.join(self.model_dir, 'stacked_metrics.pkl'))


# ---------------------------------------------------------------------------
# Standalone entry point: `python models/neural_networks.py`
# Trains all four models on Student data.csv and saves them to ../saved_models.
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train all neural-network models on Student data.csv')
    parser.add_argument('--data', default=None, help='Path to Student data.csv')
    parser.add_argument('--out', default=None, help='Directory to save trained models')
    args = parser.parse_args()

    here = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.abspath(os.path.join(here, '..'))
    project_dir = os.path.abspath(os.path.join(backend_dir, '..'))

    data_path = args.data or os.path.join(project_dir, 'Student data.csv')
    out_dir = args.out or os.path.join(backend_dir, 'saved_models')

    if not os.path.isfile(data_path):
        raise SystemExit(f'Dataset not found at {data_path}')

    # Import here to avoid circular import at module load time.
    import sys
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from services.data_service import load_csv_data

    print(f'[train] Loading data from: {data_path}')
    df = load_csv_data(data_path)
    print(f'[train] {len(df)} rows loaded. Saving models to: {out_dir}')

    print('\n[train] === Persistence ===')
    m = PersistenceModel(out_dir); met = m.train(df); m.save()
    print(f'  samples={met["training_samples"]}/{met["test_samples"]}  '
          f'acc={met["accuracy"]:.4f}  f1={met["f1_score"]:.4f}')

    print('\n[train] === GPA ===')
    m = GPAModel(out_dir); met = m.train(df); m.save()
    print(f'  samples={met["training_samples"]}/{met["test_samples"]}  '
          f'R2={met["r2_score"]:.4f}  MAE={met["mae"]:.4f}')

    print('\n[train] === At-Risk ===')
    m = AtRiskModel(out_dir); met = m.train(df); m.save()
    print(f'  samples={met["training_samples"]}/{met["test_samples"]}  '
          f'acc={met["accuracy"]:.4f}  f1={met["f1_score"]:.4f}')

    print('\n[train] === Stacked Academic ===')
    m = StackedAcademicModel(out_dir); met = m.train(df); m.save()
    print(f'  samples={met["training_samples"]}/{met["test_samples"]}  '
          f'R2={met["r2_score"]:.4f}  MAE={met["mae"]:.4f}')

    print('\n[train] All models trained and saved.')
