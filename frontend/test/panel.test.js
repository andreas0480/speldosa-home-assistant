import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { debounce } from "../src/api.js";
import { languageOf, translator } from "../src/i18n.js";
import "../src/speldosa-panel.js";

const OVERVIEW = {
  boxes: [
    {
      entry_id: "box1", name: "Speldosa 55c889", area: "Office", player: "media_player.office_2",
      player_name: "Office", player_state: "idle", available: true, tag: "3A-33-84-19",
      tag_linked: false, reader_problem: false,
    },
  ],
  tags: [
    {
      uid: "04-02", name: "BEST OF Italo Pop", uri: "spotify://playlist/i", media_type: "playlist",
      mode: "from_start", modes: ["from_start", "shuffle", "resume"], image: null, subtitle: null,
      episodes: 0, has_position: false,
    },
  ],
  seen: [{ uid: "BA-2A-A2-80", last_seen: 1794772660, box: "Speldosa 55c889" }],
};

const ARTIST = {
  uri: "spotify://artist/d", name: "Die drei ???", media_type: "artist", image: "https://i.scdn.co/a",
  source_image: "https://i.scdn.co/a", subtitle: null, score: 100,
  modes: ["random_album", "next_album", "shuffle", "from_start"], mode: "random_album",
};
const PLAYLIST = {
  uri: "spotify://playlist/alle", name: "Die drei ??? Alle Folgen (1-240)", media_type: "playlist",
  image: "/api/speldosa/image/x?authSig=y", source_image: "http://ma/imageproxy/x", subtitle: null, score: 85,
  modes: ["from_start", "shuffle", "resume"], mode: "from_start",
};
const SEARCH = {
  best: [ARTIST],
  groups: [{ media_type: "playlist", items: [PLAYLIST] }],
  weaker: [{ ...PLAYLIST, uri: "spotify://audiobook/s", name: "Die drei kleinen Schweinchen", media_type: "audiobook", score: 26 }],
  empty: false,
};

const EPISODES = [
  { uri: "spotify://album/1", title: "001/Panik im Paradies", number: 1, included: true, image: null },
  { uri: "spotify://album/a", title: "Adventskalender - 24 Tage", number: null, included: false, image: null },
  { uri: "spotify://album/2", title: "002/Spuk im Dino-Park", number: 2, included: true, image: null },
];

function fakeHass(language = "en", answers = {}) {
  const calls = [];
  return {
    calls,
    language,
    locale: { language },
    connection: { subscribeMessage: vi.fn(async () => () => {}) },
    callWS: vi.fn(async (msg) => {
      calls.push(msg);
      const answer = answers[msg.type];
      if (typeof answer === "function") return answer(msg);
      if (answer !== undefined) return answer;
      if (msg.type === "speldosa/overview") return structuredClone(OVERVIEW);
      if (msg.type === "speldosa/now_playing") return { player_name: "Office", now: null };
      if (msg.type === "speldosa/search") return structuredClone(SEARCH);
      if (msg.type === "speldosa/tag/link") return { ...msg, name: msg.name };
      if (msg.type === "speldosa/tag/update") return { ...OVERVIEW.tags[0], ...msg };
      if (msg.type === "speldosa/tag/try") return { player_name: "Office" };
      if (msg.type === "speldosa/episodes") return { episodes: structuredClone(EPISODES) };
      if (msg.type === "speldosa/tag/get") return { ...OVERVIEW.tags[0], episode_list: [] };
      return {};
    }),
  };
}

async function mount(hass) {
  const el = document.createElement("speldosa-panel");
  el.hass = hass;
  document.body.appendChild(el);
  await settle(el);
  return el;
}

async function settle(el) {
  for (let i = 0; i < 5; i++) {
    await el.updateComplete;
    await Promise.resolve();
  }
}

const q = (el, sel) => el.shadowRoot.querySelector(sel);
const qa = (el, sel) => [...el.shadowRoot.querySelectorAll(sel)];
const text = (el) => el.shadowRoot.textContent.replace(/\s+/g, " ");
const button = (el, label) => qa(el, "button").find((b) => b.textContent.trim().startsWith(label));

afterEach(() => {
  document.body.innerHTML = "";
  vi.useRealTimers();
});

