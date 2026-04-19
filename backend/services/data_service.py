import pandas as pd
import numpy as np
from database.db import db, Student


COLUMN_NAMES = [
    'first_term_gpa', 'second_term_gpa', 'first_language', 'funding',
    'school', 'fast_track', 'coop', 'residency', 'gender',
    'prev_education', 'age_group', 'high_school_avg', 'math_score',
    'english_grade', 'first_year_persistence'
]

# Human-readable labels for categorical variables
VARIABLE_LABELS = {
    'first_language': {1: 'English', 2: 'French', 3: 'Other'},
    'funding': {
        1: 'Apprentice_PS', 2: 'GPOG_FT', 3: 'Intl Offshore',
        4: 'Intl Regular', 5: 'Intl Transfer', 6: 'Joint Program Ryerson',
        7: 'Joint Program UTSC', 8: 'Second Career Program', 9: 'WSIB'
    },
    'school': {
        1: 'Advancement', 2: 'Business', 3: 'Communications',
        4: 'Community & Health', 5: 'Hospitality', 6: 'Engineering',
        7: 'Transportation'
    },
    'fast_track': {1: 'Yes', 2: 'No'},
    'coop': {1: 'Yes', 2: 'No'},
    'residency': {1: 'Domestic', 2: 'International'},
    'gender': {1: 'Female', 2: 'Male', 3: 'Neutral'},
    'prev_education': {1: 'High School', 2: 'Post-Secondary'},
    'age_group': {
        1: '0-18', 2: '19-20', 3: '21-25', 4: '26-30', 5: '31-35',
        6: '36-40', 7: '41-50', 8: '51-60', 9: '61-65', 10: '66+'
    },
    'english_grade': {
        1: 'Level-130', 2: 'Level-131', 3: 'Level-140', 4: 'Level-141',
        5: 'Level-150', 6: 'Level-151', 7: 'Level-160', 8: 'Level-161',
        9: 'Level-170', 10: 'Level-171', 11: 'Level-180'
    },
    'first_year_persistence': {0: 'Did not persist', 1: 'Persisted'},
}


def load_csv_data(filepath):
    """Load and parse the student data CSV file."""
    df = pd.read_csv(
        filepath,
        skiprows=24,
        header=None,
        names=COLUMN_NAMES,
        na_values=['?'],
    )
    return df


def import_data_to_db(filepath):
    """Import CSV data into the SQLite database."""
    df = load_csv_data(filepath)
    count = 0

    for _, row in df.iterrows():
        student = Student(
            first_term_gpa=row['first_term_gpa'] if pd.notna(row['first_term_gpa']) else None,
            second_term_gpa=row['second_term_gpa'] if pd.notna(row['second_term_gpa']) else None,
            first_language=int(row['first_language']) if pd.notna(row['first_language']) else None,
            funding=int(row['funding']) if pd.notna(row['funding']) else None,
            school=int(row['school']) if pd.notna(row['school']) else None,
            fast_track=int(row['fast_track']) if pd.notna(row['fast_track']) else None,
            coop=int(row['coop']) if pd.notna(row['coop']) else None,
            residency=int(row['residency']) if pd.notna(row['residency']) else None,
            gender=int(row['gender']) if pd.notna(row['gender']) else None,
            prev_education=int(row['prev_education']) if pd.notna(row['prev_education']) else None,
            age_group=int(row['age_group']) if pd.notna(row['age_group']) else None,
            high_school_avg=row['high_school_avg'] if pd.notna(row['high_school_avg']) else None,
            math_score=row['math_score'] if pd.notna(row['math_score']) else None,
            english_grade=int(row['english_grade']) if pd.notna(row['english_grade']) else None,
            first_year_persistence=int(row['first_year_persistence']) if pd.notna(row['first_year_persistence']) else None,
        )
        db.session.add(student)
        count += 1

    db.session.commit()
    return count


def get_data_summary():
    """Return summary statistics about the dataset."""
    students = Student.query.all()
    df = pd.DataFrame([s.to_dict() for s in students])

    if df.empty:
        return {'total_records': 0}

    summary = {
        'total_records': len(df),
        'persistence_rate': float(df['first_year_persistence'].mean()) if df['first_year_persistence'].notna().any() else 0,
        'avg_first_term_gpa': float(df['first_term_gpa'].mean()) if df['first_term_gpa'].notna().any() else 0,
        'avg_second_term_gpa': float(df['second_term_gpa'].mean()) if df['second_term_gpa'].notna().any() else 0,
        'missing_values': {col: int(df[col].isna().sum()) for col in df.columns if col != 'id'},
        'persistence_counts': {
            'persisted': int((df['first_year_persistence'] == 1).sum()),
            'not_persisted': int((df['first_year_persistence'] == 0).sum()),
        },
        'gender_distribution': df['gender'].value_counts().to_dict() if df['gender'].notna().any() else {},
        'school_distribution': df['school'].value_counts().to_dict() if df['school'].notna().any() else {},
        'age_group_distribution': df['age_group'].value_counts().to_dict() if df['age_group'].notna().any() else {},
        'residency_distribution': df['residency'].value_counts().to_dict() if df['residency'].notna().any() else {},
        'gpa_stats': {
            'first_term': {
                'mean': float(df['first_term_gpa'].mean()),
                'median': float(df['first_term_gpa'].median()),
                'std': float(df['first_term_gpa'].std()),
                'min': float(df['first_term_gpa'].min()),
                'max': float(df['first_term_gpa'].max()),
            } if df['first_term_gpa'].notna().any() else {},
            'second_term': {
                'mean': float(df['second_term_gpa'].mean()),
                'median': float(df['second_term_gpa'].median()),
                'std': float(df['second_term_gpa'].std()),
                'min': float(df['second_term_gpa'].min()),
                'max': float(df['second_term_gpa'].max()),
            } if df['second_term_gpa'].notna().any() else {},
        },
    }

    # Convert integer keys to strings for JSON serialization
    for key in ['gender_distribution', 'school_distribution', 'age_group_distribution', 'residency_distribution']:
        summary[key] = {str(k): int(v) for k, v in summary[key].items()}

    return summary


def get_students_paginated(page=1, per_page=20, filters=None):
    """Get paginated student records with optional filters."""
    query = Student.query

    if filters:
        if filters.get('school'):
            query = query.filter(Student.school == filters['school'])
        if filters.get('gender'):
            query = query.filter(Student.gender == filters['gender'])
        if filters.get('persistence') is not None:
            query = query.filter(Student.first_year_persistence == filters['persistence'])
        if filters.get('residency'):
            query = query.filter(Student.residency == filters['residency'])

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'students': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    }


def get_correlation_data():
    """Compute correlation matrix for numeric features."""
    students = Student.query.all()
    df = pd.DataFrame([s.to_dict() for s in students])
    df = df.drop(columns=['id'])
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    return {
        'columns': corr.columns.tolist(),
        'values': corr.values.tolist(),
    }
