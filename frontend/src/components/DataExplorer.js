import React, { useState, useEffect } from 'react';
import { getStudents, getLabels } from '../services/api';

const COLUMN_HEADERS = [
  { key: 'id', label: 'ID' },
  { key: 'first_term_gpa', label: '1st GPA' },
  { key: 'second_term_gpa', label: '2nd GPA' },
  { key: 'first_language', label: 'Language' },
  { key: 'funding', label: 'Funding' },
  { key: 'school', label: 'School' },
  { key: 'fast_track', label: 'Fast Track' },
  { key: 'coop', label: 'Co-op' },
  { key: 'residency', label: 'Residency' },
  { key: 'gender', label: 'Gender' },
  { key: 'prev_education', label: 'Prev Edu' },
  { key: 'age_group', label: 'Age Group' },
  { key: 'high_school_avg', label: 'HS Avg' },
  { key: 'math_score', label: 'Math' },
  { key: 'english_grade', label: 'English' },
  { key: 'first_year_persistence', label: 'Persistence' },
];

function DataExplorer() {
  const [data, setData] = useState(null);
  const [labels, setLabels] = useState({});
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLabels()
      .then(res => setLabels(res.data))
      .catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    getStudents(page, 25, filters)
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page, filters]);

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters };
    if (value === '') {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    setFilters(newFilters);
    setPage(1);
  };

  const getLabel = (field, value) => {
    if (value === null || value === undefined) return '-';
    if (labels[field] && labels[field][String(value)]) {
      return labels[field][String(value)];
    }
    return value;
  };

  const formatCell = (col, value) => {
    if (value === null || value === undefined) return <span style={{ color: '#555' }}>-</span>;
    if (['first_term_gpa', 'second_term_gpa'].includes(col)) return Number(value).toFixed(2);
    if (col === 'first_year_persistence') {
      return value === 1
        ? <span className="badge badge-success">Yes</span>
        : <span className="badge badge-danger">No</span>;
    }
    const label = getLabel(col, value);
    return label !== value ? label : value;
  };

  return (
    <div>
      <div className="page-header">
        <h1>Data Explorer</h1>
        <p>Browse and filter the student dataset</p>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3>Filters</h3>
        <div className="grid-4">
          <div className="form-group">
            <label>School</label>
            <select value={filters.school || ''} onChange={e => handleFilterChange('school', e.target.value)}>
              <option value="">All Schools</option>
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
            <label>Gender</label>
            <select value={filters.gender || ''} onChange={e => handleFilterChange('gender', e.target.value)}>
              <option value="">All</option>
              <option value="1">Female</option>
              <option value="2">Male</option>
              <option value="3">Neutral</option>
            </select>
          </div>
          <div className="form-group">
            <label>Persistence</label>
            <select value={filters.persistence !== undefined ? filters.persistence : ''} onChange={e => handleFilterChange('persistence', e.target.value)}>
              <option value="">All</option>
              <option value="1">Persisted</option>
              <option value="0">Did Not Persist</option>
            </select>
          </div>
          <div className="form-group">
            <label>Residency</label>
            <select value={filters.residency || ''} onChange={e => handleFilterChange('residency', e.target.value)}>
              <option value="">All</option>
              <option value="1">Domestic</option>
              <option value="2">International</option>
            </select>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="card">
        {loading ? (
          <div className="loading"><div className="spinner" /> Loading data...</div>
        ) : data ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}>Student Records</h2>
              <span style={{ color: '#a0a0b8', fontSize: '0.9rem' }}>
                {data.total} total records
              </span>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    {COLUMN_HEADERS.map(col => (
                      <th key={col.key}>{col.label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.students.map(student => (
                    <tr key={student.id}>
                      {COLUMN_HEADERS.map(col => (
                        <td key={col.key}>{formatCell(col.key, student[col.key])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination">
              <button onClick={() => setPage(p => p - 1)} disabled={!data.has_prev}>
                Previous
              </button>
              <span>Page {data.current_page} of {data.pages}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={!data.has_next}>
                Next
              </button>
            </div>
          </>
        ) : (
          <div className="error-msg">Failed to load data.</div>
        )}
      </div>
    </div>
  );
}

export default DataExplorer;
