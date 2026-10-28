/*
 * Runs synchronously in <head>, before first paint, so the page never flashes
 * the wrong concept. Order of precedence:
 *   1. URL parameter ?c=a|b   (shareable links)
 *   2. localStorage            (choice remembered between visits)
 *   3. default "a"
 * localStorage may be unavailable (private mode, file://, blocked storage),
 * so every access is wrapped in try/catch.
 */
(function () {
  var KEY = "proto-concept";
  var VALID = { a: true, b: true };
  var root = document.documentElement;
  var concept = null;

  root.classList.remove("no-js");
  root.classList.add("js");

  try {
    var fromUrl = new URLSearchParams(window.location.search).get("c");
    if (fromUrl && VALID[fromUrl.toLowerCase()]) concept = fromUrl.toLowerCase();
  } catch (e) { /* old browser: ignore */ }

  if (!concept) {
    try {
      var stored = window.localStorage.getItem(KEY);
      if (stored && VALID[stored]) concept = stored;
    } catch (e) { /* storage blocked */ }
  }

  if (!concept) concept = "a";

  try {
    window.localStorage.setItem(KEY, concept);
  } catch (e) { /* storage blocked: the URL parameter still carries the choice */ }

  root.setAttribute("data-concept", concept);
})();
