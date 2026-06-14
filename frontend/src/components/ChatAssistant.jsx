import React from "react";
import { Bot, Send, User } from "lucide-react";
import { useState } from "react";

import { api } from "../api.js";

const fieldLabels = {
  dni: "DNI",
  first_names: "Nombres",
  paternal_last_name: "Apellido paterno",
  maternal_last_name: "Apellido materno",
  birth_date: "Fecha nacimiento",
  civil_status: "Estado civil",
  phone_primary: "Teléfono principal",
  phone_secondary: "Teléfono secundario",
  email: "Correo",
  father_name: "Padre",
  mother_name: "Madre",
  home_department: "Departamento domicilio",
  home_province: "Provincia domicilio",
  home_district: "Distrito domicilio",
  home_address: "Domicilio",
  occupation: "Ocupación",
  event_date: "Fecha del hecho",
  event_hour: "Hora",
  event_minute: "Minutos",
  event_department: "Departamento hecho",
  event_province: "Provincia hecho",
  event_district: "Distrito hecho",
  event_address: "Lugar del hecho",
  police_station: "Comisaría",
  narrative: "Narración",
  lost_items: "Especies perdidas",
};

export default function ChatAssistant({
  context = {},
  currentStep = 0,
  messages: controlledMessages,
  setMessages: setControlledMessages,
  suggestedFields: controlledSuggestedFields,
  setSuggestedFields: setControlledSuggestedFields,
  onApplySuggestedFields,
}) {
  const defaultMessages = [
    {
      role: "assistant",
      content: "Hola. Puedes conversar conmigo y contarme tus datos con calma. Cuando quieras que rellene el formulario, escribe: toma mis datos.",
    },
  ];
  const [localMessages, setLocalMessages] = useState(defaultMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [localSuggestedFields, setLocalSuggestedFields] = useState({});
  const messages = controlledMessages ?? localMessages;
  const setMessages = setControlledMessages ?? setLocalMessages;
  const suggestedFields = controlledSuggestedFields ?? localSuggestedFields;
  const setSuggestedFields = setControlledSuggestedFields ?? setLocalSuggestedFields;

  const send = async (event) => {
    event?.preventDefault();
    if (!input.trim() || loading) return;
    const nextMessages = [...messages, { role: "user", content: input.trim() }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    try {
      const response = await api.chat({ messages: nextMessages, context, current_step: currentStep });
      setMessages([...nextMessages, { role: "assistant", content: response.reply }]);
      setSuggestedFields(response.suggested_fields || {});
    } catch (error) {
      setMessages([...nextMessages, { role: "assistant", content: `No pude consultar la IA ahora: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestionEntries = Object.entries(suggestedFields).filter(([, value]) => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== "" && value !== null && value !== undefined;
  });

  const applySuggestions = () => {
    if (!onApplySuggestedFields) return;
    onApplySuggestedFields(suggestedFields);
    setSuggestedFields({});
    setMessages((current) => [
      ...current,
      { role: "assistant", content: "Listo, apliqué los datos sugeridos al formulario. Revísalos antes de enviar." },
    ]);
  };

  return (
    <section className="chat-box">
      <div className="chat-log">
        {messages.map((message, index) => (
          <div className={`chat-message ${message.role}`} key={`${message.role}-${index}`}>
            {message.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
            <p>{message.content}</p>
          </div>
        ))}
        {loading && <div className="chat-message assistant"><Bot size={18} /><p>Consultando asistente...</p></div>}
        {suggestionEntries.length > 0 && (
          <div className="suggestions-card">
            <strong>Datos detectados</strong>
            <ul>
              {suggestionEntries.map(([field, value]) => (
                <li key={field}>
                  <span>{fieldLabels[field] || field}</span>
                  <code>{Array.isArray(value) ? `${value.length} item(s)` : String(value)}</code>
                </li>
              ))}
            </ul>
            {onApplySuggestedFields ? (
              <button type="button" onClick={applySuggestions}>Aplicar datos sugeridos</button>
            ) : (
              <p>Abre el formulario para aplicar estos datos.</p>
            )}
          </div>
        )}
      </div>
      <form className="chat-input" onSubmit={send}>
        <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Escribe tu consulta..." />
        <button type="submit" title="Enviar">
          <Send size={18} />
        </button>
      </form>
    </section>
  );
}
