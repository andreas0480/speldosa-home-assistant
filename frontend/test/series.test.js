import { afterEach, describe, expect, it, vi } from "vitest";
import "../src/speldosa-panel.js";

const EPISODES = [
  { uri: "spotify://album/1", title: "001/Panik im Paradies", number: 1, included: true, image: null },
  { uri: "spotify://album/a", title: "Adventskalender - 24 Tage", number: null, included: false, image: null },
  { uri: "spotify://album/2", title: "002/Spuk im Dino-Park", number: 2, included: true, image: null },
];
const TAG = {
  uid: "D1", name: "Die drei ??? Kids", uri: "spotify://artist/d", media_type: "artist", mode: "next_album",
  modes: ["random_album", "next_album", "shuffle", "from_start"], image: null, subtitle: null,
  episodes: 3, included: 2, heard: 1, current: "002/Spuk im Dino-Park", has_position: true,
};
const OVERVIEW = {
  boxes: [{ entry_id: "box1", name: "Speldosa 9fd540", area: "Office", player: "media_player.office_2",
    player_name: "Office", player_state: "idle", available: true, tag: null, tag_linked: false,
    reader_problem: false }],
  tags: [TAG],
  seen: [],
};

function fakeHass() {
  const calls = [];
  return {
    calls,
    language: "en",
    locale: { language: "en" },
    connection: { subscribeMessage: vi.fn(async () => () => {}) },
    callWS: vi.fn(async (msg) => {
      calls.push(msg);
      if (msg.type === "speldosa/overview") return structuredClone(OVERVIEW);
      if (msg.type === "speldosa/tag/get") return { ...TAG, episode_list: structuredClone(EPISODES) };
      if (msg.type === "speldosa/tag/update") return { ...TAG, ...msg };
      if (msg.type === "speldosa/now_playing") return { player_name: "Office", now: null };
      return {};
    }),
  };
}

async function settle(el) {
  for (let i = 0; i < 6; i++) {
    await el.updateComplete;
    await Promise.resolve();
  }
}

const qa = (el, sel) => [...el.shadowRoot.querySelectorAll(sel)];
const text = (el) => el.shadowRoot.textContent.replace(/\s+/g, " ");
const button = (el, label) => qa(el, "button").find((b) => b.textContent.trim().startsWith(label));

afterEach(() => {
  document.body.innerHTML = "";
});

describe("changing a series tag", () => {
  it("shows progress, loads the tag's own album choice and saves changes to it", async () => {
    const hass = fakeHass();
    const el = document.createElement("speldosa-panel");
    el.hass = hass;
    document.body.appendChild(el);
    await settle(el);
    expect(text(el)).toContain("2 chosen · 1 heard");
    expect(text(el)).toContain("Listening: 002/Spuk im Dino-Park");
    button(el, "Change").click();
    await settle(el);
    expect(hass.calls.some((c) => c.type === "speldosa/episodes")).toBe(false);
    expect(text(el)).toContain("2 of 3 chosen");
    const boxes = qa(el, "label.episode input");
    boxes[1].checked = true;
    boxes[1].dispatchEvent(new Event("change"));
    await settle(el);
    button(el, "Save").click();
    await settle(el);
    const update = hass.calls.find((c) => c.type === "speldosa/tag/update");
    expect(update.mode).toBe("next_album");
    expect(update.episodes.map((e) => e.included)).toEqual([true, true, true]);
  });
});
