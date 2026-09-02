(function () {
  const STACK = [
    {
      here: "yours",
      done: [],
      session: "not set",
      user: "not set",
      step: "1 · inward · your middleware",
      caption:
        "The diner is at the door. Your middleware is first in MIDDLEWARE, so it sees them first. request.session and request.user are not set — those waiters have not run. This is your print above get_response.",
    },
    {
      here: "session",
      done: ["yours"],
      session: "set — dictionary on the server",
      user: "not set",
      step: "2 · inward · SessionMiddleware",
      caption:
        "You called get_response: that is the next waiter, not the kitchen yet. SessionMiddleware loads request.session from the ticket number. Auth has not run, so request.user is still missing.",
    },
    {
      here: "auth",
      done: ["yours", "session"],
      session: "set — dictionary on the server",
      user: "set — AnonymousUser on this GET",
      step: "3 · inward · AuthenticationMiddleware",
      caption:
        "Auth reads the session dictionary and sets request.user. Django’s docs: it must run after SessionMiddleware; it uses session storage. No login id in the session → still a user object, the “not signed in” one.",
    },
    {
      here: "view",
      done: ["yours", "session", "auth"],
      session: "set — dictionary on the server",
      user: "set — AnonymousUser on this GET",
      step: "4 · the view",
      caption:
        "Last get_response reaches the kitchen. The view can read session and user because those waiters already stamped the same request object on the way in.",
    },
    {
      here: "auth",
      done: ["yours", "session", "auth", "view"],
      session: "set — dictionary on the server",
      user: "set — AnonymousUser on this GET",
      step: "5 · outward · AuthenticationMiddleware",
      caption:
        "Coming back out. Same list, reverse order. Auth is closer to the kitchen, so it sees the response first. The pockets stay on the request.",
    },
    {
      here: "session",
      done: ["yours", "session", "auth", "view"],
      session: "set — dictionary on the server",
      user: "set — AnonymousUser on this GET",
      step: "6 · outward · SessionMiddleware",
      caption:
        "SessionMiddleware on the way out can write Set-Cookie if the session is new. The dictionary itself stays on the server. You already saw that in lesson 0004.",
    },
    {
      here: "yours",
      done: ["yours", "session", "auth", "view"],
      session: "set — dictionary on the server",
      user: "set — AnonymousUser on this GET",
      step: "7 · outward · your middleware",
      caption:
        "Back at the door. Inner waiters already ran. This is your print after get_response — the same place you already dump the route, the user, and the session keys.",
    },
  ];

  function bindStack(root) {
    const buttons = {
      prev: root.querySelector("[data-mw-prev]"),
      next: root.querySelector("[data-mw-next]"),
    };
    const stepEl = root.querySelector("[data-mw-step]");
    const caption = root.querySelector("[data-mw-caption]");
    const sessionEl = root.querySelector("[data-fact='session']");
    const userEl = root.querySelector("[data-fact='user']");
    const layers = [...root.querySelectorAll("[data-layer]")];
    let i = 0;

    function show() {
      const snap = STACK[i];
      if (stepEl) stepEl.textContent = snap.step;
      if (caption) caption.textContent = snap.caption;
      if (sessionEl) sessionEl.textContent = snap.session;
      if (userEl) userEl.textContent = snap.user;
      layers.forEach((el) => {
        const id = el.dataset.layer;
        el.dataset.here = id === snap.here ? "1" : "0";
        el.dataset.done = snap.done.indexOf(id) !== -1 && id !== snap.here ? "1" : "0";
      });
      if (buttons.prev) buttons.prev.disabled = i === 0;
      if (buttons.next) buttons.next.disabled = i === STACK.length - 1;
    }

    if (buttons.prev) buttons.prev.addEventListener("click", () => {
      if (i > 0) {
        i -= 1;
        show();
      }
    });
    if (buttons.next) buttons.next.addEventListener("click", () => {
      if (i < STACK.length - 1) {
        i += 1;
        show();
      }
    });
    show();
  }

  const SWAP = {
    ok: {
      order: "ok",
      caption:
        "Inward, top to bottom. SessionMiddleware sets request.session. AuthenticationMiddleware then reads it and sets request.user. That is the restaurant app’s real order, and the rule in Django’s middleware docs.",
      layers: [
        { here: false, fail: false, name: "SessionMiddleware", job: "sets request.session from the ticket number" },
        { here: false, fail: false, name: "AuthenticationMiddleware", job: "reads that dictionary, sets request.user" },
      ],
    },
    bad: {
      order: "bad",
      caption:
        "Auth ran first. request.session is not set yet. Django’s docs: AuthenticationMiddleware uses session storage, so it must run after SessionMiddleware. Swap them in the live app and Auth cannot do its job.",
      layers: [
        { here: true, fail: true, name: "AuthenticationMiddleware", job: "looks for request.session → not set" },
        { here: false, fail: false, name: "SessionMiddleware", job: "would load the dictionary — too late for Auth on this pass" },
      ],
    },
  };

  function bindSwap(root) {
    const buttons = [...root.querySelectorAll("[data-order]")];
    const caption = root.querySelector("[data-mwswap-caption]");
    const list = root.querySelector("[data-mwswap-layers]");

    function show(key) {
      const snap = SWAP[key];
      if (!snap || !list) return;
      caption.textContent = snap.caption;
      list.innerHTML = "";
      snap.layers.forEach((row) => {
        const li = document.createElement("li");
        if (row.here) li.dataset.here = "1";
        if (row.fail) li.dataset.fail = "1";
        li.innerHTML =
          row.name + '<span class="job">' + row.job + "</span>";
        list.appendChild(li);
      });
      buttons.forEach((b) => {
        b.setAttribute(
          "aria-pressed",
          b.dataset.order === key ? "true" : "false"
        );
      });
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => show(b.dataset.order))
    );
    show(root.dataset.start || "ok");
  }

  document.querySelectorAll("[data-mwstack]").forEach(bindStack);
  document.querySelectorAll("[data-mwswap]").forEach(bindSwap);
})();
