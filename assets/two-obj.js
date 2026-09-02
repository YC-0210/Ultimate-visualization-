(function () {
  const SNAPSHOTS = {
    before: {
      responseState: "empty",
      status: "not yet",
      headers: "not yet",
      content: "not yet",
      size: "not yet",
      caption:
        "get_response has not returned. You already have the request. There is no response object yet.",
    },
    after: {
      responseState: "live",
      status: "200",
      headers: 'Content-Type: application/json · …',
      content: 'b\'{"slug": "經典原味鍋", …}\'',
      size: "len(content) — a byte count",
      caption:
        "Same request still in __call__. get_response returned a new object. Status, headers, content, and size live on that object — not on the request.",
    },
  };

  function bind(root) {
    const responseObj = root.querySelector("[data-obj='response']");
    const statusEl = root.querySelector("[data-fact='status']");
    const headersEl = root.querySelector("[data-fact='headers']");
    const contentEl = root.querySelector("[data-fact='content']");
    const sizeEl = root.querySelector("[data-fact='size']");
    const caption = root.querySelector("[data-twobox-caption]");
    const buttons = [...root.querySelectorAll("[data-moment]")];

    function show(key) {
      const snap = SNAPSHOTS[key];
      if (!snap) return;
      responseObj.dataset.state = snap.responseState;
      statusEl.textContent = snap.status;
      headersEl.textContent = snap.headers;
      contentEl.textContent = snap.content;
      sizeEl.textContent = snap.size;
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
    show(root.dataset.start || "before");
  }

  document.querySelectorAll("[data-twobox]").forEach(bind);
})();