describe("i18n", () => {
  it("picks Swedish for sv and sv-SE, English otherwise", () => {
    expect(languageOf({ locale: { language: "sv-SE" } })).toBe("sv");
    expect(languageOf({ language: "sv" })).toBe("sv");
    expect(languageOf({ locale: { language: "de" } })).toBe("en");
    expect(languageOf(undefined)).toBe("en");
  });

  it("fills placeholders and falls back to the key", () => {
    const t = translator({ language: "en" });
    expect(t("play_on", { player: "Office" })).toBe("Play on Office");
    expect(t("no_such_key")).toBe("no_such_key");
    expect(translator({ language: "sv" })("mode_resume")).toBe("Fortsätt där det slutade");
  });

  it("has the same keys in English and Swedish", async () => {
    const en = (await import("../src/translations/en.json")).default;
    const sv = (await import("../src/translations/sv.json")).default;
    expect(Object.keys(sv).sort()).toEqual(Object.keys(en).sort());
  });
});

describe("debounce", () => {
  it("runs only the last call after the wait", () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    const d = debounce(fn, 600);
    d("a");
    d("b");
    vi.advanceTimersByTime(599);
    expect(fn).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1);
    expect(fn).toHaveBeenCalledExactlyOnceWith("b");
  });
});

describe("tags page", () => {
  it("shows the new tag, the box, linked and seen tags", async () => {
    const el = await mount(fakeHass());
    const t = text(el);
    expect(t).toContain("A new tag is on Speldosa 55c889");
    expect(t).toContain("Tag on: not linked");
    expect(t).toContain("Office · plays on Office");
    expect(t).toContain("BEST OF Italo Pop");
    expect(t).toContain("Playlist · From the start");
    expect(t).toContain("BA-2A-A2-80");
    expect(t).toContain("Tag 3A-33-84-19");
    expect(t).toContain("Tag 04-02");
  });

  it("names the linked tag on a box and shows its tag ID", async () => {
    const ov = structuredClone(OVERVIEW);
    ov.boxes[0].tag = "04-02";
    ov.boxes[0].tag_linked = true;
    const el = await mount(fakeHass("en", { "speldosa/overview": ov }));
    const t = text(el);
    expect(t).toContain("Tag on: BEST OF Italo Pop");
    expect(t).toContain("Tag 04-02");
  });

  it("is in Swedish for a Swedish user", async () => {
    const el = await mount(fakeHass("sv"));
    expect(text(el)).toContain("En ny bricka ligger på Speldosa 55c889");
    expect(text(el)).toContain("Spellista · Från början");
  });

  it("subscribes to changes", async () => {
    const hass = fakeHass();
    await mount(hass);
    expect(hass.connection.subscribeMessage).toHaveBeenCalledWith(expect.any(Function), { type: "speldosa/subscribe" });
  });
});

