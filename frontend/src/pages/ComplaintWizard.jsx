import React from "react";
import { CheckCircle, MapPin } from "lucide-react";
import { useMemo, useState } from "react";

import { api } from "../api.js";
import ChatAssistant from "../components/ChatAssistant.jsx";
import ComplaintPreview from "../components/ComplaintPreview.jsx";
import LostItemsTable from "../components/LostItemsTable.jsx";
import Stepper from "../components/Stepper.jsx";

const today = new Date().toISOString().slice(0, 10);
const initialForm = {
  dni: "",
  first_names: "",
  paternal_last_name: "",
  maternal_last_name: "",
  birth_date: "",
  civil_status: "SOLTERO",
  phone_primary: "",
  phone_secondary: "",
  email: "",
  father_name: "",
  mother_name: "",
  home_department: "JUNIN",
  home_province: "HUANCAYO",
  home_district: "EL TAMBO",
  home_address: "",
  occupation: "",
  event_date: today,
  event_hour: 8,
  event_minute: 0,
  event_department: "JUNIN",
  event_province: "HUANCAYO",
  event_district: "EL TAMBO",
  event_address: "",
  event_latitude: "",
  event_longitude: "",
  police_station: "CPNP EL TAMBO",
  complaint_type: "DENUNCIA",
  narrative: "",
  ai_summary: "",
  lost_items: [],
};

const initialChatMessages = [
  {
    role: "assistant",
    content: "Hola. Puedes conversar conmigo y contarme tus datos con calma. Cuando quieras que rellene el formulario, escribe: toma mis datos.",
  },
];

const fieldLabels = {
  dni: "Nro. D.N.I",
  first_names: "Nombres",
  paternal_last_name: "Apellido paterno",
  maternal_last_name: "Apellido materno",
  birth_date: "Fecha nacimiento",
  civil_status: "Estado civil",
  phone_primary: "Teléfono principal",
  phone_secondary: "Teléfono secundario",
  email: "Correo electrónico",
  father_name: "Padre",
  mother_name: "Madre",
  home_department: "Departamento",
  home_province: "Provincia",
  home_district: "Distrito",
  home_address: "Dirección",
  occupation: "Ocupación",
  event_date: "Fecha",
  event_hour: "Hora",
  event_minute: "Minutos",
  event_department: "Departamento",
  event_province: "Provincia",
  event_district: "Distrito",
  event_address: "Nombre de la vía",
  event_latitude: "Latitud",
  event_longitude: "Longitud",
  police_station: "Comisaría",
  narrative: "Narración adicional",
};

const stepFields = {
  0: new Set([
    "dni",
    "first_names",
    "paternal_last_name",
    "maternal_last_name",
    "birth_date",
    "civil_status",
    "phone_primary",
    "phone_secondary",
    "email",
    "father_name",
    "mother_name",
  ]),
  1: new Set(["home_department", "home_province", "home_district", "home_address", "occupation"]),
  2: new Set([
    "event_date",
    "event_hour",
    "event_minute",
    "event_department",
    "event_province",
    "event_district",
    "event_address",
    "event_latitude",
    "event_longitude",
    "police_station",
  ]),
  3: new Set(["lost_items", "narrative"]),
};

function stepForErrors(validationErrors) {
  const errorKeys = Object.keys(validationErrors || {});
  if (errorKeys.length === 0) return null;
  for (const key of errorKeys) {
    const field = key.split(".")[0];
    if (field === "lost_items") return 3;
    const match = Object.entries(stepFields).find(([, fields]) => fields.has(field));
    if (match) return Number(match[0]);
  }
  return null;
}

function derivePoliceStation(eventDistrict) {
  const district = String(eventDistrict || "").trim().replace(/\s+/g, " ").toUpperCase();
  return district ? `COMISARIA DE ${district}` : "";
}

function draftHasData(draft) {
  if (!draft) return false;
  return ["item_type", "item_number", "brand", "model", "operator", "description"].some((field) =>
    String(draft[field] || "").trim()
  );
}

function effectiveLostItems(lostState) {
  const list = lostState.list || [];
  if (!draftHasData(lostState.draft)) return list;
  return [...list, lostState.draft];
}

