(function () {
  function bindQuiz(root) {
    const buttons = [...root.querySelectorAll("[data-answer]")];
    const feedback = root.querySelector(".quiz-feedback");
    const explainRight = root.dataset.explainRight || "Correct.";
    const explainWrong = root.dataset.explainWrong || "Not that one.";

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        if (root.dataset.locked === "1") return;
        root.dataset.locked = "1";
        const right = btn.dataset.correct === "1";
        buttons.forEach((b) => {
          b.disabled = true;
          if (b.dataset.correct === "1") b.dataset.state = "right";
          else if (b === btn) b.dataset.state = "wrong";
        });
        feedback.hidden = false;
        feedback.dataset.kind = right ? "right" : "wrong";
        feedback.textContent = right ? explainRight : explainWrong;
      });
    });
  }

  document.querySelectorAll("[data-quiz]").forEach(bindQuiz);
})();
