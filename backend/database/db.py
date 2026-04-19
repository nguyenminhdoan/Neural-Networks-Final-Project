from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    """Student data model for storing student records."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_term_gpa = db.Column(db.Float, nullable=True)
    second_term_gpa = db.Column(db.Float, nullable=True)
    first_language = db.Column(db.Integer, nullable=True)
    funding = db.Column(db.Integer, nullable=True)
    school = db.Column(db.Integer, nullable=True)
    fast_track = db.Column(db.Integer, nullable=True)
    coop = db.Column(db.Integer, nullable=True)
    residency = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.Integer, nullable=True)
    prev_education = db.Column(db.Integer, nullable=True)
    age_group = db.Column(db.Integer, nullable=True)
    high_school_avg = db.Column(db.Float, nullable=True)
    math_score = db.Column(db.Float, nullable=True)
    english_grade = db.Column(db.Integer, nullable=True)
    first_year_persistence = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'first_term_gpa': self.first_term_gpa,
            'second_term_gpa': self.second_term_gpa,
            'first_language': self.first_language,
            'funding': self.funding,
            'school': self.school,
            'fast_track': self.fast_track,
            'coop': self.coop,
            'residency': self.residency,
            'gender': self.gender,
            'prev_education': self.prev_education,
            'age_group': self.age_group,
            'high_school_avg': self.high_school_avg,
            'math_score': self.math_score,
            'english_grade': self.english_grade,
            'first_year_persistence': self.first_year_persistence,
        }


class PredictionLog(db.Model):
    """Stores prediction history for auditing."""
    __tablename__ = 'prediction_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_type = db.Column(db.String(50), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    prediction_result = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'model_type': self.model_type,
            'input_data': self.input_data,
            'prediction_result': self.prediction_result,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
