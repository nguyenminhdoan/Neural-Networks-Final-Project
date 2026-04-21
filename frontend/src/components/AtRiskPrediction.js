import React, { useState } from 'react';
import { predictAtRisk } from '../services/api';

const INITIAL = {
  first_term_gpa: '', first_language: '1', funding: '2', school: '6',
  fast_track: '2', coop: '2', residency: '1', gender: '1',
  prev_education: '1', age_group: '2', high_school_avg: '', math_score: '',
  english_grade: '7',
};

function AtRiskPrediction() {
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
      const res = await predictAtRisk(form);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    if (level === 'High Risk') return '#ef476f';
    if (level === 'Medium Risk') return '#ffd166';
    return '#06d6a0';
  };

  return (
    <div>
      <div className="page-header">
        <h1>At-Risk Student Identification</h1>
        <p>Identify students who may be at risk of poor academic outcomes</p>
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
              {loading ? 'Analyzing...' : 'Assess Risk'}
            </button>
          </form>
        </div>

        <div>
          {error && <div className="error-msg">{error}</div>}

          {result && (
            <div className="card">
              <h2>Risk Assessment Result</h2>
              <div className="result-box" style={{ textAlign: 'center' }}>
                <div style={{
                  width: '120px', height: '120px', borderRadius: '50%',
                  margin: '0 auto 16px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: `conic-gradient(${getRiskColor(result.risk_level)} ${result.probability * 360}deg, #1a1a2e ${result.probability * 360}deg)`,
                  position: 'relative',
                }}>
                  <div style={{
                    width: '90px', height: '90px', borderRadius: '50%',
                    background: '#0f3460', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', flexDirection: 'column',
                  }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: getRiskColor(result.risk_level) }}>
                      {(result.probability * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                <div className="result-value" style={{
                  color: getRiskColor(result.risk_level),
                  fontSize: '1.8rem',
                }}>
                  {result.risk_level}
                </div>
                <div style={{ color: '#a0a0b8', marginTop: '8px', fontSize: '0.95rem' }}>
                  {result.label}
                </div>

                <div style={{ marginTop: '24px', textAlign: 'left' }}>
                  <h3 style={{ color: '#e8e8e8', marginBottom: '12px' }}>Recommendations</h3>
                  {result.risk_level === 'High Risk' && (
                    <ul style={{ color: '#a0a0b8', fontSize: '0.9rem', paddingLeft: '20px' }}>
                      <li>Schedule immediate academic advising appointment</li>
                      <li>Consider tutoring support services</li>
                      <li>Monitor attendance closely</li>
                      <li>Connect with peer mentoring program</li>
                    </ul>
                  )}
                  {result.risk_level === 'Medium Risk' && (
                    <ul style={{ color: '#a0a0b8', fontSize: '0.9rem', paddingLeft: '20px' }}>
                      <li>Schedule check-in with academic advisor</li>
                      <li>Explore study skills workshops</li>
                      <li>Consider joining study groups</li>
                    </ul>
                  )}
                  {result.risk_level === 'Low Risk' && (
                    <ul style={{ color: '#a0a0b8', fontSize: '0.9rem', paddingLeft: '20px' }}>
                      <li>Continue current academic trajectory</li>
                      <li>Explore leadership and enrichment opportunities</li>
                      <li>Consider peer mentoring roles</li>
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="card" style={{ marginTop: '20px' }}>
            <h2>About This Model</h2>
            <p style={{ color: '#a0a0b8', fontSize: '0.9rem', lineHeight: '1.7' }}>
              This model identifies students who may be at risk of poor academic
              outcomes, defined as non-persistence or low GPA (below 2.0).
              Risk levels are categorized as:
            </p>
            <ul style={{ color: '#a0a0b8', fontSize: '0.9rem', marginTop: '8px', paddingLeft: '20px' }}>
              <li><strong style={{ color: '#ef476f' }}>High Risk (70%+)</strong> - Immediate intervention recommended</li>
              <li><strong style={{ color: '#ffd166' }}>Medium Risk (40-70%)</strong> - Proactive support suggested</li>
              <li><strong style={{ color: '#06d6a0' }}>Low Risk (&lt;40%)</strong> - Standard monitoring</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AtRiskPrediction;
