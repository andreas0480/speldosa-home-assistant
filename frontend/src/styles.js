// Styles on Home Assistant's theme variables, so the page follows the user's theme (light, dark, custom).
import { css } from "lit";

export const styles = css`
  :host {
    display: block;
    min-height: 100vh;
    background: var(--primary-background-color, #fafafa);
    color: var(--primary-text-color, #212121);
    font-family: var(--ha-font-family-body, Roboto, system-ui, sans-serif);
    font-size: 14px;
    line-height: 20px;
  }
  .toolbar {
    height: var(--header-height, 56px);
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 8px 0 16px;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
    background: var(--app-header-background-color, var(--primary-background-color, #fafafa));
    color: var(--app-header-text-color, var(--primary-text-color, #212121));
    box-sizing: border-box;
  }
  .toolbar.narrow { padding-left: 0; }
  .toolbar h1 { margin: 0; font-size: 20px; font-weight: 400; flex: 1 1 auto; min-width: 0;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .toolbar .aside { color: var(--secondary-text-color, #727272); white-space: nowrap; }
  .content { padding: 16px; display: flex; flex-direction: column; gap: 16px; max-width: 1040px;
    box-sizing: border-box; margin: 0 auto; }
  .card { display: block; background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1px solid var(--divider-color, #e0e0e0); border-radius: var(--ha-card-border-radius, 12px);
    color: var(--primary-text-color); }
  .card-title { padding: 16px 16px 8px; font-size: 20px; line-height: 28px; display: flex;
    align-items: baseline; gap: 12px; flex-wrap: wrap; }
  .card-title .hint, .secondary { color: var(--secondary-text-color, #727272); font-size: 14px; }
  .banner { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12); border-radius: 12px;
    padding: 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
  .banner .text { flex: 1 1 320px; min-width: 0; }
  .banner .text strong { display: block; font-size: 16px; font-weight: 500; }
  button, a.button { font: inherit; font-weight: 500; cursor: pointer; border-radius: 18px; height: 36px;
    padding: 0 16px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    text-decoration: none; box-sizing: border-box; }
  button.primary { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); border: 0; }
  button.text { background: transparent; color: var(--primary-color, #03a9f4); border: 0; padding: 0 12px; }
  button.outlined { background: transparent; color: var(--primary-color, #03a9f4);
    border: 1px solid var(--outline-color, var(--divider-color, #bdbdbd)); }
  button:disabled { opacity: 0.5; cursor: default; }
  button:focus-visible, input:focus-visible, .result:focus-visible {
    outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 2px; }
  .row { display: flex; align-items: center; gap: 16px; padding: 8px 16px; min-height: 56px;
    border-top: 1px solid var(--divider-color, #eee); flex-wrap: wrap; }
  .row .grow { flex: 1 1 200px; min-width: 0; }
  .chip { background: var(--secondary-background-color, #f5f5f5); border-radius: 8px; padding: 4px 10px; }
  .chip.warn { background: rgba(var(--rgb-warning-color, 255, 166, 0), 0.2); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px;
    padding: 8px 16px 16px; }
  .tile { border: 1px solid var(--divider-color, #e0e0e0); border-radius: 12px; overflow: hidden;
    display: flex; flex-direction: column; background: var(--card-background-color, #fff); }
  .tile .body { padding: 12px; }
  .tile .body .name { font-weight: 500; }
  .tile .actions { display: flex; flex-wrap: wrap; gap: 4px; padding: 0 8px 8px; }
  .cover { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; display: block;
    background: var(--secondary-background-color, #eceff1); }
  .cover.placeholder { display: flex; align-items: center; justify-content: center;
    color: var(--secondary-text-color); }
  .thumb { width: 48px; height: 48px; border-radius: 6px; object-fit: cover; flex: 0 0 auto;
    background: var(--secondary-background-color, #eceff1); }
  .thumb.round { border-radius: 50%; }
  .search { position: relative; display: flex; align-items: center; gap: 12px; height: 56px; padding: 0 12px;
    border: 1px solid var(--outline-color, #9e9e9e); border-radius: 4px;
    background: var(--card-background-color, #fff); }
  .search label, .field label { position: absolute; top: -9px; left: 10px; padding: 0 4px; font-size: 12px;
    background: var(--card-background-color, #fff); color: var(--primary-color, #03a9f4); }
  .search input, .field input { flex: 1 1 auto; border: 0; outline: none; font: inherit; font-size: 16px;
    background: transparent; color: var(--primary-text-color); min-width: 0; }
  .field { position: relative; display: flex; align-items: center; height: 56px; padding: 0 12px;
    border: 1px solid var(--outline-color, #9e9e9e); border-radius: 4px; }
  .field label { color: var(--secondary-text-color); }
  .filters { display: flex; gap: 8px; flex-wrap: wrap; }
  .filter { height: 32px; border-radius: 8px; padding: 0 12px; font-weight: 400;
    background: transparent; color: var(--primary-text-color); border: 1px solid var(--outline-color, #bdbdbd); }
  .filter[aria-pressed="true"] { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.16);
    border-color: transparent; font-weight: 500; }
  .split { display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-start; }
  .split > .main { flex: 999 1 480px; min-width: 0; display: flex; flex-direction: column; gap: 16px; }
  .split > .side { flex: 1 1 300px; min-width: 0; position: sticky; top: 16px; }
  .results { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px;
    padding: 0 16px 16px; }
  .result { display: flex; flex-direction: column; gap: 6px; padding: 7px; text-align: left; height: auto;
    border-radius: 12px; border: 1px solid var(--divider-color, #e0e0e0); background: transparent;
    color: var(--primary-text-color); font-weight: 400; align-items: stretch; }
  .result[aria-pressed="true"] { border: 2px solid var(--primary-color, #03a9f4); padding: 6px;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08); }
  .result .cover { border-radius: 8px; }
  .result.line { flex-direction: row; align-items: center; gap: 12px; border: 0; border-radius: 8px; padding: 8px; }
  .result.line[aria-pressed="true"] { padding: 6px; }
  .side .card { overflow: hidden; }
  .side .inner { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
  .side .hero { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; display: block;
    background: var(--secondary-background-color, #eceff1); }
  fieldset { border: 0; margin: 0; padding: 0; display: flex; flex-direction: column; }
  legend { font-weight: 500; padding: 0; margin-bottom: 4px; }
  .mode { display: flex; gap: 12px; align-items: flex-start; min-height: 40px; padding: 4px 0; cursor: pointer; }
  .mode input { width: 18px; height: 18px; margin: 1px 0 0; accent-color: var(--primary-color, #03a9f4); }
  .mode small { display: block; color: var(--secondary-text-color); }
  .episodes { gap: 8px; }
  .episodes legend { display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
  .episode-list { max-height: 320px; overflow-y: auto; border: 1px solid var(--divider-color, #e0e0e0);
    border-radius: 8px; padding: 4px 8px; }
  .episode { display: flex; gap: 10px; align-items: center; min-height: 36px; cursor: pointer; }
  .episode input { width: 18px; height: 18px; margin: 0; accent-color: var(--primary-color, #03a9f4); }
  .actions-end { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; }
  .message { padding: 16px; color: var(--secondary-text-color); }
  .toast { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
    background: var(--primary-text-color, #323232); color: var(--primary-background-color, #fff);
    padding: 12px 20px; border-radius: 8px; z-index: 10; max-width: calc(100% - 32px); }
  .error { color: var(--error-color, #db4437); }
  svg.icon { width: 24px; height: 24px; fill: currentColor; flex: 0 0 auto; }
  .card-id {
    font-family: var(--code-font-family, monospace);
    font-size: 0.85em;
  }
`;
