/* The flow grid. One interaction's whole journey, on screen at once.
 *
 * Rows are named values; columns are events; the slider only dims what has
 * not happened yet. Two things are always visible without a click: which
 * value is which type at every moment, and which zone the work is in.
 *
 * "If I can't see it all at once, I don't understand it yet."
 *
 * An event is a TRIGGER, never a keystroke — a person doing something, or a
 * function returning a value. That is what moves the data forward, and it is
 * why every event carries what it returned.
 *
 * Unobserved events (`obs: false`) are marked "not captured". They are drawn
 * because the flow is the subject, but never as though something measured
 * them — same rule as D2, applied to a diagram.
 *
 * Markup:
 *   <div data-flow>
 *     <script type="application/json" data-flow-config>{ ... }</script>
 *   </div>
 *
 * Config:
 *   scenario  string   what the person is doing. `backticks` become <code>.
 *   zones     array    [{ id, name }] in the order they should be named
 *   start     number   event index to open on (default 0)
 *   events    array    [{ by, zone, obs, hop, what, fn, ret, sets, note }]
 *     by      "user" | "code"   — who caused it
 *     sets    { name: { t, v, was } }  — t is the type now, was the type before
 */
(function () {
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  /* `backticks` → <code>, so a scenario line can name a URL without the
     config having to carry markup. */
  function ticks(s) {
    return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>');
  }

  function bind(root) {
    const script = root.querySelector("[data-flow-config]");
    if (!script) return;
    let cfg;
    try { cfg = JSON.parse(script.textContent); }
    catch (err) {
      root.appendChild(Object.assign(document.createElement("p"),
        { className: "fl-error", textContent: "Flow config is not valid JSON." }));
      return;
    }
    const EVENTS = cfg.events || [];
    const ZONES = cfg.zones || [];
    if (!EVENTS.length) return;

    const zoneName = id => (ZONES.find(z => z.id === id) || { name: id }).name;

    /* every value name, in the order it first appears */
    const KEYS = [];
    EVENTS.forEach(e => e.sets && Object.keys(e.sets).forEach(k => KEYS.includes(k) || KEYS.push(k)));

    /* contiguous runs of one zone — the band's segments */
    const RUNS = [];
    EVENTS.forEach((e, n) => {
      const last = RUNS[RUNS.length - 1];
      if (last && last.zone === e.zone) { last.span++; last.end = n; }
      else RUNS.push({ zone: e.zone, span: 1, start: n, end: n });
    });

    /* replay the values up to and including event i */
    function stateAt(i) {
      const s = {};
      for (let n = 0; n <= i; n++) {
        const e = EVENTS[n];
        if (e.sets) for (const [k, v] of Object.entries(e.sets)) s[k] = Object.assign({}, v, { at: n });
      }
      return s;
    }

    const shell = document.createElement("div");
    shell.className = "fl";
    shell.innerHTML =
      (cfg.scenario ? `<div class="fl-scenario"><span class="fl-tag">You are doing this</span>` +
        `<span>${ticks(cfg.scenario)}</span></div>` : "") +
      `<div class="fl-scrub">` +
        `<button class="fl-step" type="button" data-go="-1">◀</button>` +
        `<input class="fl-slider" type="range" min="0" step="1" max="${EVENTS.length - 1}" aria-label="Step events">` +
        `<button class="fl-step" type="button" data-go="1">▶</button>` +
        `<span class="fl-readout"></span></div>` +
      `<div class="fl-trigger"></div>` +
      `<div class="fl-grid"></div>` +
      `<div class="fl-values"></div>` +
      `<p class="fl-note"></p>`;
    root.appendChild(shell);

    const slider = shell.querySelector(".fl-slider");
    const readout = shell.querySelector(".fl-readout");
    const trigEl = shell.querySelector(".fl-trigger");
    const gridEl = shell.querySelector(".fl-grid");
    const valsEl = shell.querySelector(".fl-values");
    const noteEl = shell.querySelector(".fl-note");
    const steps = [...shell.querySelectorAll(".fl-step")];

    let i = typeof cfg.start === "number" ? cfg.start : 0;

    function drawGrid() {
      let h = '<table><thead><tr class="fl-zonerow"><th class="fl-name">zone</th>';
      RUNS.forEach(r => {
        const on = i >= r.start && i <= r.end;
        h += `<th class="fl-zb${on ? " on" : ""}" data-z="${esc(r.zone)}" colspan="${r.span}">${esc(zoneName(r.zone))}</th>`;
      });
      h += '</tr><tr class="fl-numrow"><th class="fl-name">value</th>';
      EVENTS.forEach((e, n) => {
        h += `<th class="${n === i ? "fl-now" : ""}" title="${esc(e.fn || e.what)}">` +
             `${e.by === "user" ? '<span class="fl-userflag">●</span>' : n + 1}</th>`;
      });
      h += "</tr></thead><tbody>";

      KEYS.forEach(key => {
        h += `<tr><th class="fl-name">${esc(key)}</th>`;
        let cur = null;
        EVENTS.forEach((e, n) => {
          const set = e.sets && e.sets[key];
          if (set) cur = set;
          const c = ["fl-z-" + e.zone];
          if (n === i) c.push("fl-now");
          if (n > i) c.push("fl-after");
          if (!cur) c.push("fl-void");
          else if (set && set.was) c.push("fl-change");
          else if (set) c.push("fl-born");
          else c.push("fl-hold");
          h += `<td class="${c.join(" ")}">` +
               (set ? `<span class="fl-cv">${esc(set.t)}</span>` : cur ? '<span class="fl-cv">·</span>' : "") +
               "</td>";
        });
        h += "</tr>";
      });
      gridEl.innerHTML = h + "</tbody></table>";

      /* Centre the current column WITHOUT touching vertical scroll —
         scrollIntoView moves both axes and slides the first body row under
         the sticky header. */
      const col = gridEl.querySelector("th.fl-now");
      const nameCell = gridEl.querySelector("th.fl-name");
      if (col && nameCell) {
        const nameW = nameCell.offsetWidth;
        gridEl.scrollLeft = col.offsetLeft - nameW - (gridEl.clientWidth - nameW) / 2 + col.offsetWidth / 2;
      }
    }

    function drawValues() {
      const s = stateAt(i);
      const keys = KEYS.filter(k => s[k]);
      if (!keys.length) { valsEl.innerHTML = '<span class="fl-dim">nothing exists yet</span>'; return; }
      valsEl.innerHTML = keys.map(k =>
        `<div class="fl-row${s[k].at === i ? " now" : ""}">` +
        `<span class="fl-k">${esc(k)}</span>` +
        (s[k].was ? `<span class="fl-ty was">${esc(s[k].was)}</span><span class="fl-arr">→</span>` : "") +
        `<span class="fl-ty">${esc(s[k].t)}</span>` +
        `<span class="fl-lit">${esc(s[k].v)}</span></div>`).join("");
    }

    function draw() {
      const e = EVENTS[i];
      trigEl.innerHTML =
        `<span class="fl-by ${e.by === "user" ? "user" : "code"}">${e.by === "user" ? "you did this" : "code ran"}</span>` +
        `<span class="fl-what">${esc(e.what)}</span>` +
        (e.fn ? `<span class="fl-fn">${esc(e.fn)}</span>` : "") +
        (e.ret ? `<span class="fl-ret">${esc(e.ret)}</span>` : "") +
        (e.obs === false ? '<span class="fl-badge fut">not captured yet</span>' : "") +
        (e.hop ? '<span class="fl-badge hop">type change</span>' : "");
      drawGrid();
      drawValues();
      slider.value = String(i);
      readout.textContent = `event ${i + 1} of ${EVENTS.length} · ${zoneName(e.zone)}`;
      noteEl.textContent = e.note || "";
      steps[0].disabled = i === 0;
      steps[1].disabled = i === EVENTS.length - 1;
    }
    function go(n) { i = Math.max(0, Math.min(EVENTS.length - 1, n)); draw(); }

    slider.addEventListener("input", () => go(Number(slider.value)));
    steps.forEach(b => b.addEventListener("click", () => go(i + Number(b.dataset.go))));
    /* Arrow keys only once the component has focus, so a page carrying two
       of these — or a form — does not fight over them. */
    shell.tabIndex = 0;
    shell.addEventListener("keydown", ev => {
      if (ev.key === "ArrowLeft") { go(i - 1); ev.preventDefault(); }
      if (ev.key === "ArrowRight") { go(i + 1); ev.preventDefault(); }
    });

    draw();
  }

  document.querySelectorAll("[data-flow]").forEach(bind);
})();
