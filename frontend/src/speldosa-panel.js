// The Speldosa page in the Home Assistant sidebar: boxes, linked tags, and linking a tag to Music
// Assistant content by search. Talks only to the integration's websocket API (api.js).
import { LitElement, html, nothing } from "lit";
import { SpeldosaApi, debounce } from "./api.js";
import { formatWhen, translator } from "./i18n.js";
import { styles } from "./styles.js";

const SEARCH_WAIT_MS = 600;
const MIN_CHARS = 3;
const FILTERS = ["artist", "playlist", "album", "audiobook", "podcast"];
const SERIES = new Set(["random_album", "next_album", "random_episode", "next_episode"]);
const HAS_EPISODES = new Set(["artist", "podcast"]);

const ICON = {
  back: "M20 11H7.8l5.6-5.6L12 4l-8 8 8 8 1.4-1.4L7.8 13H20z",
  search:
    "M15.5 14h-.8l-.3-.3A6.5 6.5 0 1 0 14 15.5l.3.3v.8l5 5 1.5-1.5zm-6 0a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9z",
  music: "M15 6H3v2h12zm0 4H3v2h12zM3 16h8v-2H3zM17 6v8.18A3 3 0 1 0 19 17V8h3V6z",
  plus: "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z",
};

const icon = (path) => html`<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d=${path}></path></svg>`;

export class SpeldosaPanel extends LitElement {
  static properties = {
    hass: { attribute: false },
    narrow: { type: Boolean },
    route: { attribute: false },
    panel: { attribute: false },
    _overview: { state: true },
    _view: { state: true },
    _uid: { state: true },
    _editing: { state: true },
    _query: { state: true },
    _results: { state: true },
    _searching: { state: true },
    _filter: { state: true },
    _selected: { state: true },
    _mode: { state: true },
    _name: { state: true },
    _now: { state: true },
    _confirmUnlink: { state: true },
    _episodes: { state: true },
    _episodesLoading: { state: true },
    _toast: { state: true },
    _error: { state: true },
  };

  static styles = styles;

  constructor() {
    super();
    this._overview = null;
    this._view = "tags";
    this._results = null;
    this._filter = null;
    this._query = "";
    this._search = debounce((q) => this._runSearch(q), SEARCH_WAIT_MS);
    this._searchSeq = 0;
  }

  get _t() {
    return translator(this.hass);
  }

  get _api() {
    if (!this.__api || this.__api.hass !== this.hass) this.__api = new SpeldosaApi(this.hass);
    return this.__api;
  }

  connectedCallback() {
    super.connectedCallback();
    this._subscribe();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._search.cancel();
    this._unsub?.then((unsub) => unsub()).catch(() => {});
    this._unsub = null;
  }

  updated(changed) {
    if (changed.has("hass") && this.hass && !this._overview && !this._loading) this._load();
    if (changed.has("hass") && this.hass && !this._unsub && this.isConnected) this._subscribe();
  }

  _subscribe() {
    if (!this.hass || this._unsub) return;
    this._unsub = this._api.subscribe(() => this._load());
    this._unsub.catch(() => (this._unsub = null));
  }

  async _load() {
    this._loading = true;
    try {
      this._overview = await this._api.overview();
    } catch (err) {
      this._error = err?.message || String(err);
    } finally {
      this._loading = false;
    }
  }

  _box(boxId) {
    const boxes = this._overview?.boxes || [];
    return boxes.find((b) => b.entry_id === boxId) || boxes[0];
  }

  _boxWithTag(uid) {
    return (this._overview?.boxes || []).find((b) => b.tag === uid);
  }

