(function () {
  function press(buttons, key) {
    buttons.forEach((b) => {
      b.setAttribute(
        "aria-pressed",
        b.dataset.moment === key ? "true" : "false"
      );
    });
  }

  function bindRoles(root) {
    const buttons = [...root.querySelectorAll("[data-moment]")];
    const cards = [...root.querySelectorAll("[data-role]")];
    const bagItems = [...root.querySelectorAll("[data-slug]")];
    const matchSlug = root.dataset.matchSlug || "";
    const caption = root.querySelector("[data-roles-caption]");

    function show(key) {
      root.dataset.moment = key;
      cards.forEach((el) => {
        el.dataset.on = el.dataset.role === key ? "1" : "0";
      });
      bagItems.forEach((el) => {
        if (key === "queryset") el.dataset.on = "1";
        else if (key === "instance")
          el.dataset.on = el.dataset.slug === matchSlug ? "1" : "0";
        else el.dataset.on = "0";
      });
      if (caption) {
        const fromBtn = buttons.find((b) => b.dataset.moment === key);
        caption.textContent = fromBtn ? fromBtn.dataset.caption || "" : "";
      }
      press(buttons, key);
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => show(b.dataset.moment))
    );
    show(root.dataset.start || "model");
  }

  function bindLookup(root) {
    const order = ["body", "search", "row"];
    const buttons = [...root.querySelectorAll("[data-moment]")];
    const steps = [...root.querySelectorAll("[data-step]")];
    const caption = root.querySelector("[data-lookup-caption]");

    function show(key) {
      root.dataset.moment = key;
      const idx = order.indexOf(key);
      steps.forEach((el) => {
        const i = order.indexOf(el.dataset.step);
        if (i < idx) el.dataset.on = "done";
        else if (i === idx) el.dataset.on = "1";
        else el.dataset.on = "0";
      });
      if (caption) {
        const fromBtn = buttons.find((b) => b.dataset.moment === key);
        caption.textContent = fromBtn ? fromBtn.dataset.caption || "" : "";
      }
      press(buttons, key);
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => show(b.dataset.moment))
    );
    show(root.dataset.start || "body");
  }

  document.querySelectorAll("[data-roles]").forEach(bindRoles);
  document.querySelectorAll("[data-lookup]").forEach(bindLookup);
})();
