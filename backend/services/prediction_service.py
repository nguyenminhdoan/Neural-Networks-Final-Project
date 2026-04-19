"""
Prediction Service - manages model lifecycle (train, load, predict).
"""

import os
import json
import pandas as pd
from models.neural_networks import (
    PersistenceModel, GPAModel, AtRiskModel,
    PERSISTENCE_FEATURES, GPA_FEATURES, AT_RISK_FEATURES,
)
from database.db import db, PredictionLog
from services.data_service import load_csv_data


class PredictionService:
    """Singleton-style service that holds trained model instances."""

    def __init__(self, model_dir='saved_models', data_path=None):
        self.model_dir = model_dir
        self.data_path = data_path
        self.persistence_model = PersistenceModel(model_dir)
        self.gpa_model = GPAModel(model_dir)
        self.atrisk_model = AtRiskModel(model_dir)
        self._models_ready = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self):
        """Try to load saved models; if not found, train from scratch."""
        try:
            self.persistence_model.load()
            self.gpa_model.load()
            self.atrisk_model.load()
            self._models_ready = True
            print('[PredictionService] Models loaded from disk.')
        except Exception as e:
            print(f'[PredictionService] Could not load models ({e}). Training ...')
            self.train_all()

    def train_all(self):
        """Train every model on the CSV dataset and save to disk."""
        if not self.data_path:
            raise RuntimeError('data_path not configured')

        df = load_csv_data(self.data_path)
        print(f'[PredictionService] Loaded {len(df)} records for training.')

        print('[PredictionService] Training persistence model ...')
        p_metrics = self.persistence_model.train(df)
        self.persistence_model.save()
        print(f'  -> accuracy={p_metrics["accuracy"]:.4f}  f1={p_metrics["f1_score"]:.4f}')

        print('[PredictionService] Training GPA model ...')
        g_metrics = self.gpa_model.train(df)
        self.gpa_model.save()
        print(f'  -> R2={g_metrics["r2_score"]:.4f}  MAE={g_metrics["mae"]:.4f}')

        print('[PredictionService] Training at-risk model ...')
        a_metrics = self.atrisk_model.train(df)
        self.atrisk_model.save()
        print(f'  -> accuracy={a_metrics["accuracy"]:.4f}  f1={a_metrics["f1_score"]:.4f}')

        self._models_ready = True
        return {
            'persistence': p_metrics,
            'gpa': g_metrics,
            'at_risk': a_metrics,
        }

    @property
    def is_ready(self):
        return self._models_ready

    # ------------------------------------------------------------------
    # Predictions
    # ------------------------------------------------------------------

    def predict_persistence(self, input_dict):
        features = [float(input_dict[f]) for f in PERSISTENCE_FEATURES]
        result = self.persistence_model.predict(features)
        self._log('persistence', input_dict, result)
        return result

    def predict_gpa(self, input_dict):
        features = [float(input_dict[f]) for f in GPA_FEATURES]
        result = self.gpa_model.predict(features)
        self._log('gpa', input_dict, result)
        return result

    def predict_atrisk(self, input_dict):
        features = [float(input_dict[f]) for f in AT_RISK_FEATURES]
        result = self.atrisk_model.predict(features)
        self._log('at_risk', input_dict, result)
        return result

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_all_metrics(self):
        return {
            'persistence': self.persistence_model.metrics,
            'gpa': self.gpa_model.metrics,
            'at_risk': self.atrisk_model.metrics,
            'models_ready': self._models_ready,
        }

    def get_feature_names(self):
        return {
            'persistence': PERSISTENCE_FEATURES,
            'gpa': GPA_FEATURES,
            'at_risk': AT_RISK_FEATURES,
        }

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log(self, model_type, input_data, result):
        try:
            log = PredictionLog(
                model_type=model_type,
                input_data=json.dumps(input_data),
                prediction_result=json.dumps(result),
                confidence=result.get('probability'),
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()
