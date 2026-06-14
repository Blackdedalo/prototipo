import React from "react";
import { Plus, Trash2 } from "lucide-react";

const emptyItem = {
  modality: "PÉRDIDA",
  item_type: "",
  item_number: "",
  brand: "",
  model: "",
  operator: "",
  description: "",
};

const numberOnlyTypes = ["D.N.I", "CARNET UNIVERSITARIO"];

function hasDraftData(draft) {
  return ["item_type", "item_number", "brand", "model", "operator", "description"].some((field) =>
    String(draft?.[field] || "").trim()
  );
}

export default function LostItemsTable({ items, onChange, errors = {} }) {
  const updateDraft = (field, value) => {
    const nextDraft = { ...(items.draft || emptyItem), [field]: value };
    if (field === "item_type" && numberOnlyTypes.includes(value)) {
      nextDraft.brand = "";
      nextDraft.model = "";
      nextDraft.operator = "";
      nextDraft.description = "";
    }
    onChange({ draft: nextDraft });
  };

  const addItem = () => {
    const draft = items.draft || emptyItem;
    if (!hasDraftData(draft)) return;
    onChange({ list: [...items.list, draft], draft: emptyItem });
  };

  const removeItem = (index) => {
    onChange({ list: items.list.filter((_, itemIndex) => itemIndex !== index), draft: items.draft || emptyItem });
  };

  const draft = items.draft || emptyItem;
  const numberOnly = numberOnlyTypes.includes(draft.item_type);
  const lostItemErrors = Object.entries(errors).filter(([key]) => key.startsWith("lost_items."));

  return (
    <section className="lost-panel">
      <div className="grid two">
        <label>
          Modalidad
          <select value={draft.modality} onChange={(event) => updateDraft("modality", event.target.value)}>
            <option value="PÉRDIDA">PÉRDIDA</option>
            <option value="ROBO">ROBO</option>
          </select>
        </label>
        <label>
          Especie
          <select value={draft.item_type} onChange={(event) => updateDraft("item_type", event.target.value)}>
            <option value="">. SELECCIONE .</option>
            <option value="D.N.I">D.N.I</option>
            <option value="CARNET UNIVERSITARIO">CARNET UNIVERSITARIO</option>
            <option value="CELULAR">CELULAR</option>
            <option value="LICENCIA">LICENCIA</option>
            <option value="TARJETA">TARJETA</option>
            <option value="OTRO">OTRO</option>
          </select>
        </label>
        <label>
          Número
          <input value={draft.item_number} onChange={(event) => updateDraft("item_number", event.target.value)} />
        </label>
        {!numberOnly && (
          <>
            <label>
              Marca
              <input value={draft.brand} onChange={(event) => updateDraft("brand", event.target.value)} />
            </label>
            <label>
              Modelo
              <input value={draft.model} onChange={(event) => updateDraft("model", event.target.value)} />
            </label>
            <label>
              Operador
              <input value={draft.operator} onChange={(event) => updateDraft("operator", event.target.value)} />
            </label>
          </>
        )}
      </div>
      {!numberOnly && (
        <label>
          Descripción
          <textarea value={draft.description} onChange={(event) => updateDraft("description", event.target.value)} />
        </label>
      )}
      {errors.lost_items && <p className="error">{errors.lost_items}</p>}
      {lostItemErrors.length > 0 && (
        <div className="error-list">
          {lostItemErrors.map(([field, message]) => (
            <p className="error" key={field}>{message}</p>
          ))}
        </div>
      )}
      <button className="secondary" type="button" onClick={addItem} disabled={!hasDraftData(draft)}>
        <Plus size={18} /> Agregar especie
      </button>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Modalidad</th>
              <th>Especie</th>
              <th>Número</th>
              <th>Detalle</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.list.map((item, index) => (
              <tr key={`${item.item_type}-${index}`}>
                <td>{item.modality}</td>
                <td>{item.item_type}</td>
                <td>{item.item_number || "-"}</td>
                <td>{[item.brand, item.model, item.operator, item.description].filter(Boolean).join(" ") || "-"}</td>
                <td>
                  <button className="icon danger" type="button" onClick={() => removeItem(index)} title="Eliminar">
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {items.list.length === 0 && (
              <tr>
                <td colSpan="5" className="muted-cell">Sin especies registradas</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
