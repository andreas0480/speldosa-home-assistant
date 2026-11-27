// The integration's websocket API (custom_components/speldosa/websocket.py).

export class SpeldosaApi {
  constructor(hass) {
    this.hass = hass;
  }

  overview() {
    return this.hass.callWS({ type: "speldosa/overview" });
  }

  search(query, boxId, types) {
    const msg = { type: "speldosa/search", query };
    if (boxId) msg.box_id = boxId;
    if (types && types.length) msg.types = types;
    return this.hass.callWS(msg);
  }

  nowPlaying(boxId) {
    const msg = { type: "speldosa/now_playing" };
    if (boxId) msg.box_id = boxId;
    return this.hass.callWS(msg);
  }

  link({ uid, item, name, mode, boxId, episodes }) {
    const msg = {
      type: "speldosa/tag/link",
      uid,
      uri: item.uri,
      media_type: item.media_type,
      name: name || item.name,
      mode,
      image: item.source_image ?? item.image ?? null,
      subtitle: item.subtitle ?? null,
    };
    if (boxId) msg.box_id = boxId;
    if (episodes) msg.episodes = episodes.map(({ uri, title, number, included }) => ({ uri, title, number, included }));
    return this.hass.callWS(msg);
  }

  episodes(item, uid, boxId) {
    const msg = { type: "speldosa/episodes", uri: item.uri, media_type: item.media_type };
    if (uid) msg.uid = uid;
    if (boxId) msg.box_id = boxId;
    return this.hass.callWS(msg);
  }

  tag(uid) {
    return this.hass.callWS({ type: "speldosa/tag/get", uid });
  }

  update(uid, changes) {
    return this.hass.callWS({ type: "speldosa/tag/update", uid, ...changes });
  }

  unlink(uid) {
    return this.hass.callWS({ type: "speldosa/tag/unlink", uid });
  }

  tryPlay(item, mode, boxId) {
    const msg = { type: "speldosa/tag/try", uri: item.uri, media_type: item.media_type };
    if (mode) msg.mode = mode;
    if (boxId) msg.box_id = boxId;
    return this.hass.callWS(msg);
  }

  forgetSeen(uid) {
    return this.hass.callWS({ type: "speldosa/seen/forget", uid });
  }

  subscribe(callback) {
    return this.hass.connection.subscribeMessage(callback, { type: "speldosa/subscribe" });
  }
}

// Calls fn after the input has been still for `wait` ms; a newer call cancels the older one.
export function debounce(fn, wait) {
  let timer = null;
  const debounced = (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
  debounced.cancel = () => clearTimeout(timer);
  return debounced;
}
