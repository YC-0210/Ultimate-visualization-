(function () {
  const SNAPSHOTS = {
    arrive: {
      laterState: "empty",
      session: "not set",
      user: "not set",
      match: "not set",
      caption:
        "Your P1.1 print lives here. Django already wrapped this visit in one object. method, path, COOKIES, body, headers are on it because the diner sent them. session, user, and the menu choice are not — those pockets get stamped inside get_response.",
    },
    after: {
      laterState: "live",
      session: 'keys ["table_number", "cart_id", "_auth_user_id", …]',
      user: "User, is_authenticated True",
      match: "menuitem_detail · api/menuitem/<str:slug>/",
      caption:
        "Same object. Same method and path. SessionMiddleware filled session from sessionid. AuthenticationMiddleware filled user from _auth_user_id in that dictionary. The menu walk filled resolver_match. You read all of that here.",
    },
  };

  function bind(root) {
    const later = root.querySelector("[data-pocket='later']");
    const sessionEl = root.querySelector("[data-fact='session']");
    const userEl = root.querySelector("[data-fact='user']");
    const matchEl = root.querySelector("[data-fact='match']");
    const caption = root.querySelector("[data-reqbox-caption]");
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      if (!snap) return;
      later.dataset.state = snap.laterState;
      if (sessionEl) sessionEl.textContent = snap.session;
      if (userEl) userEl.textContent = snap.user;
      if (matchEl) matchEl.textContent = snap.match;
      caption.textContent = snap.caption;
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
    show(root.dataset.start || "arrive");
  }

  document.querySelectorAll("[data-reqbox]").forEach(bind);
})();
