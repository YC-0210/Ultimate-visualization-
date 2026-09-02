(function () {
  const SNAPSHOTS = {
    before: {
      phase: "before",
      path: "/api/menuitem/經典原味鍋/",
      match: "not set",
      caption:
        "Your P1.1 print lives here. The path is here because the browser sent it. The result is not — Django has not walked urlpatterns yet.",
    },
    resolve: {
      phase: "resolve",
      path: "/api/menuitem/經典原味鍋/",
      match: "the result is being stored",
      caption:
        "Inside get_response. Django walks urlpatterns in order and stops at the first match. The docs call this walk “URL resolving.” This is the first moment the result exists.",
    },
    after: {
      phase: "after",
      path: "/api/menuitem/經典原味鍋/",
      match: "the result is on the request",
      caption:
        "Coming back out. Same request. The result is still on it. Read it here — not on the line above get_response.",
    },
  };

  function bind(root) {
    const diagram = root.querySelector("[data-onion-diagram]");
    const caption = root.querySelector("[data-onion-caption]");
    const pathEl = root.querySelector("[data-fact='path']");
    const matchEl = root.querySelector("[data-fact='match']");
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      if (!snap) return;
      diagram.dataset.phase = snap.phase;
      caption.textContent = snap.caption;
      if (pathEl) pathEl.textContent = snap.path;
      if (matchEl) matchEl.textContent = snap.match;
      buttons.forEach((b) => {
        b.setAttribute(
          "aria-pressed",
          b.dataset.moment === key ? "true" : "false"
        );
      });
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => show(b.dataset.moment))
    );
    show(root.dataset.start || "before");
  }

  document.querySelectorAll("[data-onion]").forEach(bind);
})();
