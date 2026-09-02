(function () {
  const SNAPSHOTS = {
    install: {
      hatch: true,
      queries: [],
      caption:
        "The wrapper is installed for this request only. No SQL has run yet. Django’s docs: execute_wrapper is a context manager — on when you enter, off when you leave.",
    },
    queries: {
      hatch: true,
      queries: ["session", "view"],
      caption:
        "Inside get_response, each database call goes through the wrapper. You copy the sql string as it passes, then call execute so the query still runs. SessionMiddleware may send a query too — wrapping get_response sees all of them, not only the view.",
    },
    dump: {
      hatch: false,
      queries: ["session", "view"],
      caption:
        "The with block has ended, so the wrapper is gone. The list you filled is still in memory. Dump it here, next to the route and view facts you already print after get_response.",
    },
  };

  function bind(root) {
    const hatch = root.querySelector("[data-sqlwrap-hatch]");
    const caption = root.querySelector("[data-sqlwrap-caption]");
    const queries = [...root.querySelectorAll("[data-query]")];
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      if (!snap) return;
      hatch.dataset.on = snap.hatch ? "1" : "0";
      queries.forEach((li) => {
        li.dataset.on = snap.queries.includes(li.dataset.query) ? "1" : "0";
      });
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
    show(root.dataset.start || "install");
  }

  document.querySelectorAll("[data-sqlwrap]").forEach(bind);
})();
