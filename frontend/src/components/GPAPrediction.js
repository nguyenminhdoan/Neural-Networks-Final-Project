import React, { useState } from 'react';
import { predictGPA } from '../services/api';

const INITIAL = {
  first_term_gpa: '', first_language: '1', funding: '2', school: '6',
  fast_track: '2', coop: '2', residency: '1', gender: '1',
  prev_education: '1', age_group: '2', high_school_avg: '', math_score: '',
  english_grade: '7',
};

function GPAPrediction() {
  const [form, setForm] = useState(INITIAL);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await predictGPA(form);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const getGPAColor = (gpa) => {
    if (gpa >= 3.5) return '#06d6a0';
    if (gpa >= 2.5) return '#4361ee';
    if (gpa >= 2.0) return '#ffd166';
    return '#ef476f';
  };

  const getGPALabel = (gpa) => {
    if (gpa >= 3.5) return 'Excellent';
    if (gpa >= 3.0) return 'Good';
    if (gpa >= 2.5) return 'Satisfactory';
    if (gpa >= 2.0) return 'Needs Improvement';
    return 'At Risk';
  };

  return (
    <div>
      <div className="page-header">
        <h1>Second-Term GPA Prediction</h1>
        <p>Predict a student's second-term GPA based on first-term performance and demographics</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>Student Information</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid-2">
              <div className="form-group">
                <label>First Term GPA (0.0 - 4.5)</label>
                <input type="number" name="first_term_gpa" value={form.first_term_gpa}
                  onChange={handleChange} step="0.01" min="0" max="4.5" required />
              </div>
              <div className="form-group">
                <label>First Language</label>
                <select name="first_language" value={form.first_language} onChange={handleChange}>
                  <option value="1">English</option>
                  <option value="2">French</option>
                  <option value="3">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>Funding</label>
                <select name="funding" value={form.funding} onChange={handleChange}>
                  <option value="1">Apprentice_PS</option>
                  <option value="2">GPOG_FT</option>
                  <option value="3">Intl Offshore</option>
                  <option value="4">Intl Regular</option>
                  <option value="5">Intl Transfer</option>
                  <option value="6">Joint Program Ryerson</option>
                  <option value="7">Joint Program UTSC</option>
                  <option value="8">Second Career Program</option>
                  <option value="9">WSIB</option>
                </select>
              </div>
              <div className="form-group">
                <label>School</label>
                <select name="school" value={form.school} onChange={handleChange}>
                  <option value="1">Advancement</option>
                  <option value="2">Business</option>
                  <option value="3">Communications</option>
                  <option value="4">Community & Health</option>
                  <option value="5">Hospitality</option>
                  <option value="6">Engineering</option>
                  <option value="7">Transportation</option>
                </select>
              </div>
              <div className="form-group">
                <label>Fast Track</label>
                <select name="fast_track" value={form.fast_track} onChange={handleChange}>
                  <option value="1">Yes</option>
                  <option value="2">No</option>
                </select>
              </div>
              <div className="form-group">
                <label>Co-op</label>
                <select name="coop" value={form.coop} onChange={handleChange}>
                  <option value="1">Yes</option>
                  <option value="2">No</option>
                </select>
              </div>
              <div className="form-group">
                <label>Residency</label>
                <select name="residency" value={form.residency} onChange={handleChange}>
                  <option value="1">Domestic</option>
                  <option value="2">International</option>
                </select>
              </div>
              <div className="form-group">
                <label>Gender</label>
                <select name="gender" value={form.gender} onChange={handleChange}>
                  <option value="1">Female</option>
                  <option value="2">Male</option>
                  <option value="3">Neutral</option>
                </select>
              </div>
              <div className="form-group">
                <label>Previous Education</label>
                <select name="prev_education" value={form.prev_education} onChange={handleChange}>
                  <option value="1">High School</option>
                  <option value="2">Post-Secondary</option>
                </select>
              </div>
              <div className="form-group">
                <label>Age Group</label>
                <select name="age_group" value={form.age_group} onChange={handleChange}>
                  <option value="1">0-18</option>
                  <option value="2">19-20</option>
                  <option value="3">21-25</option>
                  <option value="4">26-30</option>
                  <option value="5">31-35</option>
                  <option value="6">36-40</option>
                  <option value="7">41-50</option>
                  <option value="8">51-60</option>
                  <option value="9">61-65</option>
                  <option value="10">66+</option>
                </select>
              </div>
              <div className="form-group">
                <label>High School Average (0-100)</label>
                <input type="number" name="high_school_avg" value={form.high_school_avg}
                  onChange={handleChange} min="0" max="100" required />
              </div>
              <div className="form-group">
                <label>Math Score (0-50)</label>
                <input type="number" name="math_score" value={form.math_score}
                  onChange={handleChange} min="0" max="50" required />
              </div>
              <div className="form-group">
                <label>English Grade</label>
                <select name="english_grade" value={form.english_grade} onChange={handleChange}>
                  {[['1','Level-130'],['2','Level-131'],['3','Level-140'],['4','Level-141'],
                    ['5','Level-150'],['6','Level-151'],['7','Level-160'],['8','Level-161'],
                    ['9','Level-170'],['10','Level-171'],['11','Level-180']].map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </div>
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}
                    style={{ marginTop: '16px', width: '100%' }}>
              {loading ? 'Predicting...' : 'Predict GPA'}
            </button>
          </form>
        </div>

        <div>
          {error && <div className="error-msg">{error}</div>}

          {result && (
            <div className="card">
              <h2>Predicted Second-Term GPA</h2>
              <div className="result-box" style={{ textAlign: 'center' }}>
                <div className="result-value" style={{
                  fontSize: '4rem',
                  color: getGPAColor(result.predicted_gpa),
                }}>
                  {result.predicted_gpa}
                </div>
                <div style={{ marginTop: '8px' }}>
                  <span className={`badge ${
                    result.predicted_gpa >= 3.0 ? 'badge-success' :
                    result.predicted_gpa >= 2.0 ? 'badge-warning' : 'badge-danger'
                  }`}>
                    {getGPALabel(result.predicted_gpa)}
                  </span>
                </div>
                <div style={{ marginTop: '20px' }}>
                  <div style={{ color: '#a0a0b8', fontSize: '0.85rem', marginBottom: '6px' }}>
                    GPA Scale
                  </div>
                  <div style={{
                    background: '#1a1a2e',
                    borderRadius: '8px',
                    height: '16px',
                    overflow: 'hidden',
                    position: 'relative',
                  }}>
                    <div style={{
                      width: `${(result.predicted_gpa / 4.5) * 100}%`,
                      height: '100%',
                      background: `linear-gradient(90deg, #ef476f, #ffd166, #06d6a0)`,
                      borderRadius: '8px',
                      transition: 'width 0.5s ease',
                    }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#a0a0b8', marginTop: '4px' }}>
                    <span>0.0</span>
                    <span>4.5</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="card" style={{ marginTop: '20px' }}>
            <h2>About This Model</h2>
            <p style={{ color: '#a0a0b8', fontSize: '0.9rem', lineHeight: '1.7' }}>
              This regression neural network predicts a student's second-term GPA
              based on their first-term GPA, high school scores, and demographic
              factors. It helps identify students who may need additional academic
              support early in their studies.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GPAPrediction;
