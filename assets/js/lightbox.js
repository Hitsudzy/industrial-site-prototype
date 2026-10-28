/*
 * Lightbox for the project gallery (project.html), no libraries.
 *
 *   [data-lightbox]          the gallery; its [data-lightbox-item] buttons open the dialog
 *   [data-lightbox-dialog]   role="dialog" aria-modal="true", hidden until opened
 *
 * The enlarged picture is a clone of the item's .gallery__media content (inline SVG
 * or the <img class="only-a/only-b"> pair, so the concept switch keeps working).
 * Closing: Esc, the close button, a click on the backdrop. ← / → page through the
 * items (wrapping around). Tab is kept inside the dialog, the rest of the page is
 * made inert, and focus returns to the item that opened the dialog.
 */
(function () {
  "use strict";

  function init() {
    var gallery = document.querySelector("[data-lightbox]");
    var dialog = document.querySelector("[data-lightbox-dialog]");
    if (!gallery || !dialog) return;

    var triggers = Array.prototype.slice.call(gallery.querySelectorAll("[data-lightbox-item]"));
    var n = triggers.length;
    if (!n) return;

    var media = dialog.querySelector("[data-lightbox-media]");
    var title = dialog.querySelector("[data-lightbox-title]");
    var sub = dialog.querySelector("[data-lightbox-sub]");
    var counter = dialog.querySelector("[data-lightbox-counter]");
    var closeBtn = dialog.querySelector("[data-lightbox-close]");
    var prevBtn = dialog.querySelector("[data-lightbox-prev]");
    var nextBtn = dialog.querySelector("[data-lightbox-next]");
    var backdrop = [dialog].concat(Array.prototype.slice.call(dialog.querySelectorAll("[data-lightbox-backdrop]")));

    var hasInert = "inert" in HTMLElement.prototype;
    var index = 0;
    var opener = null;
    var inerted = [];

    function pad(i) {
      return (i < 10 ? "0" : "") + i;
    }

    function text(root, selector) {
      var el = root.querySelector(selector);
      return el ? el.textContent.replace(/^\s*—\s*/, "").trim() : "";
    }

    function show(i) {
      index = (i + n) % n;
      var item = triggers[index];
      var source = item.querySelector(".gallery__media");
      var figure = item.closest("figure") || item;

      media.textContent = "";
      Array.prototype.forEach.call(source.children, function (el) {
        var copy = el.cloneNode(true);
        if (copy.tagName === "IMG") copy.removeAttribute("loading");
        media.appendChild(copy);
      });

      title.textContent = text(figure, ".gallery__title");
      sub.textContent = text(figure, ".gallery__sub");
      counter.innerHTML =
        '<span aria-hidden="true">' + pad(index + 1) + " / " + pad(n) + "</span>" +
        '<span class="visually-hidden">Изображение ' + (index + 1) + " из " + n + "</span>";
    }

    function setInert(on) {
      if (on) {
        Array.prototype.forEach.call(document.body.children, function (el) {
          if (el === dialog || el.tagName === "SCRIPT" || el.inert) return;
          el.inert = true;
          if (!hasInert) el.setAttribute("aria-hidden", "true"); /* old browser: hide at least from AT */
          inerted.push(el);
        });
      } else {
        inerted.forEach(function (el) {
          el.inert = false;
          el.removeAttribute("aria-hidden");
        });
        inerted = [];
      }
    }

    function focusables() {
      return [closeBtn, prevBtn, nextBtn].filter(function (el) {
        return el && !el.disabled && el.offsetParent !== null;
      });
    }

    function onKey(e) {
      if (e.key === "Escape" || e.key === "Esc") {
        e.preventDefault();
        e.stopPropagation();
        close();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        show(index - 1);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        show(index + 1);
      } else if (e.key === "Tab") {
        var list = focusables();
        if (!list.length) return;
        var first = list[0];
        var last = list[list.length - 1];
        var active = document.activeElement;
        if (!dialog.contains(active)) {
          e.preventDefault();
          first.focus();
        } else if (e.shiftKey && active === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && active === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    function open(i, trigger) {
      opener = trigger;
      show(i);
      dialog.hidden = false;
      document.documentElement.classList.add("has-lightbox");
      setInert(true);
      document.addEventListener("keydown", onKey, true);
      closeBtn.focus();
    }

    function close() {
      if (dialog.hidden) return;
      dialog.hidden = true;
      document.documentElement.classList.remove("has-lightbox");
      setInert(false);
      document.removeEventListener("keydown", onKey, true);
      media.textContent = "";
      if (opener) opener.focus();
      opener = null;
    }

    triggers.forEach(function (btn, i) {
      btn.addEventListener("click", function () {
        open(i, btn);
      });
    });
    closeBtn.addEventListener("click", close);
    prevBtn.addEventListener("click", function () { show(index - 1); });
    nextBtn.addEventListener("click", function () { show(index + 1); });
    dialog.addEventListener("click", function (e) {
      if (backdrop.indexOf(e.target) !== -1) close();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
