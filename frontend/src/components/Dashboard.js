import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts';
import { getDataSummary, getModelMetrics } from '../services/api';

const COLORS = ['#06d6a0', '#ef476f', '#4361ee', '#ffd166', '#7209b7', '#f72585', '#3a0ca3'];

const SCHOOL_NAMES = {
  '1': 'Advancement', '2': 'Business', '3': 'Communications',
  '4': 'Community & Health', '5': 'Hospitality', '6': 'Engineering', '7': 'Transportation',
};
const GENDER_NAMES = { '1': 'Female', '2': 'Male', '3': 'Neutral' };
const AGE_NAMES = {
  '1': '0-18', '2': '19-20', '3': '21-25', '4': '26-30', '5': '31-35',
  '6': '36-40', '7': '41-50', '8': '51-60', '9': '61-65', '10': '66+',
};

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDataSummary(), getModelMetrics()])
      .then(([summaryRes, metricsRes]) => {
        setSummary(summaryRes.data);
        setMetrics(metricsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading dashboard...</div>;
  }

  if (!summary) {
    return <div className="error-msg">Failed to load dashboard data.</div>;
  }

  const persistenceData = [
    { name: 'Persisted', value: summary.persistence_counts?.persisted || 0 },
    { name: 'Did Not Persist', value: summary.persistence_counts?.not_persisted || 0 },
  ];

  const schoolData = Object.entries(summary.school_distribution || {}).map(([k, v]) => ({
    name: SCHOOL_NAMES[k] || k, value: v,
  }));

  const genderData = Object.entries(summary.gender_distribution || {}).map(([k, v]) => ({
    name: GENDER_NAMES[k] || k, value: v,
  }));

  const ageData = Object.entries(summary.age_group_distribution || {})
    .sort((a, b) => Number(a[0]) - Number(b[0]))
    .map(([k, v]) => ({ name: AGE_NAMES[k] || k, value: v }));

  return (
    <div>
      <div className="page-header">
        <h1>Student Analytics Dashboard</h1>
        <p>Overview of student data and AI model performance</p>
      </div>

      {/* Stat Cards */}
      <div className="grid-4" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-value">{summary.total_records}</div>
          <div className="stat-label">Total Students</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#06d6a0' }}>
            {(summary.persistence_rate * 100).toFixed(1)}%
          </div>
          <div className="stat-label">Persistence Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.avg_first_term_gpa?.toFixed(2)}</div>
          <div className="stat-label">Avg 1st Term GPA</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.avg_second_term_gpa?.toFixed(2)}</div>
          <div className="stat-label">Avg 2nd Term GPA</div>
        </div>
      </div>

      {/* Model Performance Cards */}
      {metrics && metrics.models_ready && (
        <div className="grid-3" style={{ marginBottom: '24px' }}>
          <div className="card">
            <h3>Persistence Model</h3>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#4361ee' }}>
              {(metrics.persistence?.accuracy * 100).toFixed(1)}%
            </div>
            <div style={{ color: '#a0a0b8', fontSize: '0.85rem' }}>Accuracy</div>
            <div style={{ marginTop: '8px', fontSize: '0.9rem' }}>
              F1: {metrics.persistence?.f1_score?.toFixed(3)}
            </div>
            <Link to="/predict/persistence" className="btn btn-primary" style={{ marginTop: '12px', display: 'inline-block', textDecoration: 'none' }}>
              Predict
            </Link>
          </div>
          <div className="card">
            <h3>GPA Prediction Model</h3>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#06d6a0' }}>
              {metrics.gpa?.r2_score?.toFixed(3)}
            </div>
            <div style={{ color: '#a0a0b8', fontSize: '0.85rem' }}>R2 Score</div>
            <div style={{ marginTop: '8px', fontSize: '0.9rem' }}>
              MAE: {metrics.gpa?.mae?.toFixed(3)}
            </div>
            <Link to="/predict/gpa" className="btn btn-primary" style={{ marginTop: '12px', display: 'inline-block', textDecoration: 'none' }}>
              Predict
            </Link>
          </div>
          <div className="card">
            <h3>At-Risk Model</h3>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f72585' }}>
              {(metrics.at_risk?.accuracy * 100).toFixed(1)}%
            </div>
            <div style={{ color: '#a0a0b8', fontSize: '0.85rem' }}>Accuracy</div>
            <div style={{ marginTop: '8px', fontSize: '0.9rem' }}>
              F1: {metrics.at_risk?.f1_score?.toFixed(3)}
            </div>
            <Link to="/predict/atrisk" className="btn btn-primary" style={{ marginTop: '12px', display: 'inline-block', textDecoration: 'none' }}>
              Predict
            </Link>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <div className="card">
          <h2>First-Year Persistence</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={persistenceData} cx="50%" cy="50%" outerRadius={100}
                   dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {persistenceData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>Students by School</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={schoolData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis dataKey="name" tick={{ fill: '#a0a0b8', fontSize: 11 }} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fill: '#a0a0b8' }} />
              <Tooltip contentStyle={{ background: '#16213e', border: '1px solid #2a2a4a' }} />
              <Bar dataKey="value" fill="#4361ee" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>Gender Distribution</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={genderData} cx="50%" cy="50%" outerRadius={100}
                   dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {genderData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i + 2]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>Age Group Distribution</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={ageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis dataKey="name" tick={{ fill: '#a0a0b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#a0a0b8' }} />
              <Tooltip contentStyle={{ background: '#16213e', border: '1px solid #2a2a4a' }} />
              <Bar dataKey="value" fill="#7209b7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* GPA Distribution */}
      {summary.gpa_stats && (
        <div className="card" style={{ marginTop: '24px' }}>
          <h2>GPA Statistics</h2>
          <div className="grid-2">
            <div>
              <h3>First Term GPA</h3>
              <table className="data-table">
                <tbody>
                  <tr><td>Mean</td><td>{summary.gpa_stats.first_term?.mean?.toFixed(3)}</td></tr>
                  <tr><td>Median</td><td>{summary.gpa_stats.first_term?.median?.toFixed(3)}</td></tr>
                  <tr><td>Std Dev</td><td>{summary.gpa_stats.first_term?.std?.toFixed(3)}</td></tr>
                  <tr><td>Min</td><td>{summary.gpa_stats.first_term?.min?.toFixed(3)}</td></tr>
                  <tr><td>Max</td><td>{summary.gpa_stats.first_term?.max?.toFixed(3)}</td></tr>
                </tbody>
              </table>
            </div>
            <div>
              <h3>Second Term GPA</h3>
              <table className="data-table">
                <tbody>
                  <tr><td>Mean</td><td>{summary.gpa_stats.second_term?.mean?.toFixed(3)}</td></tr>
                  <tr><td>Median</td><td>{summary.gpa_stats.second_term?.median?.toFixed(3)}</td></tr>
                  <tr><td>Std Dev</td><td>{summary.gpa_stats.second_term?.std?.toFixed(3)}</td></tr>
                  <tr><td>Min</td><td>{summary.gpa_stats.second_term?.min?.toFixed(3)}</td></tr>
                  <tr><td>Max</td><td>{summary.gpa_stats.second_term?.max?.toFixed(3)}</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
