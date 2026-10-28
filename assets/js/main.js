/*
 * Shared behaviour for every page:
 *   - concept switcher A/B (button in the corner)
 *   - keeps the concept across page transitions: internal links get ?c=<concept>
 *     and the choice is stored in localStorage (both, so it survives even when
 *     storage is blocked)
 *   - mobile menu toggle
 *   - current year in the footer
 * No dependencies, no network requests.
 */
(function () {
  "use strict";

  var KEY = "proto-concept";
  var CONCEPTS = {
    a: { code: "A", name: "«инженерный тёмный»" },
    b: { code: "B", name: "«корпоративный светлый»" }
  };
  var root = document.documentElement;

  function current() {
    var c = root.getAttribute("data-concept");
    return CONCEPTS[c] ? c : "a";
  }

  function other(c) {
    return c === "a" ? "b" : "a";
  }

  function store(c) {
    try {
      window.localStorage.setItem(KEY, c);
    } catch (e) { /* storage blocked */ }
  }

  /* Is this href a link to another page of the prototype (relative .html)? */
  function isInternalPage(href) {
    if (!href) return false;
    if (/^[a-z][a-z0-9+.-]*:/i.test(href)) return false; // http:, mailto:, tel:, ...
    if (href.charAt(0) === "#" || href.indexOf("//") === 0) return false;
    var path = href.split("#")[0].split("?")[0];
    return /\.html$/i.test(path) || path === "" || /\/$/.test(path);
  }

  function withConcept(href, c) {
    var hashAt = href.indexOf("#");
    var hash = hashAt >= 0 ? href.slice(hashAt) : "";
    var rest = hashAt >= 0 ? href.slice(0, hashAt) : href;
    var qAt = rest.indexOf("?");
    var path = qAt >= 0 ? rest.slice(0, qAt) : rest;
    var query = qAt >= 0 ? rest.slice(qAt + 1) : "";
    var parts = query
      ? query.split("&").filter(function (p) { return p && p.split("=")[0] !== "c"; })
      : [];
    parts.push("c=" + c);
    return path + "?" + parts.join("&") + hash;
  }

  function syncLinks(c) {
    var links = document.querySelectorAll("a[href]");
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      var base = a.getAttribute("data-href");
      if (base === null) {
        base = a.getAttribute("href");
        if (!isInternalPage(base)) continue;
        a.setAttribute("data-href", base);
      }
      a.setAttribute("href", withConcept(base, c));
    }
  }

  function syncUrl(c) {
    try {
      var url = new URL(window.location.href);
      if (url.searchParams.get("c") === c) return;
      url.searchParams.set("c", c);
      window.history.replaceState(window.history.state, "", url.toString());
    } catch (e) { /* file:// in some browsers, very old browsers */ }
  }

  function syncButton(btn, c) {
    var now = CONCEPTS[c];
    var next = CONCEPTS[other(c)];
    btn.setAttribute(
      "aria-label",
      "Концепция оформления: " + now.code + " " + now.name +
        ". Переключить на " + next.code + " " + next.name
    );
    btn.setAttribute("title", "Переключить на концепцию " + next.code + " " + next.name);
    var opts = btn.querySelectorAll("[data-concept-opt]");
    for (var i = 0; i < opts.length; i++) {
      opts[i].classList.toggle("is-active", opts[i].getAttribute("data-concept-opt") === c);
    }
  }

  function apply(c, announce) {
    root.setAttribute("data-concept", c);
    store(c);
    syncLinks(c);
    syncUrl(c);
    var btn = document.querySelector("[data-concept-toggle]");
    if (btn) syncButton(btn, c);
    var status = document.querySelector("[data-concept-status]");
    if (status && announce) {
      status.textContent = "Включена концепция " + CONCEPTS[c].code + " " + CONCEPTS[c].name;
    }
  }

  function initConcept() {
    var btn = document.querySelector("[data-concept-toggle]");
    if (btn) {
      btn.hidden = false;
      btn.addEventListener("click", function () {
        apply(other(current()), true);
      });
    }
    apply(current(), false);

    /* Another tab changed the concept: follow it */
    window.addEventListener("storage", function (e) {
      if (e.key === KEY && CONCEPTS[e.newValue] && e.newValue !== current()) {
        apply(e.newValue, false);
      }
    });
  }

  function initMenu() {
    var header = document.querySelector(".site-header");
    var toggle = document.querySelector("[data-nav-toggle]");
    if (!header || !toggle) return;

    function setOpen(open) {
      header.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Закрыть меню" : "Открыть меню");
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && header.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
    var wide = window.matchMedia("(min-width: 1100px)");
    var onChange = function () { if (wide.matches) setOpen(false); };
    if (wide.addEventListener) wide.addEventListener("change", onChange);
    else if (wide.addListener) wide.addListener(onChange);
  }

  function initYear() {
    var nodes = document.querySelectorAll("[data-year]");
    var y = String(new Date().getFullYear());
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = y;
  }

  function init() {
    initConcept();
    initMenu();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
