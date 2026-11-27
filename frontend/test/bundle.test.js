import { expect, it } from "vitest";

// The committed bundle is what Home Assistant serves; it must define the panel element on its own.
it("the built bundle defines speldosa-panel", async () => {
  await import("../../custom_components/speldosa/frontend/speldosa-panel.js");
  const Panel = customElements.get("speldosa-panel");
  expect(Panel).toBeDefined();
  const el = new Panel();
  el.hass = {
    language: "en",
    locale: { language: "en" },
    connection: { subscribeMessage: async () => () => {} },
    callWS: async () => ({ boxes: [], tags: [], seen: [] }),
  };
  document.body.appendChild(el);
  await el.updateComplete;
  await new Promise((r) => setTimeout(r, 0));
  await el.updateComplete;
  expect(el.shadowRoot.textContent).toContain("No Speldosa box is set up yet");
});
