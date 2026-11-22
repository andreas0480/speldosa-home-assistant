// Page texts in the user's Home Assistant language: Swedish for sv, English otherwise.
import en from "./translations/en.json";
import sv from "./translations/sv.json";

const TABLES = { en, sv };

export function languageOf(hass) {
  const lang = (hass?.locale?.language || hass?.language || "en").toLowerCase();
  return lang.startsWith("sv") ? "sv" : "en";
}

export function translator(hass) {
  const table = TABLES[languageOf(hass)];
  return (key, vars = {}) => {
    const text = table[key] ?? en[key] ?? key;
    return text.replace(/\{(\w+)\}/g, (m, name) => (name in vars ? String(vars[name]) : m));
  };
}

export function formatWhen(hass, epochSeconds) {
  const lang = hass?.locale?.language || hass?.language || "en";
  try {
    return new Intl.DateTimeFormat(lang, { dateStyle: "medium", timeStyle: "short" }).format(
      new Date(epochSeconds * 1000),
    );
  } catch {
    return new Date(epochSeconds * 1000).toISOString().slice(0, 16).replace("T", " ");
  }
}
