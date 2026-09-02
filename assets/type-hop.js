(function () {
  function bind(root) {
    const buttons = [...root.querySelectorAll("[data-moment]")];
    const caption = root.querySelector("[data-typehop-caption]");
    const slots = [...root.querySelectorAll("[data-when]")];

    function show(key) {
      root.dataset.moment = key;
      slots.forEach((el) => {
        el.hidden = el.dataset.when !== key;
      });
      if (caption) {
        const fromBtn = buttons.find((b) => b.dataset.moment === key);
        caption.textContent = fromBtn ? fromBtn.dataset.caption || "" : "";
      }
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
    show(root.dataset.start || "body");
  }

  document.querySelectorAll("[data-typehop]").forEach(bind);
})();
