"""
Main Flask Application - Entry point for the backend API.

Architecture: MVC pattern
  - Models:      database/db.py, models/neural_networks.py
  - Views:       routes/api.py (REST endpoints)
  - Controllers: services/ (business logic)
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.db import db, Student
from services.data_service import import_data_to_db
from services.prediction_service import PredictionService
from routes.api import data_bp, predict_bp, models_bp, admin_bp, set_prediction_service


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for React frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(data_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(admin_bp)

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'message': 'Student Analytics API is running'})

    with app.app_context():
        # Create tables
        db.create_all()

        # Import data if DB is empty
        if Student.query.count() == 0:
            print('[App] Importing student data from CSV ...')
            count = import_data_to_db(Config.DATA_FILE)
            print(f'[App] Imported {count} student records.')

        # Initialize prediction service
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        svc = PredictionService(
            model_dir=Config.MODEL_DIR,
            data_path=Config.DATA_FILE,
        )
        svc.initialize()
        set_prediction_service(svc)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
