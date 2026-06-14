import React from "react";
import { Search } from "lucide-react";
import { useState } from "react";

import { api } from "../api.js";
import StatusBar, { statusLabels } from "../components/StatusBar.jsx";

export default function Tracking() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);
    try {
      setResult(await api.track(code));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="page-card narrow">
      <h1>Seguimiento de trámite</h1>
      <form className="lookup-form" onSubmit={submit}>
        <input value={code} onChange={(event) => setCode(event.target.value)} placeholder="PNP-2026-000001" />
        <button type="submit"><Search size={18} /> Buscar</button>
      </form>
      {error && <p className="error banner">{error}</p>}
      {result && (
        <div className="tracking-result">
          <StatusBar status={result.status} />
          <dl>
            <dt>Código</dt><dd>{result.code}</dd>
            <dt>Estado</dt><dd>{statusLabels[result.status]}</dd>
            <dt>Denunciante</dt><dd>{result.complainant}</dd>
            <dt>DNI</dt><dd>{result.dni}</dd>
            <dt>Comisaría</dt><dd>{result.police_station}</dd>
            <dt>Lugar del hecho</dt><dd>{result.event_location}</dd>
          </dl>
        </div>
      )}
    </section>
  );
}