function toPayload(form) {
  return {
    ...form,
    birth_date: form.birth_date || null,
    event_hour: Number(form.event_hour),
    event_minute: Number(form.event_minute),
    event_latitude: form.event_latitude === "" ? null : Number(form.event_latitude),
    event_longitude: form.event_longitude === "" ? null : Number(form.event_longitude),
    police_station: derivePoliceStation(form.event_district),
    lost_items: form.lost_items,
  };
}

function Field({ name, form, setForm, errors, type = "text", as = "input", children }) {
  const Component = as;
  return (
    <label>
      {fieldLabels[name]}
      {children || (
        <Component
          type={type}
          value={form[name] ?? ""}
          onChange={(event) => setForm((current) => ({ ...current, [name]: event.target.value }))}
        />
      )}
      {errors[name] && <span className="error">{errors[name]}</span>}
    </label>
  );
}

export default function ComplaintWizard() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [created, setCreated] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [lostState, setLostState] = useState({ list: [], draft: undefined });
  const [chatMessages, setChatMessages] = useState(initialChatMessages);
  const [chatSuggestedFields, setChatSuggestedFields] = useState({});
  const payload = useMemo(
    () => toPayload({ ...form, lost_items: effectiveLostItems(lostState) }),
    [form, lostState]
  );

  const validate = async () => {
    try {
      const result = await api.validateComplaint(payload);
      const validationErrors = result.errors || {};
      setErrors(validationErrors);
      return { valid: result.valid, errors: validationErrors };
    } catch (error) {
      const validationErrors = { general: error.message };
      setErrors(validationErrors);
      return { valid: false, errors: validationErrors };
    }
  };

  const next = async () => {
    if (step >= 4) return;
    if (step === 3 || step === 4) {
      const result = await validate();
      if (!result.valid) {
        const targetStep = stepForErrors(result.errors);
        if (targetStep !== null) setStep(targetStep);
        return;
      }
    }
    setStep((current) => current + 1);
  };

  const submit = async () => {
    setSubmitting(true);
    try {
      const result = await validate();
      if (!result.valid) {
        const targetStep = stepForErrors(result.errors);
        if (targetStep !== null) setStep(targetStep);
        return;
      }
      const complaint = await api.createComplaint(payload);
      setCreated(complaint);
      setStep(5);
    } catch (error) {
      setErrors({ general: error.message });
    } finally {
      setSubmitting(false);
    }
  };

  const applySuggestedFields = (suggestedFields) => {
    const { lost_items: suggestedItems, ...formFields } = suggestedFields;
    const allowedFields = stepFields[step] || stepFields[0];
    setForm((current) => {
      const next = { ...current };
      Object.entries(formFields).forEach(([field, value]) => {
        if (allowedFields.has(field) && field in next && value !== null && value !== undefined && value !== "") {
          next[field] = value;
          if (field === "event_district") {
            next.police_station = derivePoliceStation(value);
          }
        }
      });
      return next;
    });
    if (allowedFields.has("lost_items") && Array.isArray(suggestedItems) && suggestedItems.length > 0) {
      setLostState((current) => {
        const existing = new Set(current.list.map((item) => `${item.item_type}|${item.item_number || ""}`));
        const merged = [...current.list];
        suggestedItems.forEach((item) => {
          const key = `${item.item_type}|${item.item_number || ""}`;
          if (!existing.has(key)) {
            merged.push(item);
            existing.add(key);
          }
        });
        return { ...current, list: merged };
      });
    }
  };

  if (created) {
    return (
      <div className="page-card">
        <Stepper current={5} />
        <section className="success-panel">
          <CheckCircle size={48} />
          <h2>Denuncia registrada</h2>
          <p>Tu código de denuncia generado es:</p>
          <strong className="generated-code">{created.code}</strong>
          <p>Comisaria derivada: {created.police_station}</p>
          <p>Estado inicial: {created.status}</p>
        </section>
        <ComplaintPreview data={created} />
      </div>
    );
  }

  return (
    <div className="wizard-layout">
      <section className="page-card">
        <Stepper current={step} />
        {errors.general && <p className="error banner">{errors.general}</p>}

        {step === 0 && (
          <div className="form-section">
            <p>Registre sus datos personales tal como figuran en su Documento Nacional de Identidad.</p>
            <div className="grid two">
              <Field name="dni" form={form} setForm={setForm} errors={errors} />
              <Field name="birth_date" form={form} setForm={setForm} errors={errors} type="date" />
              <Field name="paternal_last_name" form={form} setForm={setForm} errors={errors} />
              <Field name="maternal_last_name" form={form} setForm={setForm} errors={errors} />
              <Field name="first_names" form={form} setForm={setForm} errors={errors} />
              <Field name="civil_status" form={form} setForm={setForm} errors={errors}>
                <select value={form.civil_status} onChange={(event) => setForm({ ...form, civil_status: event.target.value })}>
                  <option>SOLTERO</option>
                  <option>CASADO</option>
                  <option>DIVORCIADO</option>
                  <option>VIUDO</option>
                </select>
              </Field>
              <Field name="father_name" form={form} setForm={setForm} errors={errors} />
              <Field name="mother_name" form={form} setForm={setForm} errors={errors} />
              <Field name="phone_primary" form={form} setForm={setForm} errors={errors} />
              <Field name="phone_secondary" form={form} setForm={setForm} errors={errors} />
              <Field name="email" form={form} setForm={setForm} errors={errors} type="email" />
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="form-section">
            <h2>Lugar del domicilio</h2>
            <div className="grid two">
              <Field name="home_department" form={form} setForm={setForm} errors={errors} />
              <Field name="home_province" form={form} setForm={setForm} errors={errors} />
              <Field name="home_district" form={form} setForm={setForm} errors={errors} />
              <Field name="home_address" form={form} setForm={setForm} errors={errors} />
              <Field name="occupation" form={form} setForm={setForm} errors={errors} />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="form-section">
            <h2>Fecha, hora y lugar donde ocurrió</h2>
            <div className="grid three">
              <Field name="event_date" form={form} setForm={setForm} errors={errors} type="date" />
              <Field name="event_hour" form={form} setForm={setForm} errors={errors} type="number" />
              <Field name="event_minute" form={form} setForm={setForm} errors={errors} type="number" />
            </div>
            <div className="grid two">
              <Field name="event_department" form={form} setForm={setForm} errors={errors} />
              <Field name="event_province" form={form} setForm={setForm} errors={errors} />
              <Field name="event_district" form={form} setForm={setForm} errors={errors}>
                <input
                  value={form.event_district}
                  onChange={(event) => {
                    const eventDistrict = event.target.value;
                    setForm((current) => ({
                      ...current,
                      event_district: eventDistrict,
                      police_station: derivePoliceStation(eventDistrict),
                    }));
                  }}
                />
              </Field>
              <Field name="event_address" form={form} setForm={setForm} errors={errors} />
              <Field name="police_station" form={form} setForm={setForm} errors={errors}>
                <input value={derivePoliceStation(form.event_district)} readOnly />
              </Field>
              <div className="map-mock">
                <MapPin size={22} />
                <span>Geolocalización simulada</span>
              </div>
              <Field name="event_latitude" form={form} setForm={setForm} errors={errors} type="number" />
              <Field name="event_longitude" form={form} setForm={setForm} errors={errors} type="number" />
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="form-section">
            <h2>Denuncia</h2>
            <LostItemsTable
              items={lostState}
              onChange={(next) => setLostState((current) => ({ ...current, ...next }))}
              errors={errors}
            />
            <Field name="narrative" form={form} setForm={setForm} errors={errors} as="textarea" />
          </div>
        )}

        {step === 4 && (
          <div className="form-section">
            <p>Verifique que todos los datos consignados sean correctos antes de enviar la denuncia.</p>
            <ComplaintPreview data={payload} />
          </div>
        )}

        <div className="wizard-actions">
          <button className="secondary" disabled={step === 0} onClick={() => setStep((current) => Math.max(0, current - 1))}>
            Atrás
          </button>
          {step < 4 ? <button onClick={next}>Siguiente</button> : <button onClick={submit} disabled={submitting}>Enviar denuncia</button>}
        </div>
      </section>
      <ChatAssistant
        context={payload}
        currentStep={step}
        messages={chatMessages}
        setMessages={setChatMessages}
        suggestedFields={chatSuggestedFields}
        setSuggestedFields={setChatSuggestedFields}
        onApplySuggestedFields={applySuggestedFields}
      />
    </div>
  );
}
