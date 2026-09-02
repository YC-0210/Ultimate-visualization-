(function () {
  const SNAPSHOTS = {
    first: {
      phase: "before",
      cookie: "(none)",
      knows: "stranger — no ticket number",
      caption:
        "First visit. The customer typed the path. They did not bring a ticket. The waiter has no memory of last time — each HTTP request starts as a stranger unless a ticket comes with it.",
    },
    back: {
      phase: "resolve",
      cookie: "(still none on this request)",
      knows: "writes a number on a new ticket",
      caption:
        "Same first visit, on the way out. The waiter writes a number on a ticket and hands it to the customer. HTTP calls that Set-Cookie. You do not print the response yet, so this line will not appear in captured headers.",
    },
    return: {
      phase: "after",
      cookie: "sessionid=…  (a string)",
      knows: "same diner as last visit",
      caption:
        "Second visit, same browser. The customer puts the ticket on the table. HTTP calls that the Cookie header. That is what you already dump in headers. The number is not the diner’s name — it is how Django finds the session dictionary it stored on the server.",
    },
  };

  function bind(root) {
    const diagram = root.querySelector("[data-cookie-diagram]");
    const caption = root.querySelector("[data-cookie-caption]");
    const cookieEl = root.querySelector("[data-fact='cookie']");
    const knowsEl = root.querySelector("[data-fact='knows']");
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      if (!snap) return;
      diagram.dataset.phase = snap.phase;
      caption.textContent = snap.caption;
      if (cookieEl) cookieEl.textContent = snap.cookie;
      if (knowsEl) knowsEl.textContent = snap.knows;
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
    show(root.dataset.start || "first");
  }

  document.querySelectorAll("[data-cookie-trip]").forEach(bind);
})();
