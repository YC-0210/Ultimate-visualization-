(function () {
  const SNAPSHOTS = {
    before: {
      label: "1 · Request-phase middleware (your P1.1 print lives here)",
      body:
        "path: /api/menuitem/經典原味鍋/\n" +
        "method: GET\n" +
        "resolver_match: <not set>\n" +
        "\n" +
        "URL resolving has not run. Django is still walking the middleware onion inward.",
    },
    resolve: {
      label: "2 · Inside Django's handler, after the onion's inward pass",
      body:
        "Django calls resolver.resolve(path)\n" +
        "then sets request.resolver_match = match\n" +
        "then process_view() hooks, then the view.\n" +
        "\n" +
        "This is the first moment the match exists.",
    },
    after: {
      label: "3 · Response-phase middleware (after get_response returns)",
      body:
        "path: /api/menuitem/經典原味鍋/\n" +
        "resolver_match.route: api/menuitem/<str:slug>/\n" +
        "resolver_match.url_name: menuitem_detail\n" +
        "resolver_match.kwargs: {\"slug\": \"經典原味鍋\"}\n" +
        "match.func.view_class: menuitemDetail\n" +
        "\n" +
        "Same request object. The match is still on it. This is the smallest change to your P1.1 middleware.",
    },
  };

  function bind(root) {
    const out = root.querySelector(".lifecycle-out");
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      out.textContent = snap.label + "\n\n" + snap.body;
      buttons.forEach((b) => {
        b.setAttribute("aria-pressed", b.dataset.moment === key ? "true" : "false");
      });
    }

    buttons.forEach((b) => b.addEventListener("click", () => show(b.dataset.moment)));
    show(root.dataset.start || "before");
  }

  document.querySelectorAll("[data-lifecycle]").forEach(bind);
})();