describe("linking a tag", () => {
  let hass;
  let el;

  beforeEach(async () => {
    hass = fakeHass();
    el = await mount(hass);
    button(el, "Link this tag").click();
    await settle(el);
  });

  async function typeQuery(value) {
    vi.useFakeTimers();
    const input = q(el, "#q");
    input.value = value;
    input.dispatchEvent(new Event("input"));
    vi.advanceTimersByTime(600);
    vi.useRealTimers();
    await settle(el);
  }

  it("searches once after a pause, not for short queries", async () => {
    await typeQuery("di");
    expect(hass.calls.filter((c) => c.type === "speldosa/search")).toHaveLength(0);
    expect(text(el)).toContain("Type at least 3 characters");
    await typeQuery("Die drei ???");
    const searches = hass.calls.filter((c) => c.type === "speldosa/search");
    expect(searches).toEqual([{ type: "speldosa/search", query: "Die drei ???", box_id: "box1" }]);
    const t = text(el);
    expect(t).toContain("Best match");
    expect(t).toContain("Die drei ??? Alle Folgen (1-240)");
    expect(t).toContain("Weaker matches");
  });

  it("offers the modes of the picked item and links with them", async () => {
    await typeQuery("Die drei ???");
    qa(el, "button.result").find((b) => b.textContent.includes("Die drei ???") && b.textContent.includes("Artist")).click();
    await settle(el);
    const labels = qa(el, "label.mode").map((l) => l.textContent.trim().split("\n")[0].trim());
    expect(labels[0]).toContain("A random album each time");
    expect(labels[0]).toContain("each album is one episode");
    expect(labels[1]).toContain("The next album each time");
    expect(labels).toHaveLength(4);
    expect(qa(el, "label.mode input")[0].checked).toBe(true);
    expect(text(el)).toContain("continues there when it comes back");
    // The album list, with the suggestion from the integration.
    expect(hass.calls.find((c) => c.type === "speldosa/episodes")).toEqual({
      type: "speldosa/episodes", uri: "spotify://artist/d", media_type: "artist", uid: "3A-33-84-19", box_id: "box1",
    });
    expect(text(el)).toContain("2 of 3 chosen");
    button(el, "Link tag").click();
    await settle(el);
    const link = hass.calls.find((c) => c.type === "speldosa/tag/link");
    expect(link).toEqual({
      type: "speldosa/tag/link", uid: "3A-33-84-19", uri: "spotify://artist/d", media_type: "artist",
      name: "Die drei ???", mode: "random_album", image: "https://i.scdn.co/a", subtitle: null, box_id: "box1",
      episodes: EPISODES.map(({ uri, title, number, included }) => ({ uri, title, number, included })),
    });
  });

  it("lets the parent change the album choice", async () => {
    await typeQuery("Die drei ???");
    qa(el, "button.result").find((b) => b.textContent.includes("Die drei ???") && b.textContent.includes("Artist")).click();
    await settle(el);
    qa(el, "fieldset.episodes button").find((b) => b.textContent.trim() === "All").click();
    await settle(el);
    expect(text(el)).toContain("3 of 3 chosen");
    qa(el, "fieldset.episodes button").find((b) => b.textContent.includes("Numbered")).click();
    await settle(el);
    expect(text(el)).toContain("2 of 3 chosen");
    const boxes = qa(el, "label.episode input");
    boxes[2].checked = false;
    boxes[2].dispatchEvent(new Event("change"));
    await settle(el);
    expect(text(el)).toContain("1 of 3 chosen");
    qa(el, "label.mode input")[2].click(); // shuffle: no album list, none sent
    await settle(el);
    expect(q(el, "fieldset.episodes")).toBeNull();
    button(el, "Link tag").click();
    await settle(el);
    const link = hass.calls.find((c) => c.type === "speldosa/tag/link");
    expect(link.mode).toBe("shuffle");
    expect(link.episodes).toBeUndefined();
  });

  it("sends the original image URL, not the signed one", async () => {
    await typeQuery("Die drei ???");
    qa(el, "button.result").find((b) => b.textContent.includes("Alle Folgen")).click();
    await settle(el);
    qa(el, "label.mode input")[1].click();
    await settle(el);
    button(el, "Link tag").click();
    await settle(el);
    const link = hass.calls.find((c) => c.type === "speldosa/tag/link");
    expect(link.image).toBe("http://ma/imageproxy/x");
    expect(link.mode).toBe("shuffle");
  });

  it("says Spotify may be busy on an empty answer and can retry", async () => {
    hass.callWS.mockImplementation(async (msg) => {
      hass.calls.push(msg);
      if (msg.type === "speldosa/search") return { best: [], groups: [], weaker: [], empty: true };
      return {};
    });
    await typeQuery("Bamse");
    expect(text(el)).toContain("Spotify may be busy");
    button(el, "Try again").click();
    await settle(el);
    expect(hass.calls.filter((c) => c.type === "speldosa/search")).toHaveLength(2);
  });

  it("tries an item on the box's speaker", async () => {
    await typeQuery("Die drei ???");
    qa(el, "button.result").find((b) => b.textContent.includes("Alle Folgen")).click();
    await settle(el);
    button(el, "Try on Office").click();
    await settle(el);
    expect(hass.calls.find((c) => c.type === "speldosa/tag/try")).toEqual({
      type: "speldosa/tag/try", uri: "spotify://playlist/alle", media_type: "playlist", mode: "from_start", box_id: "box1",
    });
    expect(text(el)).toContain("Playing on Office");
  });
});

describe("changing a tag", () => {
  it("saves a new mode and name", async () => {
    const hass = fakeHass();
    const el = await mount(hass);
    button(el, "Change").click();
    await settle(el);
    expect(text(el)).toContain("Change BEST OF Italo Pop");
    qa(el, "label.mode input")[1].click();
    const name = q(el, "#name");
    name.value = "Italo";
    name.dispatchEvent(new Event("input"));
    await settle(el);
    button(el, "Save").click();
    await settle(el);
    expect(hass.calls.find((c) => c.type === "speldosa/tag/update")).toEqual({
      type: "speldosa/tag/update", uid: "04-02", mode: "shuffle", name: "Italo",
    });
  });

  it("asks before unlinking", async () => {
    const hass = fakeHass();
    const el = await mount(hass);
    button(el, "Change").click();
    await settle(el);
    button(el, "Unlink").click();
    await settle(el);
    expect(text(el)).toContain("Unlink BEST OF Italo Pop?");
    expect(hass.calls.find((c) => c.type === "speldosa/tag/unlink")).toBeUndefined();
    button(el, "Unlink").click();
    await settle(el);
    expect(hass.calls.find((c) => c.type === "speldosa/tag/unlink")).toEqual({ type: "speldosa/tag/unlink", uid: "04-02" });
  });
});
