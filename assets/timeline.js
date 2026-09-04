/* Broad-granularity timeline. Scrub a sequence of moments; see them all at once.
 *
 * The axis is events, not code lines. Every moment stays on screen while you
 * look at one of them, because the principle this component exists to serve is:
 * "If I can't see it all at once, I don't understand it yet."
 *
 * Three tenses:
 *   past    — already built, and the data shown was really produced
 *   present — the thing being built right now
 *   future  — not built yet; the data is a stated expectation, not an observation
 *
 * That third tense is load-bearing. A future moment must never look like a
 * captured one, or the timeline would assert a fact nothing observed (D2).
 *
 * Markup:
 *   <div data-timeline>
 *     <script type="application/json" data-timeline-config>{ ... }</script>
 *   </div>
 *
 * Config:
 *   axis     string  what the slider steps through ("stage", "phase")
 *   start    number  index to open on (default: the first "present", else 0)
 *   moments  array   [{ id, label, sub, tense, when, note, data, links }]
 *     data   array   [{ key, type, value, was }]  — `was` marks a type hop
 *     links  array   [{ href, text }]
 */
(function () {
  const TENSE_WORD = {
    past: "captured",
    present: "building now",
    future: "not built yet",
  };

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function readConfig(root) {
    const script = root.querySelector("[data-timeline-config]");
    if (!script) return null;
    try {
      return JSON.parse(script.textContent);
    } catch (err) {
      root.appendChild(el("p", "tl-error", "Timeline config is not valid JSON."));
      return null;
    }
  }

  /* One row of the data panel. `was` is the previous type, so a hop reads
     left to right: str "經典原味鍋" → menuitem instance. */
  function dataRow(field) {
    const row = el("div", "tl-row");
    row.appendChild(el("span", "tl-key", field.key));

    const val = el("span", "tl-val");
    if (field.was) {
      const from = el("span", "tl-type tl-type-was", field.was);
      val.appendChild(from);
      val.appendChild(el("span", "tl-arrow", "→"));
    }
    val.appendChild(el("span", "tl-type", field.type || "?"));
    val.appendChild(el("code", "tl-lit", String(field.value)));
    row.appendChild(val);
    return row;
  }

  /* The expanded body for one moment. Built once per moment and shown or
     hidden — never rebuilt — so "all at once" costs no extra work. */
  function momentBody(moment) {
    const body = el("div", "tl-body");
    body.dataset.tense = moment.tense || "past";

    const head = el("div", "tl-body-head");
    head.appendChild(el("span", "tl-badge", TENSE_WORD[moment.tense] || moment.tense));
    if (moment.when) head.appendChild(el("span", "tl-when", moment.when));
    body.appendChild(head);

    body.appendChild(el("h3", "tl-body-title", moment.label));
    if (moment.sub) body.appendChild(el("p", "tl-body-sub", moment.sub));

    if (moment.data && moment.data.length) {
      const data = el("div", "tl-data");
      moment.data.forEach((field) => data.appendChild(dataRow(field)));
      body.appendChild(data);
    } else if (moment.tense === "future") {
      body.appendChild(
        el("p", "tl-empty", "No data — nothing has observed this yet.")
      );
    }

    if (moment.note) body.appendChild(el("p", "tl-note", moment.note));

    if (moment.links && moment.links.length) {
      const links = el("div", "tl-links");
      moment.links.forEach((link) => {
        const a = el("a", "tl-link", link.text);
        a.href = link.href;
        links.appendChild(a);
      });
      body.appendChild(links);
    }
    return body;
  }

  function bind(root) {
    const config = readConfig(root);
    if (!config || !config.moments || !config.moments.length) return;

    const moments = config.moments;
    const axis = config.axis || "moment";

    /* Default to the present, because that is the moment the reader is
       standing in. Falling back to 0 keeps a finished timeline readable. */
    let index = config.start;
    if (typeof index !== "number") {
      const present = moments.findIndex((m) => m.tense === "present");
      index = present === -1 ? 0 : present;
    }

    const shell = el("div", "tl");

    /* ---- the strip: every moment, always visible ---- */
    const strip = el("div", "tl-strip");
    const ticks = moments.map((moment, i) => {
      const tick = el("button", "tl-tick");
      tick.type = "button";
      tick.dataset.tense = moment.tense || "past";
      tick.appendChild(el("span", "tl-tick-dot"));
      tick.appendChild(el("span", "tl-tick-label", moment.label));
      tick.addEventListener("click", () => show(i));
      strip.appendChild(tick);
      return tick;
    });
    shell.appendChild(strip);

    /* ---- the scrubber ---- */
    const controls = el("div", "tl-controls");
    const prev = el("button", "tl-step", "◀");
    prev.type = "button";
    const next = el("button", "tl-step", "▶");
    next.type = "button";

    const slider = el("input", "tl-slider");
    slider.type = "range";
    slider.min = "0";
    slider.max = String(moments.length - 1);
    slider.step = "1";
    slider.setAttribute("aria-label", "Scrub " + axis);

    const readout = el("span", "tl-readout");

    controls.appendChild(prev);
    controls.appendChild(slider);
    controls.appendChild(next);
    controls.appendChild(readout);
    shell.appendChild(controls);

    /* ---- all at once ---- */
    const allWrap = el("label", "tl-all");
    const all = el("input");
    all.type = "checkbox";
    allWrap.appendChild(all);
    allWrap.appendChild(el("span", null, "All at once"));
    shell.appendChild(allWrap);

    const bodies = el("div", "tl-bodies");
    const panels = moments.map((moment) => {
      const body = momentBody(moment);
      bodies.appendChild(body);
      return body;
    });
    shell.appendChild(bodies);

    function show(i) {
      index = Math.max(0, Math.min(moments.length - 1, i));
      slider.value = String(index);
      readout.textContent =
        axis + " " + (index + 1) + " of " + moments.length + " · " + moments[index].label;
      ticks.forEach((tick, n) => {
        tick.setAttribute("aria-current", n === index ? "true" : "false");
      });
      const showAll = all.checked;
      panels.forEach((panel, n) => {
        panel.hidden = !showAll && n !== index;
        panel.dataset.dim = showAll && n !== index ? "1" : "0";
      });
      prev.disabled = index === 0;
      next.disabled = index === moments.length - 1;
    }

    slider.addEventListener("input", () => show(Number(slider.value)));
    prev.addEventListener("click", () => show(index - 1));
    next.addEventListener("click", () => show(index + 1));
    all.addEventListener("change", () => show(index));

    strip.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { show(index + 1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { show(index - 1); e.preventDefault(); }
    });

    root.appendChild(shell);
    show(index);
  }

  document.querySelectorAll("[data-timeline]").forEach(bind);
})();
