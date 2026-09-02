(function () {
  const SNAPSHOTS = {
    before: {
      phase: "before",
      cookie: "(none on this GET)",
      session: "not set",
      user: "not set",
      caption:
        "Your P1.1 print lives here. The path is here because the customer typed it. request.session is not set yet — SessionMiddleware and AuthenticationMiddleware have not run. Your middleware sits first in MIDDLEWARE, so this line is outside those attachments.",
    },
    attach: {
      phase: "resolve",
      cookie: "(none on this GET)",
      session: "being attached",
      user: "being attached",
      caption:
        "Inside get_response, on the way in. SessionMiddleware loads request.session (a dictionary on the server) from the ticket number. AuthenticationMiddleware then sets request.user. No login id in the session → still a user object, the “not signed in” one. Django’s docs call this hooking auth into the request.",
    },
    after: {
      phase: "after",
      cookie: "(none on this GET)",
      session: "attached, keys []",
      user: "AnonymousUser, is_authenticated False",
      caption:
        "Coming back out. Same request. Session and user are still on it. Read them here — the same place you already read the route. A 404 still has a user; do not nest this inside the match check.",
    },
  };

  function bind(root) {
    const diagram = root.querySelector("[data-attach-diagram]");
    const caption = root.querySelector("[data-attach-caption]");
    const cookieEl = root.querySelector("[data-fact='cookie']");
    const sessionEl = root.querySelector("[data-fact='session']");
    const userEl = root.querySelector("[data-fact='user']");
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      if (!snap) return;
      diagram.dataset.phase = snap.phase;
      caption.textContent = snap.caption;
      if (cookieEl) cookieEl.textContent = snap.cookie;
      if (sessionEl) sessionEl.textContent = snap.session;
      if (userEl) userEl.textContent = snap.user;
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

  document.querySelectorAll("[data-attach]").forEach(bind);
})();
