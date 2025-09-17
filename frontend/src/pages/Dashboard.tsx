import React, { useEffect, useState } from 'react';
import api from '../api';
import { Link, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type Endpoint = {
  id: number;
  user_id: number;
  name: string;
  url: string;
  method: string;
  expected_status: number;
  interval_seconds: number;
  is_active: boolean;
  created_at: string;
};

type Log = {
  id: number;
  endpoint_id: number;
  status_code: number;
  success: boolean;
  latency_ms: number;
  error_message?: string;
  created_at: string;
};

export default function Dashboard() {
  const nav = useNavigate();
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [logs, setLogs] = useState<Log[]>([]);
  const [form, setForm] = useState<Partial<Endpoint>>({ method: 'GET', expected_status: 200, interval_seconds: 60, is_active: true });
  const [err, setErr] = useState<string | null>(null);

  async function fetchEndpoints() {
    try {
      const res = await api.get('/endpoints/');
      setEndpoints(res.data);
      if (res.data.length && selected == null) setSelected(res.data[0].id);
    } catch (e: any) {
      // likely 401
      nav('/login');
    }
  }

  async function fetchLogs(id: number) {
    try {
      const res = await api.get(`/logs/endpoint/${id}`);
      setLogs(res.data.reverse());
    } catch {}
  }

  useEffect(() => {
    fetchEndpoints();
  }, []);

  useEffect(() => {
    if (selected != null) fetchLogs(selected);
  }, [selected]);

  async function createEndpoint(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const res = await api.post('/endpoints/', form);
      setForm({ method: 'GET', expected_status: 200, interval_seconds: 60, is_active: true });
      setSelected(res.data.id);
      fetchEndpoints();
    } catch (e: any) {
      setErr(e.response?.data?.detail || 'Failed to create');
    }
  }

  return (
    <div className="dashboard">
      <header>
        <h2>PulseAPI Dashboard</h2>
        <nav>
          <Link to="/login">Logout</Link>
        </nav>
      </header>

      <section className="grid">
        <div className="panel">
          <h3>Your Endpoints</h3>
          <ul className="list">
            {endpoints.map(e => (
              <li key={e.id} className={selected === e.id ? 'active' : ''} onClick={() => setSelected(e.id)}>
                <span>{e.name}</span>
                <small>{e.method} {e.url}</small>
              </li>
            ))}
          </ul>

          <h4>Add Endpoint</h4>
          <form onSubmit={createEndpoint} className="form">
            <input placeholder="Name" value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} required />
            <input placeholder="URL" value={form.url || ''} onChange={e => setForm({ ...form, url: e.target.value })} required />
            <div className="row">
              <select value={form.method} onChange={e => setForm({ ...form, method: e.target.value })}>
                <option>GET</option>
                <option>POST</option>
                <option>PUT</option>
                <option>DELETE</option>
                <option>PATCH</option>
              </select>
              <input type="number" placeholder="Expected Status" value={form.expected_status || 200} onChange={e => setForm({ ...form, expected_status: Number(e.target.value) })} />
            </div>
            <div className="row">
              <input type="number" placeholder="Interval (s)" value={form.interval_seconds || 60} onChange={e => setForm({ ...form, interval_seconds: Number(e.target.value) })} />
              <label>
                <input type="checkbox" checked={form.is_active ?? true} onChange={e => setForm({ ...form, is_active: e.target.checked })} /> Active
              </label>
            </div>
            <button type="submit">Create</button>
          </form>
          {err && <p className="error">{err}</p>}
        </div>

        <div className="panel">
          <h3>Latency (ms)</h3>
          {logs.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={logs.map(l => ({ ...l, created_at: new Date(l.created_at).toLocaleTimeString() }))}>
                <XAxis dataKey="created_at" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="latency_ms" stroke="#82ca9d" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p>No logs yet. Select an endpoint or wait for checks to run.</p>
          )}
        </div>
      </section>
    </div>
  );
}


