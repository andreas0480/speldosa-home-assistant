// The Speldosa mark as a Home Assistant icon: "speldosa:logo" (sidebar entry, anywhere ha-icon is used).
// Loaded on every page through frontend.add_extra_js_url, so the sidebar has it before the Speldosa page opens.
// One filled path in the mark's own -46..46 grid: the coin ring, the play triangle and two sound waves.

const RING = "M0,-44A44,44 0 1,1 0,44A44,44 0 1,1 0,-44ZM0,-34A34,34 0 1,0 0,34A34,34 0 1,0 0,-34Z";
const PLAY = "M-24,-17L-24,17L4,0Z";
const WAVE_1 = "M13.41,-11.25A17.5,17.5 0 0,1 13.41,11.25L8.04,6.75A10.5,10.5 0 0,0 8.04,-6.75Z";
const WAVE_2 = "M21.07,-17.68A27.5,27.5 0 0,1 21.07,17.68L15.70,13.18A20.5,20.5 0 0,0 15.70,-13.18Z";

export const SPELDOSA_ICONS = {
  logo: { path: RING + PLAY + WAVE_1 + WAVE_2, viewBox: "-46 -46 92 92" },
};

const iconset = {
  getIcon: async (name) => SPELDOSA_ICONS[name] ?? SPELDOSA_ICONS.logo,
  getIconList: async () => Object.keys(SPELDOSA_ICONS).map((name) => ({ name })),
};

window.customIcons = window.customIcons || {};
window.customIcons.speldosa = iconset;
