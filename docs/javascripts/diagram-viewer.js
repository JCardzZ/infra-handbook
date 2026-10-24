// Study viewer for diagrams: architecture SVGs (figure.hb-diagram img) and
// Mermaid blocks.
//
// Each diagram gets a "Ver en detalle" button; the button or a click on the
// diagram opens a full-screen viewer with zoom toward the cursor (Ctrl+wheel,
// pinch, double click, +/- keys), pan (wheel, drag, arrows), fit-to-screen and
// real size (1:1). The SVG is resized rather than CSS-scaled, so it stays sharp
// at any zoom.
//
// Material renders Mermaid into a closed shadow root the page cannot read, so
// each block's source is saved before Material replaces it, and the viewer
// renders it again with the same mermaid global. That SVG is inserted inline
// (not as an <img>) so Material's theme variables still color it.

(function () {
  var MAX_SCALE = 6;

  function enhance() {
    document.querySelectorAll(".hb-diagram img:not([data-hb-viewer])").forEach(function (img) {
      img.dataset.hbViewer = "1";
      var frame = document.createElement("span");
      frame.className = "hb-diagram__frame";
      img.parentNode.insertBefore(frame, img);
      frame.appendChild(img);

      var button = document.createElement("button");
      button.type = "button";
      button.className = "hb-diagram__open";
      setOpenButton(button);
      frame.appendChild(button);

      var figure = img.closest("figure");
      var caption = figure && figure.querySelector("figcaption");
      var title = caption ? caption.textContent.replace(/\s*Toca o haz clic.*$/, "") : img.alt;
      var open = function () {
        openViewer({ src: img.currentSrc || img.src, alt: img.alt, title: title, opener: button, from: img.getBoundingClientRect() });
      };
      button.addEventListener("click", open);
      img.addEventListener("click", open);
    });

    enhanceMermaid();
  }

  // Superfences emits <pre class="mermaid"><code>; Material drops the class
  // while it waits for the Mermaid script, so a <pre> outside a highlighted
  // code block counts too.
  function enhanceMermaid() {
    document.querySelectorAll(".md-typeset pre").forEach(function (pre) {
      if (pre.closest(".highlight, .hb-mermaid")) return;
      if (!pre.firstElementChild || pre.firstElementChild.tagName !== "CODE") return;

      var source = pre.textContent;
      var wrap = document.createElement("div");
      wrap.className = "hb-mermaid";
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre); // Material swaps this <pre> for the diagram in place

      var button = document.createElement("button");
      button.type = "button";
      button.className = "hb-diagram__open";
      setOpenButton(button);
      wrap.appendChild(button);

      var accTitle = /accTitle:\s*(.+)/.exec(source);
      var open = function (e) {
        if (e.target.closest("a")) return;
        var shown = wrap.querySelector(".mermaid") || wrap;
        openViewer({ mermaid: source, alt: accTitle ? accTitle[1] : "", title: accTitle ? accTitle[1] : "", opener: button, from: shown.getBoundingClientRect() });
      };
      wrap.addEventListener("click", open);
    });
  }

  var mermaidIds = 0;

  // Small icon-only button (Material "arrow-expand"); the name lives in
  // aria-label and the tooltip.
  function setOpenButton(button) {
    button.setAttribute("aria-label", "Ver en detalle");
    button.title = "Ver en detalle";
    button.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 21v-2H6.41l4.5-4.5-1.41-1.41-4.5 4.5V14H3v7zm4.5-10.09 4.5-4.5V10h2V3h-7v2h3.59l-4.5 4.5z"/></svg>';
  }

  function openViewer(opts) {
    var src = opts.src;
    var title = opts.title;
    var opener = opts.opener;
    var root = document.createElement("div");
    root.className = "hb-viewer";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-modal", "true");
    root.setAttribute("aria-label", "Visor de diagrama");
    root.innerHTML =
      '<div class="hb-viewer__bar">' +
      '<p class="hb-viewer__title"></p>' +
      '<div class="hb-viewer__tools">' +
      '<button type="button" data-act="out" aria-label="Alejar" title="Alejar (−)">−</button>' +
      '<output class="hb-viewer__zoom" aria-live="polite">100%</output>' +
      '<button type="button" data-act="in" aria-label="Acercar" title="Acercar (+)">+</button>' +
      '<button type="button" data-act="fit" title="Ajustar a la pantalla (0)">Ajustar</button>' +
      '<button type="button" data-act="real" title="Tamaño real (1)">1:1</button>' +
      '<a class="hb-viewer__svg" target="_blank" rel="noopener" title="Abrir el SVG en otra pestaña">SVG</a>' +
      '<button type="button" data-act="close" class="hb-viewer__close" aria-label="Cerrar" title="Cerrar (Esc)">✕</button>' +
      "</div></div>" +
      '<div class="hb-viewer__stage"></div>' +
      '<p class="hb-viewer__hint">Rueda o arrastrar: mover · Ctrl + rueda o pellizco: zoom · doble clic: acercar · ' +
      "<kbd>0</kbd> ajustar · <kbd>Esc</kbd> cerrar</p>";

    root.querySelector(".hb-viewer__title").textContent = title || "";
    var svgLink = root.querySelector(".hb-viewer__svg");
    if (src) svgLink.href = src;
    else svgLink.remove(); // a Mermaid SVG depends on the page's theme variables
    var stage = root.querySelector(".hb-viewer__stage");
    var zoomLabel = root.querySelector(".hb-viewer__zoom");
    var image = document.createElement(src ? "img" : "div");
    image.className = "hb-viewer__img" + (src ? "" : " hb-viewer__img--mermaid");
    if (src) {
      image.draggable = false;
      image.alt = opts.alt || "";
    } else {
      image.setAttribute("role", "img");
      image.setAttribute("aria-label", opts.alt || "Diagrama");
    }
    stage.appendChild(image);

    document.body.appendChild(root);
    var hint = root.querySelector(".hb-viewer__hint");
    setTimeout(function () { hint.classList.add("is-faded"); }, 4000);
    var previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";

    var natural = { w: 1, h: 1 };
    var view = { s: 1, x: 0, y: 0 };
    var fitScale = 1;

    function apply() {
      image.style.width = natural.w * view.s + "px";
      image.style.height = natural.h * view.s + "px";
      image.style.transform = "translate(" + view.x + "px," + view.y + "px)";
      zoomLabel.textContent = Math.round(view.s * 100) + "%";
    }

    // The stage fills the whole screen and the toolbar floats over its top, so
    // the free area for the diagram is everything below the toolbar.
    // The hint floats at the bottom (hidden on phones), so that strip is kept free too.
    var bar = root.querySelector(".hb-viewer__bar");
    function area() {
      var r = stage.getBoundingClientRect();
      var top = bar.offsetHeight + 10;
      var bottom = (hint.offsetHeight ? hint.offsetHeight + 16 : 0) + 12;
      return { x: 12, y: top, w: r.width - 24, h: r.height - top - bottom };
    }

    function center(scale) {
      var a = area();
      view.s = scale;
      view.x = a.x + (a.w - natural.w * scale) / 2;
      view.y = a.y + (a.h - natural.h * scale) / 2;
      apply();
    }

    // Fit fills the free area; small diagrams (most Mermaid ones) grow up to 3x,
    // which stays sharp because the SVG is redrawn at the new size.
    function fit() {
      var a = area();
      fitScale = Math.min(a.w / natural.w, a.h / natural.h, 3);
      center(fitScale);
    }

    // First view: the whole diagram, filling the screen. Only a very tall one,
    // whose text would be too small fitted whole, opens at real size (or as
    // wide as fits) aligned to the top; "Ajustar" still shows it whole.
    function initialView() {
      fit();
      var a = area();
      var widthScale = Math.min(a.w / natural.w, 1);
      if (fitScale < 0.6 && widthScale > fitScale * 1.15) {
        view.s = widthScale;
        view.x = a.x + (a.w - natural.w * widthScale) / 2;
        view.y = a.y;
        apply();
      }
    }

    // Entrance: the diagram slides and grows from where it sits on the page to
    // its first view. Any wheel, drag, key or button press stops it.
    var anim = null;
    function stopAnim() {
      if (anim) cancelAnimationFrame(anim);
      anim = null;
    }

    function enter() {
      var from = opts.from;
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (!from || !from.width || reduce) return;
      var target = { s: view.s, x: view.x, y: view.y };
      var r = stage.getBoundingClientRect();
      var s0 = Math.min(from.width / natural.w, from.height / natural.h);
      var start = {
        s: s0,
        x: from.left - r.left + (from.width - natural.w * s0) / 2,
        y: from.top - r.top + (from.height - natural.h * s0) / 2,
      };
      var t0 = performance.now();
      var duration = 450;
      function step(now) {
        var k = Math.min(1, (now - t0) / duration);
        var e = 1 - Math.pow(1 - k, 3); // ease-out
        view.s = start.s + (target.s - start.s) * e;
        view.x = start.x + (target.x - start.x) * e;
        view.y = start.y + (target.y - start.y) * e;
        apply();
        anim = k < 1 ? requestAnimationFrame(step) : null;
      }
      step(t0);
    }

    function zoomAt(factor, cx, cy) {
      stopAnim();
      var r = stage.getBoundingClientRect();
      if (cx === undefined) {
        cx = r.width / 2;
        cy = r.height / 2;
      }
      var min = Math.min(fitScale, 1) / 2;
      var next = Math.min(MAX_SCALE, Math.max(min, view.s * factor));
      view.x = cx - (cx - view.x) * (next / view.s);
      view.y = cy - (cy - view.y) * (next / view.s);
      view.s = next;
      apply();
    }

    if (src) {
      image.onload = function () {
        natural.w = image.naturalWidth || 800;
        natural.h = image.naturalHeight || 600;
        initialView();
        enter();
      };
      image.src = src;
    } else {
      renderMermaid(opts.mermaid, image, function (w, h) {
        natural.w = w;
        natural.h = h;
        initialView();
        enter();
      });
    }

    // Wheel scrolls the diagram (tall ones open at the top). Ctrl+wheel, which
    // is also what a trackpad pinch sends, zooms toward the cursor.
    stage.addEventListener(
      "wheel",
      function (e) {
        e.preventDefault();
        stopAnim();
        var unit = e.deltaMode === 1 ? 16 : 1;
        if (e.ctrlKey || e.metaKey) {
          var r = stage.getBoundingClientRect();
          zoomAt(Math.exp(-e.deltaY * unit * 0.01), e.clientX - r.left, e.clientY - r.top);
        } else {
          view.x -= (e.shiftKey ? e.deltaY : e.deltaX) * unit;
          view.y -= (e.shiftKey ? 0 : e.deltaY) * unit;
          apply();
        }
      },
      { passive: false }
    );

    // Drag to pan with one pointer, pinch to zoom with two.
    var pointers = new Map();
    var pinch = null;
    stage.addEventListener("pointerdown", function (e) {
      stopAnim();
      stage.setPointerCapture(e.pointerId);
      pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      stage.classList.add("is-dragging");
      if (pointers.size === 2) pinch = pinchState();
    });
    stage.addEventListener("pointermove", function (e) {
      if (!pointers.has(e.pointerId)) return;
      var prev = pointers.get(e.pointerId);
      pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pointers.size === 1) {
        view.x += e.clientX - prev.x;
        view.y += e.clientY - prev.y;
        apply();
      } else if (pointers.size === 2 && pinch) {
        var now = pinchState();
        var r = stage.getBoundingClientRect();
        view.x += now.cx - pinch.cx;
        view.y += now.cy - pinch.cy;
        zoomAt(now.d / pinch.d, now.cx - r.left, now.cy - r.top);
        pinch = now;
      }
    });
    function release(e) {
      pointers.delete(e.pointerId);
      pinch = pointers.size === 2 ? pinchState() : null;
      if (pointers.size === 0) stage.classList.remove("is-dragging");
    }
    stage.addEventListener("pointerup", release);
    stage.addEventListener("pointercancel", release);
    function pinchState() {
      var p = Array.from(pointers.values());
      return {
        d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) || 1,
        cx: (p[0].x + p[1].x) / 2,
        cy: (p[0].y + p[1].y) / 2,
      };
    }

    stage.addEventListener("dblclick", function (e) {
      var r = stage.getBoundingClientRect();
      zoomAt(2, e.clientX - r.left, e.clientY - r.top);
    });

    root.querySelector(".hb-viewer__tools").addEventListener("click", function (e) {
      var act = e.target.closest("[data-act]");
      if (!act) return;
      stopAnim();
      viaKeyboard = e.detail === 0; // keyboard "clicks" report no pointer clicks
      ({
        in: function () { zoomAt(1.4); },
        out: function () { zoomAt(1 / 1.4); },
        fit: fit,
        real: function () { center(1); },
        close: close,
      })[act.dataset.act]();
    });

    function onKey(e) {
      var step = 80;
      var actions = {
        Escape: function () { viaKeyboard = true; close(); },
        "+": function () { zoomAt(1.4); },
        "=": function () { zoomAt(1.4); },
        "-": function () { zoomAt(1 / 1.4); },
        "0": fit,
        "1": function () { center(1); },
        ArrowLeft: function () { view.x += step; apply(); },
        ArrowRight: function () { view.x -= step; apply(); },
        ArrowUp: function () { view.y += step; apply(); },
        ArrowDown: function () { view.y -= step; apply(); },
      };
      if (actions[e.key]) {
        stopAnim();
        e.preventDefault();
        e.stopPropagation(); // keep Material's own shortcuts (search, prev/next page) out
        actions[e.key]();
      }
    }
    document.addEventListener("keydown", onKey, true);
    window.addEventListener("resize", fit);

    var viaKeyboard = false;
    function close() {
      document.removeEventListener("keydown", onKey, true);
      window.removeEventListener("resize", fit);
      document.documentElement.style.overflow = previousOverflow;
      root.remove();
      // Back to the button without a focus ring after a mouse or touch close.
      if (opener) opener.focus({ focusVisible: viaKeyboard });
    }

    root.querySelector(".hb-viewer__close").focus();
  }

  function renderMermaid(source, container, done) {
    if (typeof mermaid === "undefined" || !mermaid.render) {
      container.textContent = "Mermaid todavía no cargó; intenta de nuevo en un momento.";
      done(320, 80);
      return;
    }
    mermaid.render("hb_viewer_" + mermaidIds++, source).then(function (out) {
      container.innerHTML = out.svg;
      var svg = container.querySelector("svg");
      var box = svg.viewBox && svg.viewBox.baseVal;
      var w = box && box.width ? box.width : svg.getBoundingClientRect().width;
      var h = box && box.height ? box.height : svg.getBoundingClientRect().height;
      // Let the container's size drive the drawing; viewBox keeps proportions.
      svg.removeAttribute("style");
      svg.setAttribute("width", "100%");
      svg.setAttribute("height", "100%");
      done(w, h);
    });
  }

  // Material's instant navigation swaps pages without a full reload.
  if (window.document$) document$.subscribe(enhance);
  else document.addEventListener("DOMContentLoaded", enhance);
})();
