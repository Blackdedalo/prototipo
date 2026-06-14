import React from "react";

const steps = ["Datos Generales", "Datos Domicilio", "Datos del Hecho", "Denuncia", "Vista Previa", "Constancia"];

export default function Stepper({ current }) {
  return (
    <div className="stepper">
      {steps.map((step, index) => (
        <div className={`step ${index === current ? "current" : ""} ${index < current ? "done" : ""}`} key={step}>
          <span>{index + 1}</span>
          <p>{step}</p>
        </div>
      ))}
    </div>
  );
}
