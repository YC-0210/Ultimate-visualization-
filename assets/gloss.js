(function () {
  function close(root) {
    const btn = root.querySelector(".gloss-term");
    const pop = root.querySelector(".gloss-pop");
    root.classList.remove("is-open");
    btn.setAttribute("aria-expanded", "false");
    pop.hidden = true;
  }

  function closeAll(except) {
    document.querySelectorAll("[data-gloss].is-open").forEach((root) => {
      if (root !== except) close(root);
    });
  }

  function bind(root, i) {
    const btn = root.querySelector(".gloss-term");
    const pop = root.querySelector(".gloss-pop");
    const popId = pop.id || "gloss-pop-" + i;
    pop.id = popId;
    btn.setAttribute("aria-controls", popId);
    btn.setAttribute("aria-expanded", "false");
    pop.hidden = true;

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = root.classList.contains("is-open");
      closeAll();
      if (!open) {
        root.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
        pop.hidden = false;
        pop.removeAttribute("hidden");
      }
    });
  }

  document.querySelectorAll("[data-gloss]").forEach(bind);

  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-gloss]")) return;
    closeAll();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAll();
  });
})();
