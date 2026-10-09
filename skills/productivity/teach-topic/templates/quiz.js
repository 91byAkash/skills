// assets/quiz.js: multiple-choice questions with instant feedback.
// Markup:
// <div class="quiz" data-answer="2">
//   <p>Question?</p>
//   <button data-why="Why this is wrong">Option one</button>
//   <button data-why="Correct because ...">Option two</button>
//   <p class="feedback" aria-live="polite"></p>
// </div>
// data-answer is the 1-based index of the correct button.
(function () {
  function setup(quiz) {
    var buttons = Array.prototype.slice.call(quiz.querySelectorAll("button"));
    var answer = parseInt(quiz.getAttribute("data-answer"), 10) - 1;
    var feedback = quiz.querySelector(".feedback");
    buttons.forEach(function (btn, i) {
      btn.addEventListener("click", function () {
        var right = i === answer;
        btn.setAttribute("data-result", right ? "right" : "wrong");
        if (feedback) {
          var why = btn.getAttribute("data-why") || "";
          feedback.textContent = (right ? "Correct. " : "Not quite. ") + why;
        }
        if (right) {
          buttons.forEach(function (b) { b.disabled = true; });
          record(quiz, true);
        } else {
          record(quiz, false);
        }
      });
    });
  }
  function record(quiz, right) {
    try {
      var key = "quiz:" + location.pathname + ":" + (quiz.id || Array.prototype.indexOf.call(document.querySelectorAll(".quiz"), quiz));
      var prev = JSON.parse(localStorage.getItem(key) || '{"tries":0}');
      prev.tries += 1;
      if (right && prev.firstRight === undefined) prev.firstRight = prev.tries === 1;
      localStorage.setItem(key, JSON.stringify(prev));
    } catch (e) { /* storage unavailable: feedback still works */ }
  }
  document.querySelectorAll(".quiz").forEach(setup);
})();
