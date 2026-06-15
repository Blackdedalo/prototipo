import React from "react";
import { Plus, Trash2 } from "lucide-react";

const emptyItem = {
  modality: "PERDIDA",
  item_type: "",
  item_number: "",
  brand: "",
  model: "",
  operator: "",
  description: "",
};

const numberOnlyTypes = ["D.N.I", "CARNET UNIVERSITARIO", "LICENCIA", "TARJETA"];
const otherType = "OTRO";

function hasDraftData(draft) {
  return ["item_type", "item_number", "brand", "model", "operator", "description"].some((field) =>
    String(draft?.[field] || "").trim()
  );
}

function cleanDraftForType(draft) {
  if (numberOnlyTypes.includes(draft.item_type)) {
    return { ...draft, brand: "", model: "", operator: "", description: "" };
  }
  if (draft.item_type === otherType) {
    return { ...draft, brand: "", model: "", operator: "" };
  }
  return draft;
}

function itemDetail(item) {
  if (item.item_type === otherType) return item.description || "-";
  return [item.brand, item.model, item.operator, item.description].filter(Boolean).join(" ") || "-";
}

export default function LostItemsTable({ items, onChange, errors = {} }) {
  const updateDraft = (field, value) => {
    const nextDraft = cleanDraftForType({ ...(items.draft || emptyItem), [field]: value });
    onChange({ draft: nextDraft });
  };

  const addItem = () => {
    const draft = cleanDraftForType(items.draft || emptyItem);
    if (!hasDraftData(draft)) return;
    onChange({ list: [...items.list, draft], draft: emptyItem });
  };

  const removeItem = (index) => {
    onChange({ list: items.list.filter((_, itemIndex) => itemIndex !== index), draft: items.draft || emptyItem });
  };

  const draft = cleanDraftForType(items.draft || emptyItem);
  const numberOnly = numberOnlyTypes.includes(draft.item_type);
  const isOther = draft.item_type === otherType;
  const showCellphoneFields = draft.item_type === "CELULAR";
  const lostItemErrors = Object.entries(errors).filter(([key]) => key.startsWith("lost_items."));

  return (
    <section className="lost-panel">
      <div className="grid two">
        <label>
          Modalidad
          <select value={draft.modality} onChange={(event) => updateDraft("modality", event.target.value)}>
            <option value="PERDIDA">PERDIDA</option>
            <option value="ROBO">ROBO</option>
            <option value="HURTO">HURTO</option>
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
          {isOther ? "Nombre" : "Numero"}
          <input value={draft.item_number} onChange={(event) => updateDraft("item_number", event.target.value)} />
        </label>
        {showCellphoneFields && (
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
          Descripcion
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
              <th>Numero / Nombre</th>
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
                <td>{itemDetail(item)}</td>
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
