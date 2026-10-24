// Study path on the home page: per-step "completed" toggles, a progress bar and
// a rail that fills up to the last completed step. Progress lives in this
// browser's localStorage only; without JS the path still renders as a list.

(function () {
  var KEY = "hb-study-path";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function save(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) {
      /* private mode or storage blocked: progress just isn't remembered */
    }
  }

  function init() {
    var path = document.querySelector(".hb-path");
    if (!path || path.dataset.ready) return;
    path.dataset.ready = "1";

    var list = path.querySelector(".hb-path__steps");
    var steps = Array.prototype.slice.call(path.querySelectorAll(".hb-step"));
    var state = load();

    var progress = document.createElement("div");
    progress.className = "hb-progress";
    progress.innerHTML =
      '<div class="hb-progress__text"><strong></strong><button type="button" class="hb-progress__reset">Reiniciar</button></div>' +
      '<div class="hb-progress__bar" aria-hidden="true"><span></span></div>';
    path.parentNode.insertBefore(progress, path);
    var label = progress.querySelector("strong");
    var bar = progress.querySelector(".hb-progress__bar span");
    var reset = progress.querySelector(".hb-progress__reset");

    steps.forEach(function (step) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "hb-step__toggle";
      button.addEventListener("click", function () {
        var key = step.dataset.step;
        if (state[key]) delete state[key];
        else state[key] = true;
        save(state);
        render();
      });
      step.appendChild(button);
    });

    reset.addEventListener("click", function () {
      state = {};
      save(state);
      render();
    });

    function render() {
      var done = 0;
      var last = null;
      var next = null;
      steps.forEach(function (step) {
        var isDone = !!state[step.dataset.step];
        var button = step.querySelector(".hb-step__toggle");
        step.classList.toggle("is-done", isDone);
        step.classList.remove("is-next");
        button.setAttribute("aria-pressed", String(isDone));
        button.textContent = isDone ? "Completada" : "Marcar como completada";
        if (isDone) {
          done++;
          last = step;
        } else if (!next) {
          next = step;
        }
      });
      if (next) next.classList.add("is-next");

      var pct = Math.round((done / steps.length) * 100);
      label.textContent =
        done === steps.length
          ? "Ruta completa: " + done + " de " + steps.length + " etapas"
          : done + " de " + steps.length + " etapas completadas";
      bar.style.width = pct + "%";
      reset.hidden = done === 0;

      // Rail fill ends at the marker of the last completed step.
      var fill = last ? last.offsetTop + 28 : 0;
      list.style.setProperty("--hb-fill", fill + "px");
    }

    render();
    window.addEventListener("resize", render);

    // Reveal steps as they scroll into view (skipped when motion is reduced).
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduce && "IntersectionObserver" in window) {
      path.classList.add("hb-path--animate");
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { rootMargin: "0px 0px -10% 0px" }
      );
      steps.forEach(function (step) {
        observer.observe(step);
      });
    }
  }

  // Material's instant navigation swaps pages without a full reload.
  if (window.document$) document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
