"""
Neural Network Models for Student Data Analysis.

Three models:
1. PersistenceModel  - Binary classification: predict first-year persistence
2. GPAModel          - Regression: predict second-term GPA
3. AtRiskModel       - Binary classification: identify at-risk students (low GPA + non-persistence)
"""

import os
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


# ---------------------------------------------------------------------------
# Helper: prepare data
# ---------------------------------------------------------------------------

def _prepare_dataframe(df, features, target_col):
    """Drop rows with missing values in the required columns and split X/y."""
    cols = features + [target_col]
    subset = df[cols].dropna()
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
            X, y, test_size=0.2, random_state=42, stratify=y,
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
            X, y, test_size=0.2, random_state=42,
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
        subset = df[AT_RISK_FEATURES + ['first_year_persistence']].dropna()
        subset = subset.copy()
        subset['at_risk'] = (
            (subset['first_year_persistence'] == 0) |
            (subset['first_term_gpa'] < 2.0)
        ).astype(int)

        X = subset[AT_RISK_FEATURES].values.astype(np.float32)
        y = subset['at_risk'].values.astype(np.float32)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y,
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
