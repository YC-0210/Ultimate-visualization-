(function () {
  const LAYERS = {
    print: {
      type: "a string, for the terminal only",
      caption:
        "Same request: GET /api/menuitem/經典原味鍋/. The print already shows the letters you need. That is a label Django wrote for humans. It is not sitting on func as a value you can dump.",
    },
    func: {
      type: "a function — the wrapper as_view() returned",
      caption:
        "func is the thing Django actually called. A class cannot go in the URL list, so Django stored a small function instead. That function is what func is.",
    },
    name: {
      type: 'the string "view"',
      caption:
        "Asking the wrapper its name does not give menuitemDetail. as_view() named the wrapper view. That is why __name__ is a trap of its own.",
    },
    cls: {
      type: "a class — the one you wrote",
      caption:
        "The wrapper still knows the class: view_class. This is the object. Still not JSON.",
    },
    trace: {
      type: "a string, for the Trace",
      caption:
        "Module plus name of that class. Same letters as the print. Different door: you built it from the class, you did not copy the label, and you did not dump func.",
    },
  };

  const TRIES = {
    dump: {
      code: "json.dumps(match.func)",
      result: "TypeError: Object of type function is not JSON serializable",
      kind: "bad",
    },
    name: {
      code: "match.func.__name__",
      result: '"view"',
      kind: "bad",
    },
    cls: {
      code: "view_class.__module__ + '.' + view_class.__qualname__",
      result: '"restaurantAPI.views.menuitemDetail"',
      kind: "ok",
    },
  };

  function bindPeel(root) {
    const diagram = root.querySelector("[data-func-trap-diagram]");
    const caption = root.querySelector("[data-func-trap-caption]");
    const typeEl = root.querySelector("[data-func-trap-type]");
    const buttons = [...root.querySelectorAll("[data-layer]")];

    function show(key) {
      const snap = LAYERS[key];
      if (!snap) return;
      diagram.dataset.layer = key;
      caption.textContent = snap.caption;
      if (typeEl) typeEl.textContent = snap.type;
      buttons.forEach((b) => {
        b.setAttribute(
          "aria-pressed",
          b.dataset.layer === key ? "true" : "false"
        );
      });
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => show(b.dataset.layer))
    );
    show(root.dataset.start || "print");
  }

  function bindTry(root) {
    const out = root.querySelector("[data-func-try-out]");
    const buttons = [...root.querySelectorAll("[data-try]")];
    const seen = new Set();

    function render(key) {
      const t = TRIES[key];
      if (!t) return;
      seen.add(key);
      out.innerHTML = "";
      ["dump", "name", "cls"].forEach((id) => {
        if (!seen.has(id)) return;
        const row = TRIES[id];
        const line = document.createElement("p");
        line.className = "func-try-line";
        line.dataset.kind = row.kind;
        line.innerHTML =
          "<code>" +
          row.code +
          "</code><span>" +
          row.result +
          "</span>";
        out.appendChild(line);
      });
      buttons.forEach((b) => {
        b.setAttribute(
          "aria-pressed",
          b.dataset.try === key ? "true" : "false"
        );
      });
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => render(b.dataset.try))
    );
  }

  document.querySelectorAll("[data-func-trap]").forEach(bindPeel);
  document.querySelectorAll("[data-func-try]").forEach(bindTry);
})();
