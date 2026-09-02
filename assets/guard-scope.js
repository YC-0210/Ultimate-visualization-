/*
  guard-scope: show the same lines of code under different try/except scopes,
  and what each scope does to the app and to the trace.

  Data lives in the HTML, not here, so any lesson can reuse it.

    <figure class="guard" data-guard data-start="none">
      <div class="guard-moments">
        <button type="button" data-moment="none" data-caption="...">no guard</button>
      </div>
      <div class="guard-stack">
        <p class="guard-line" data-role="work"  data-in="wide">response = self.get_response(request)</p>
        <p class="guard-line" data-role="books" data-in="wide tight">captured["response"] = {...}</p>
      </div>
      <p class="guard-caption" data-guard-caption></p>
    </figure>

  data-in is a space-separated list of moments in which that line sits inside
  the guard. data-role marks what the line is: "work" (the observed call) or
  "books" (our own bookkeeping). Swallowing a "work" line is the mistake.
*/
(function () {
  function bind(root) {
    const buttons = [...root.querySelectorAll("[data-moment]")];
    const lines = [...root.querySelectorAll(".guard-line")];
    const slots = [...root.querySelectorAll("[data-when]")];
    const caption = root.querySelector("[data-guard-caption]");

    function show(key) {
      root.dataset.moment = key;

      lines.forEach((line) => {
        const inside = (line.dataset.in || "").split(/\s+/).includes(key);
        line.dataset.guarded = inside ? "1" : "0";
        // A guard around the observed call swallows the app's own errors.
        line.dataset.wrong = inside && line.dataset.role === "work" ? "1" : "0";
      });

      slots.forEach((el) => {
        el.hidden = el.dataset.when !== key;
      });

      const active = buttons.find((b) => b.dataset.moment === key);
      if (caption) caption.textContent = active ? active.dataset.caption || "" : "";
      buttons.forEach((b) => {
        b.setAttribute("aria-pressed", b.dataset.moment === key ? "true" : "false");
      });
    }

    buttons.forEach((b) => b.addEventListener("click", () => show(b.dataset.moment)));
    show(root.dataset.start || (buttons[0] && buttons[0].dataset.moment));
  }

  document.querySelectorAll("[data-guard]").forEach(bind);
})();
