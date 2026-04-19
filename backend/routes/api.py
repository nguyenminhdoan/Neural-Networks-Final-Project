"""
REST API Routes following MVC pattern.

Blueprints:
  /api/data      - Data access endpoints
  /api/predict   - Prediction endpoints
  /api/models    - Model information endpoints
  /api/admin     - Admin operations
"""

from flask import Blueprint, request, jsonify
from database.db import db, Student, PredictionLog
from services.data_service import (
    get_data_summary, get_students_paginated,
    get_correlation_data, VARIABLE_LABELS, import_data_to_db,
)

# The prediction service instance is injected from app.py
prediction_service = None


def set_prediction_service(svc):
    global prediction_service
    prediction_service = svc


# ======================================================================
# Data Blueprint
# ======================================================================
data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@data_bp.route('/summary', methods=['GET'])
def data_summary():
    """Get dataset summary statistics."""
    summary = get_data_summary()
    return jsonify(summary)


@data_bp.route('/students', methods=['GET'])
def list_students():
    """Get paginated list of students with optional filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    filters = {}
    if request.args.get('school'):
        filters['school'] = int(request.args['school'])
    if request.args.get('gender'):
        filters['gender'] = int(request.args['gender'])
    if request.args.get('persistence') is not None and request.args.get('persistence') != '':
        filters['persistence'] = int(request.args['persistence'])
    if request.args.get('residency'):
        filters['residency'] = int(request.args['residency'])

    result = get_students_paginated(page, per_page, filters)
    return jsonify(result)


@data_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a single student record."""
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict())


@data_bp.route('/correlation', methods=['GET'])
def correlation():
    """Get correlation matrix for the dataset."""
    data = get_correlation_data()
    return jsonify(data)


@data_bp.route('/labels', methods=['GET'])
def variable_labels():
    """Get human-readable labels for categorical variables."""
    # Convert integer keys to strings for JSON
    labels = {}
    for var, mapping in VARIABLE_LABELS.items():
        labels[var] = {str(k): v for k, v in mapping.items()}
    return jsonify(labels)


# ======================================================================
# Prediction Blueprint
# ======================================================================
predict_bp = Blueprint('predict', __name__, url_prefix='/api/predict')


@predict_bp.route('/persistence', methods=['POST'])
def predict_persistence():
    """Predict first-year persistence for a student."""
    if not prediction_service or not prediction_service.is_ready:
        return jsonify({'error': 'Models not ready'}), 503

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        result = prediction_service.predict_persistence(data)
        return jsonify(result)
    except (KeyError, ValueError) as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400


@predict_bp.route('/gpa', methods=['POST'])
def predict_gpa():
    """Predict second-term GPA for a student."""
    if not prediction_service or not prediction_service.is_ready:
        return jsonify({'error': 'Models not ready'}), 503

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        result = prediction_service.predict_gpa(data)
        return jsonify(result)
    except (KeyError, ValueError) as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400


@predict_bp.route('/atrisk', methods=['POST'])
def predict_atrisk():
    """Predict at-risk status for a student."""
    if not prediction_service or not prediction_service.is_ready:
        return jsonify({'error': 'Models not ready'}), 503

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        result = prediction_service.predict_atrisk(data)
        return jsonify(result)
    except (KeyError, ValueError) as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400


# ======================================================================
# Model Info Blueprint
# ======================================================================
models_bp = Blueprint('models', __name__, url_prefix='/api/models')


@models_bp.route('/metrics', methods=['GET'])
def model_metrics():
    """Get evaluation metrics for all trained models."""
    if not prediction_service:
        return jsonify({'error': 'Service not initialized'}), 503
    return jsonify(prediction_service.get_all_metrics())


@models_bp.route('/features', methods=['GET'])
def model_features():
    """Get feature names used by each model."""
    if not prediction_service:
        return jsonify({'error': 'Service not initialized'}), 503
    return jsonify(prediction_service.get_feature_names())


@models_bp.route('/status', methods=['GET'])
def model_status():
    """Check if models are ready."""
    ready = prediction_service.is_ready if prediction_service else False
    return jsonify({'models_ready': ready})


# ======================================================================
# Admin Blueprint
# ======================================================================
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/retrain', methods=['POST'])
def retrain_models():
    """Re-train all neural network models."""
    if not prediction_service:
        return jsonify({'error': 'Service not initialized'}), 503
    try:
        metrics = prediction_service.train_all()
        return jsonify({'message': 'Models retrained successfully', 'metrics': metrics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/predictions', methods=['GET'])
def prediction_history():
    """Get prediction history log."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = PredictionLog.query.order_by(
        PredictionLog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
    })


@admin_bp.route('/import-data', methods=['POST'])
def reimport_data():
    """Re-import CSV data into the database."""
    from config import Config
    try:
        Student.query.delete()
        db.session.commit()
        count = import_data_to_db(Config.DATA_FILE)
        return jsonify({'message': f'Imported {count} records successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
