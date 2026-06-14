import React from "react";

export default function ComplaintPreview({ data }) {
  const fullName = `${data.paternal_last_name} ${data.maternal_last_name} ${data.first_names}`.trim();
  const content = data.lost_items
    .map((item, index) => {
      const details = [item.item_number && `Nro. ${item.item_number}`, item.brand && `MARCA ${item.brand}`, item.model && `MODELO ${item.model}`, item.operator && `OPERADOR ${item.operator}`]
        .filter(Boolean)
        .join(" ");
      return `(${index + 1}) ${item.item_type} ${details}`;
    })
    .join("\n");

  return (
    <section className="preview-doc">
      <div className="preview-banner">
        <div className="crest">PNP</div>
        <strong>POLICÍA NACIONAL DEL PERÚ</strong>
        <strong>COMISARÍA DIGITAL</strong>
      </div>
      <div className="preview-grid">
        <strong>TIPO</strong><span>{data.complaint_type}</span>
        <strong>FORMALIDAD</strong><span>VIRTUAL</span>
        <strong>FECHA Y HORA HECHO</strong><span>{data.event_date} {String(data.event_hour).padStart(2, "0")}:{String(data.event_minute).padStart(2, "0")}:00</span>
        <strong>LUGAR DEL HECHO</strong><span>{data.event_department}/{data.event_province}/{data.event_district} - {data.event_address}</span>
        <strong>COMISARÍA</strong><span>{data.police_station}</span>
        <strong>DENUNCIANTE</strong><span>{fullName} CON DOCUMENTO DE IDENTIDAD PERSONAL NRO. {data.dni}</span>
        <strong>DOMICILIADO EN</strong><span>{data.home_department}/{data.home_province}/{data.home_district} - {data.home_address}</span>
        <strong>OCUPACIÓN</strong><span>{data.occupation}</span>
      </div>
      <strong>CONTENIDO</strong>
      <p>Que haciendo uso del Sistema de Denuncia Virtual de la PNP, hago conocer la PÉRDIDA de la(s) especie(s) indicadas.</p>
      <textarea readOnly value={content} />
      <strong>LO QUE DENUNCIO ANTE LA PNP PARA LOS FINES DEL CASO.</strong>
    </section>
  );
}