  _flash(text) {
    this._toast = text;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => (this._toast = null), 3500);
  }

  async _call(fn) {
    try {
      return await fn();
    } catch (err) {
      this._flash(this._t("error", { error: err?.message || String(err) }));
      return undefined;
    }
  }

  // Navigation ------------------------------------------------------------------

  _openLink(uid, editing = null) {
    this._uid = uid;
    this._editing = editing;
    this._view = "link";
    this._results = null;
    this._query = "";
    this._filter = null;
    this._selected = null;
    this._name = editing?.name || "";
    this._mode = editing?.mode || null;
    this._confirmUnlink = false;
    this._now = null;
    this._episodes = null;
    this._episodesLoading = false;
    if (editing && HAS_EPISODES.has(editing.media_type)) {
      this._episodesLoading = true;
      this._api
        .tag(uid)
        .then((r) => {
          if (r.episode_list?.length) {
            this._episodes = r.episode_list;
            this._episodesLoading = false;
          } else this._loadEpisodes(editing);
        })
        .catch(() => (this._episodesLoading = false));
    }
    const box = this._boxWithTag(uid) || this._box();
    if (box) this._api.nowPlaying(box.entry_id).then((r) => (this._now = r)).catch(() => {});
  }

  _openNewTag() {
    const box = (this._overview?.boxes || []).find((b) => b.tag && !b.tag_linked);
    if (!box) {
      this._flash(this._t("no_tag_on_box"));
      return;
    }
    this._openLink(box.tag);
  }

  _back() {
    this._search.cancel();
    this._view = "tags";
    this._load();
  }

  // Search ----------------------------------------------------------------------

  _onQuery(ev) {
    this._query = ev.target.value;
    if (this._query.trim().length < MIN_CHARS) {
      this._search.cancel();
      this._results = null;
      return;
    }
    this._search(this._query);
  }

  async _runSearch(query) {
    const seq = ++this._searchSeq;
    this._searching = true;
    const box = this._boxWithTag(this._uid) || this._box();
    try {
      const result = await this._api.search(query, box?.entry_id);
      if (seq === this._searchSeq) this._results = result;
    } catch (err) {
      if (seq === this._searchSeq) this._results = { error: err?.message || String(err) };
    } finally {
      if (seq === this._searchSeq) this._searching = false;
    }
  }

  _select(item) {
    this._selected = item;
    this._mode = item.mode;
    if (!this._editing) this._name = "";
    this._episodes = null;
    if (HAS_EPISODES.has(item.media_type)) this._loadEpisodes(item);
  }

  async _loadEpisodes(item) {
    const box = this._boxWithTag(this._uid) || this._box();
    this._episodesLoading = true;
    const uri = item.uri;
    try {
      const r = await this._api.episodes(item, this._uid, box?.entry_id);
      if ((this._selected || this._editing)?.uri === uri) this._episodes = r.episodes;
    } catch {
      this._episodes = [];
    } finally {
      this._episodesLoading = false;
    }
  }

  _setIncluded(pick) {
    this._episodes = this._episodes.map((e) => ({ ...e, included: pick(e) }));
  }

  _seriesEpisodes(mode) {
    return SERIES.has(mode) && this._episodes?.length ? this._episodes : undefined;
  }

  // Actions ---------------------------------------------------------------------

  async _link() {
    const item = this._selected;
    if (!item) return;
    const box = this._boxWithTag(this._uid) || this._box();
    const tag = await this._call(() =>
      this._api.link({
        uid: this._uid,
        item,
        name: this._name.trim() || (this._editing ? this._editing.name : item.name),
        mode: this._mode || item.mode,
        boxId: box?.entry_id,
        episodes: this._seriesEpisodes(this._mode || item.mode),
      }),
    );
    if (tag) {
      this._flash(this._t("linked_done", { name: tag.name }));
      this._back();
    }
  }

  async _saveEdit() {
    const changes = { mode: this._mode };
    if (this._name.trim()) changes.name = this._name.trim();
    const episodes = this._seriesEpisodes(this._mode);
    if (episodes) changes.episodes = episodes.map(({ uri, title, number, included }) => ({ uri, title, number, included }));
    const tag = await this._call(() => this._api.update(this._uid, changes));
    if (tag) {
      this._flash(this._t("saved"));
      this._back();
    }
  }

  async _tryItem(item, mode) {
    const box = this._boxWithTag(this._uid) || this._box();
    const r = await this._call(() => this._api.tryPlay(item, mode, box?.entry_id));
    if (r) this._flash(this._t("playing_on", { player: r.player_name }));
  }

  async _unlink(uid) {
    await this._call(() => this._api.unlink(uid));
    this._back();
  }

  async _forget(uid) {
    await this._call(() => this._api.forgetSeen(uid));
    this._load();
  }

  // Rendering ---------------------------------------------------------------------

  render() {
    if (!this.hass) return nothing;
    return html`
      ${this._view === "link" ? this._renderLink() : this._renderTags()}
      ${this._toast ? html`<div class="toast" role="status">${this._toast}</div>` : nothing}
    `;
  }

  _toolbar(title, { back = false, aside = "" } = {}) {
    const menu =
      !back && customElements.get("ha-menu-button")
        ? html`<ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>`
        : nothing;
    return html`<div class="toolbar ${this.narrow ? "narrow" : ""}">
      ${menu}
      ${back
        ? html`<button class="text" aria-label=${this._t("back")} @click=${this._back}>${icon(ICON.back)}</button>`
        : nothing}
      <h1>${title}</h1>
      ${aside ? html`<span class="aside">${aside}</span>` : nothing}
    </div>`;
  }

  _cover(image, cls = "cover", round = false) {
    if (image) return html`<img class="${cls} ${round ? "round" : ""}" src=${image} alt="" loading="lazy" />`;
    return html`<div class="${cls} placeholder ${round ? "round" : ""}">${icon(ICON.music)}</div>`;
  }

  _modeLabel(mode) {
    return this._t(`mode_${mode}`);
  }

  _hint(mode) {
    const key = `mode_${mode}_hint`;
    const text = this._t(key);
    return text === key ? "" : text;
  }

  _renderEpisodes(shown) {
    const t = this._t;
    const albums = shown.media_type === "artist";
    if (this._episodesLoading && !this._episodes) return html`<div class="secondary">${t("albums_loading")}…</div>`;
    const list = this._episodes || [];
    if (!list.length) return html`<div class="secondary">${t("albums_none")}</div>`;
    const chosen = list.filter((e) => e.included).length;
    return html`<fieldset class="episodes">
      <legend>${albums ? t("albums_title") : t("episodes_title")}
        <span class="secondary">${t("albums_count", { n: chosen, total: list.length })}</span></legend>
      <div class="filters">
        <button class="filter" @click=${() => this._setIncluded(() => true)}>${t("select_all")}</button>
        <button class="filter" @click=${() => this._setIncluded((e) => e.number != null)}>${t("select_numbered")}</button>
        <button class="filter" @click=${() => this._setIncluded(() => false)}>${t("select_none")}</button>
      </div>
      <div class="episode-list">
        ${list.map(
          (e, i) => html`<label class="episode">
            <input type="checkbox" .checked=${e.included}
              @change=${(ev) => (this._episodes = list.map((x, j) => (j === i ? { ...x, included: ev.target.checked } : x)))} />
            <span>${e.title}</span>
          </label>`,
        )}
      </div>
    </fieldset>`;
  }

  _renderTags() {
    const t = this._t;
    const ov = this._overview;
    if (!ov) {
      return html`${this._toolbar(t("title"))}
        <div class="message">${this._error ? html`<span class="error">${t("error", { error: this._error })}</span>` : "…"}</div>`;
    }
    const newOnBox = ov.boxes.filter((b) => b.tag && !b.tag_linked);
    return html`
      ${this._toolbar(t("title"))}
      <div class="content">
        ${ov.boxes.length === 0 ? html`<div class="tag"><div class="message">${t("no_box")}</div></div>` : nothing}
        ${newOnBox.map(
          (b) => html`<div class="banner">
            ${icon(ICON.plus)}
            <div class="text">
              <strong>${t("new_tag_title", { box: b.name })}</strong>
              ${t("new_tag_text", { tag: b.tag })}
            </div>
            <button class="primary" @click=${() => this._openLink(b.tag)}>${t("link_this")}</button>
          </div>`,
        )}
        ${ov.boxes.length
          ? html`<section class="tag">
              <div class="tag-title">${t("boxes")}</div>
              ${ov.boxes.map((b) => this._renderBox(b))}
            </section>`
          : nothing}
        <section class="tag">
          <div class="tag-title">${t("linked_tags")} <span class="hint">${t("linked_hint")}</span></div>
          ${ov.tags.length === 0 ? html`<div class="message">${t("no_tags")}</div>` : nothing}
          <div class="grid">
            ${ov.tags.map((c) => this._renderTagTile(c))}
            <button class="tile outlined" style="height:auto;min-height:200px;flex-direction:column" @click=${this._openNewTag}>
              ${icon(ICON.plus)}<span>${t("link_new")}</span><span class="secondary">${t("link_new_hint")}</span>
            </button>
          </div>
        </section>
        ${ov.seen.length
          ? html`<section class="tag">
              <div class="tag-title">${t("seen")}</div>
              ${ov.seen.map(
                (s) => html`<div class="row">
                  <span class="grow"><strong>${s.uid}</strong></span>
                  <span class="secondary grow">${this._boxWithTag(s.uid)
                    ? t("on_box_now", { box: this._boxWithTag(s.uid).name })
                    : t("seen_on", { box: s.box || "", when: formatWhen(this.hass, s.last_seen) })}</span>
                  <button class="text" @click=${() => this._openLink(s.uid)}>${t("link")}</button>
                  <button class="text" @click=${() => this._forget(s.uid)}>${t("forget")}</button>
                </div>`,
              )}
            </section>`
          : nothing}
      </div>
    `;
  }

  _renderBox(b) {
    const t = this._t;
    // The tag on the box: its name when linked, and always its tag ID (Andreas, 2026-11-26)
    const onBox = b.tag ? (this._overview?.tags || []).find((c) => c.uid === b.tag) : null;
    let tagState = t("tag_none");
    if (b.tag) tagState = onBox ? t("tag_on_named", { name: onBox.name }) : t("tag_on_unlinked");
    return html`<div class="row">
      <div class="grow">
        <div><strong>${b.name}</strong></div>
        <div class="secondary">${[b.area, t("plays_on", { player: b.player_name })].filter(Boolean).join(" · ")}</div>
        ${b.tag ? html`<div class="secondary tag-id">${t("tag_id", { tag: b.tag })}</div>` : nothing}
      </div>
      ${b.available ? html`<span class="chip">${tagState}</span>` : html`<span class="chip warn">${t("offline")}</span>`}
      ${b.reader_problem ? html`<span class="chip warn">${t("reader_problem")}</span>` : html`<span class="chip">${t("reader_ok")}</span>`}
    </div>`;
  }

  _renderTagTile(c) {
    const t = this._t;
    const player = this._box()?.player_name || "";
    const detail = [t(`type_${c.media_type}`), this._modeLabel(c.mode)];
    if (SERIES.has(c.mode) && c.episodes) detail.push(t("series_progress", { included: c.included, heard: c.heard }));
    return html`<div class="tile">
      ${this._cover(c.image)}
      <div class="body">
        <div class="name">${c.name}</div>
        <div class="secondary tag-id">${t("tag_id", { tag: c.uid })}</div>
        <div class="secondary">${detail.join(" · ")}</div>
        ${c.current ? html`<div class="secondary">${t("listening", { title: c.current })}</div>` : nothing}
      </div>
      <div class="actions">
        <button class="text" @click=${() => this._tryItem(c, c.mode)}>${t("play_on", { player })}</button>
        <button class="text" @click=${() => this._openLink(c.uid, c)}>${t("change")}</button>
      </div>
    </div>`;
  }

  _renderLink() {
    const t = this._t;
    const box = this._boxWithTag(this._uid);
    const title = this._editing
      ? t("change_tag_title", { name: this._editing.name })
      : t("link_tag_title", { tag: this._uid });
    return html`
      ${this._toolbar(title, { back: true, aside: box ? t("on_box_now", { box: box.name }) : "" })}
      <div class="content">
        <div class="split">
          <div class="main">
            <div class="search">
              <label for="q">${t("search_label")}</label>
              ${icon(ICON.search)}
              <input id="q" type="search" autocomplete="off" .value=${this._query} @input=${this._onQuery} />
            </div>
            <div class="secondary">${t("search_hint")}</div>
            ${this._renderNowPlaying()}
            ${this._renderResults()}
          </div>
          <div class="side">${this._renderSide()}</div>
        </div>
      </div>
    `;
  }

  _renderNowPlaying() {
    const now = this._now?.now;
    if (!now?.track) return nothing;
    const t = this._t;
    return html`<div class="tag row" style="border-top:0">
      ${this._cover(now.album?.image || now.track.image, "thumb")}
      <div class="grow">
        <div class="secondary">${t("now_playing", { player: this._now.player_name })}</div>
        <div><strong>${now.track.name}</strong>${now.track.subtitle ? ` · ${now.track.subtitle}` : ""}</div>
      </div>
      ${now.album ? html`<button class="text" @click=${() => this._select(now.album)}>${t("link_album")}</button>` : nothing}
      <button class="text" @click=${() => this._select(now.track)}>${t("link_song")}</button>
    </div>`;
  }

  _renderResults() {
    const t = this._t;
    const r = this._results;
    if (this._query.trim() && this._query.trim().length < MIN_CHARS) return html`<div class="secondary">${t("too_short")}</div>`;
    if (this._searching && !r) return html`<div class="message">${t("searching")}…</div>`;
    if (!r) return nothing;
    if (r.error) return html`<div class="message error">${t("error", { error: r.error })}</div>`;
    if (r.empty) {
      return html`<div class="tag message">${t("empty")}
        <div><button class="text" @click=${() => this._runSearch(this._query)}>${t("try_again")}</button></div></div>`;
    }
    const groups = r.groups.filter((g) => !this._filter || g.media_type === this._filter);
    const best = !this._filter || this._filter === "artist" ? r.best : [];
    return html`
      <div class="filters" role="group">
        <button class="filter" aria-pressed=${String(!this._filter)} @click=${() => (this._filter = null)}>${t("all")}</button>
        ${FILTERS.filter((f) => f === "artist" ? r.best.length || r.groups.some((g) => g.media_type === f) : r.groups.some((g) => g.media_type === f)).map(
          (f) => html`<button class="filter" aria-pressed=${String(this._filter === f)} @click=${() => (this._filter = f)}>${t(`group_${f}`)}</button>`,
        )}
      </div>
      ${best.length
        ? html`<section class="tag"><div class="tag-title" style="font-size:16px">${t("best")}</div>
            <div style="padding:0 8px 8px">${best.map((i) => this._renderLine(i, true))}</div></section>`
        : nothing}
      ${groups.map(
        (g) => html`<section class="tag"><div class="tag-title" style="font-size:16px">${t(`group_${g.media_type}`)}</div>
          ${g.media_type === "artist" || g.media_type === "track"
            ? html`<div style="padding:0 8px 8px">${g.items.map((i) => this._renderLine(i, g.media_type === "artist"))}</div>`
            : html`<div class="results">${g.items.map((i) => this._renderResult(i))}</div>`}
        </section>`,
      )}
      ${!this._filter && r.weaker.length
        ? html`<section class="tag"><div class="tag-title" style="font-size:16px">${t("weaker")}
            <span class="hint">${t("weaker_hint")}</span></div>
            <div style="padding:0 8px 8px">${r.weaker.map((i) => this._renderLine(i))}</div></section>`
        : nothing}
    `;
  }

  _isSelected(item) {
    return this._selected?.uri === item.uri;
  }

  _renderResult(item) {
    return html`<button class="result" aria-pressed=${String(this._isSelected(item))} @click=${() => this._select(item)}>
      ${this._cover(item.image)}
      <span>${item.name}</span>
      <span class="secondary">${[this._t(`type_${item.media_type}`), item.subtitle].filter(Boolean).join(" · ")}</span>
    </button>`;
  }

  _renderLine(item, round = false) {
    return html`<button class="result line" aria-pressed=${String(this._isSelected(item))} @click=${() => this._select(item)}>
      ${this._cover(item.image, "thumb", round)}
      <span><span style="display:block">${item.name}</span>
        <span class="secondary">${[this._t(`type_${item.media_type}`), item.subtitle].filter(Boolean).join(" · ")}</span></span>
    </button>`;
  }

  _renderSide() {
    const t = this._t;
    const item = this._selected;
    const editing = this._editing;
    if (!item && !editing) return html`<div class="tag"><div class="message">${t("pick_first")}</div></div>`;
    const shown = item || editing;
    const modes = shown.modes || [];
    const mode = this._mode || shown.mode;
    const player = (this._boxWithTag(this._uid) || this._box())?.player_name || "";
    return html`<div class="tag">
      ${shown.image ? html`<img class="hero" src=${shown.image} alt="" />` : nothing}
      <div class="inner">
        <div>
          <div style="font-size:20px;line-height:28px">${shown.name}</div>
          <div class="secondary">${[t(`type_${shown.media_type}`), shown.subtitle].filter(Boolean).join(" · ")}</div>
          ${editing && item ? html`<div class="secondary">${t("current_content", { name: editing.name })}</div>` : nothing}
        </div>
        <div class="field">
          <label for="name">${t("name_label")}</label>
          <input id="name" type="text" .value=${this._name} placeholder=${editing?.name || item?.name || ""}
            @input=${(e) => (this._name = e.target.value)} />
        </div>
        <fieldset>
          <legend>${t("how_it_plays")}</legend>
          ${modes.map(
            (m) => html`<label class="mode">
              <input type="radio" name="mode" .checked=${m === mode} @change=${() => (this._mode = m)} />
              <span>${this._modeLabel(m)}${this._hint(m) ? html`<small>${this._hint(m)}</small>` : nothing}</span>
            </label>`,
          )}
          <small class="secondary">${SERIES.has(mode) ? t("series_hint") : t("window_hint")}</small>
        </fieldset>
        ${SERIES.has(mode) ? this._renderEpisodes(shown) : nothing}
        <div class="actions-end">
          ${editing && !item
            ? html`${this._confirmUnlink
                  ? html`<span class="secondary">${t("unlink_confirm", { name: editing.name })}</span>
                      <button class="text" @click=${() => this._unlink(editing.uid)}>${t("unlink")}</button>`
                  : html`<button class="text" @click=${() => (this._confirmUnlink = true)}>${t("unlink")}</button>`}
                <button class="primary" @click=${this._saveEdit}>${t("save")}</button>`
            : html`<button class="text" @click=${() => this._tryItem(item, mode)}>${t("try_on", { player })}</button>
                <button class="primary" @click=${this._link}>${t("link_tag")}</button>`}
        </div>
      </div>
    </div>`;
  }
}

if (!customElements.get("speldosa-panel")) customElements.define("speldosa-panel", SpeldosaPanel);
