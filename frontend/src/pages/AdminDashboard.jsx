import React from "react";
import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api.js";
import { adminStatuses, statusLabels } from "../components/StatusBar.jsx";

function statusOptionsFor(currentStatus) {
  if (!currentStatus || adminStatuses.includes(currentStatus)) return adminStatuses;
  return [currentStatus, ...adminStatuses];
}

export default function AdminDashboard() {
  const [filters, setFilters] = useState({ code: "", dni: "", status: "", date_from: "", date_to: "" });
  const [complaints, setComplaints] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    setError("");
    try {
      setComplaints(await api.adminList(filters));
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const updateStatus = async (id, status) => {
    try {
      const updated = await api.updateStatus(id, status);
      setComplaints((current) => current.map((item) => (item.id === id ? updated : item)));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="page-card admin-page">
      <div className="section-header">
        <div>
          <h1>Panel administrativo</h1>
          <p>Vista abierta para prototipo. Permite revisar denuncias y actualizar estados.</p>
        </div>
        <button className="secondary" onClick={load}><RefreshCw size={18} /> Actualizar</button>
      </div>
      <div className="filters">
        <input placeholder="Código" value={filters.code} onChange={(event) => setFilters({ ...filters, code: event.target.value })} />
        <input placeholder="DNI" value={filters.dni} onChange={(event) => setFilters({ ...filters, dni: event.target.value })} />
        <select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}>
          <option value="">Todos los estados</option>
          {adminStatuses.map((status) => <option value={status} key={status}>{statusLabels[status]}</option>)}
        </select>
        <input type="date" value={filters.date_from} onChange={(event) => setFilters({ ...filters, date_from: event.target.value })} />
        <input type="date" value={filters.date_to} onChange={(event) => setFilters({ ...filters, date_to: event.target.value })} />
        <button onClick={load}>Filtrar</button>
      </div>
      {error && <p className="error banner">{error}</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>DNI</th>
              <th>Denunciante</th>
              <th>Comisaría</th>
              <th>Fecha</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {complaints.map((complaint) => (
              <tr key={complaint.id}>
                <td>{complaint.code}</td>
                <td>{complaint.dni}</td>
                <td>{complaint.paternal_last_name} {complaint.maternal_last_name} {complaint.first_names}</td>
                <td>{complaint.police_station}</td>
                <td>{new Date(complaint.created_at).toLocaleString()}</td>
                <td>
                  <select value={complaint.status} onChange={(event) => updateStatus(complaint.id, event.target.value)}>
                    {statusOptionsFor(complaint.status).map((status) => (
                      <option key={status} value={status}>{statusLabels[status] || status}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {complaints.length === 0 && (
              <tr>
                <td colSpan="6" className="muted-cell">No hay denuncias registradas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
