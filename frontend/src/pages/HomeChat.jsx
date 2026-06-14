import React from "react";
import { ArrowRight, FileText, Search } from "lucide-react";

import ChatAssistant from "../components/ChatAssistant.jsx";

export default function HomeChat({ navigate }) {
  return (
    <div className="home-layout">
      <section className="intro-panel">
        <p className="eyebrow">Prototipo</p>
        <h1>Denuncia Virtual PNP asistida por IA</h1>
        <p>
          Registra una denuncia por pérdida de documentos o especies, revisa la constancia previa y consulta el avance con
          el código generado.
        </p>
        <div className="actions">
          <button onClick={() => navigate("/denuncia")}>
            <FileText size={18} /> Iniciar denuncia <ArrowRight size={18} />
          </button>
          <button className="secondary" onClick={() => navigate("/seguimiento")}>
            <Search size={18} /> Consultar trámite
          </button>
        </div>
      </section>
      <ChatAssistant />
    </div>
  );
}
