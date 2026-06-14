import React from "react";

const statusSteps = [
  { key: "PNP_REVISION_POLICIAL", group: "PNP", label: "Revision Policial" },
  { key: "PNP_REGISTRO_SIDPOL", group: "PNP", label: "Registro en el SIDPOL" },
  { key: "PNP_DERIVADO_DIRECCION", group: "PNP", label: "Derivado a direccion especializada" },
  { key: "PNP_DERIVADO_FISCALIA", group: "PNP", label: "Derivado a fiscalia" },
  { key: "FISCALIA_CARPETA_FISCAL", group: "Fiscalia", label: "En carpeta Fiscal" },
  { key: "FISCALIA_RESOLUCION", group: "Fiscalia", label: "Resolucion" },
  { key: "JUDICIAL_DETENCION", group: "Poder Judicial", label: "Detencion" },
  { key: "JUDICIAL_PENALIDAD", group: "Poder Judicial", label: "Penalidad" },
];

export const statusLabels = {
  PNP_REVISION_POLICIAL: "Revision Policial",
  PNP_REGISTRO_SIDPOL: "Registro en el SIDPOL",
  PNP_DERIVADO_DIRECCION: "Derivado a direccion especializada para investigacion preliminar",
  PNP_DERIVADO_FISCALIA: "Derivado a fiscalia",
  FISCALIA_CARPETA_FISCAL: "En carpeta Fiscal",
  FISCALIA_RESOLUCION: "Resolucion",
  JUDICIAL_DETENCION: "Detencion",
  JUDICIAL_PENALIDAD: "Penalidad",
  OBSERVADO: "Observado",
  REGISTRADA: "Revision Policial",
  EN_REVISION: "Registro en el SIDPOL",
  OBSERVADA: "Observado",
  APROBADA: "Resolucion",
  CONSTANCIA_GENERADA: "Resolucion",
  ARCHIVADA: "Archivada",
};

export const adminStatuses = [
  "PNP_REVISION_POLICIAL",
  "PNP_REGISTRO_SIDPOL",
  "PNP_DERIVADO_DIRECCION",
  "PNP_DERIVADO_FISCALIA",
  "FISCALIA_CARPETA_FISCAL",
  "FISCALIA_RESOLUCION",
  "JUDICIAL_DETENCION",
  "JUDICIAL_PENALIDAD",
  "OBSERVADO",
];

export default function StatusBar({ status }) {
  const legacyStatusMap = {
    REGISTRADA: "PNP_REVISION_POLICIAL",
    EN_REVISION: "PNP_REGISTRO_SIDPOL",
    APROBADA: "FISCALIA_RESOLUCION",
    CONSTANCIA_GENERADA: "FISCALIA_RESOLUCION",
    ARCHIVADA: "JUDICIAL_PENALIDAD",
  };
  const normalizedStatus = legacyStatusMap[status] || status;
  const isObserved = status === "OBSERVADO" || status === "OBSERVADA";
  const index = statusSteps.findIndex((step) => step.key === normalizedStatus);
  const activeIndex = isObserved ? -1 : Math.max(index, 0);

  return (
    <div className="status-wrap">
      <div className="status-line">
        {statusSteps.map((step, stepIndex) => (
          <div className={`status-step ${stepIndex <= activeIndex ? "active" : ""}`} key={step.key}>
            <span>{stepIndex + 1}</span>
            <small>{step.group}</small>
            <p>{step.label}</p>
          </div>
        ))}
      </div>
      {isObserved && <strong className="observed">Observado: requiere revision o subsanacion.</strong>}
      {status === "ARCHIVADA" && <strong className="archived">Tramite archivado</strong>}
    </div>
  );
}
