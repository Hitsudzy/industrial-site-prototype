/*
 * «Направить запрос» form (index.html#request; reusable on contacts.html).
 * Prototype only: nothing is sent anywhere. The script validates the fields on
 * the client, marks errors accessibly (aria-invalid + the error text linked via
 * aria-describedby, focus moves to the first wrong field) and, when everything is
 * filled in, announces "В прототипе форма не отправляется" in a role="status" region.
 * Without JS the browser's own `required` validation still works.
 * No dependencies, no network requests.
 */
(function () {
  "use strict";

  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE_CHARS = /^\+?[\d\s()\-]+$/;

  /* One rule per field name: returns an error message or "" */
  var RULES = {
    name: function (el) {
      var v = el.value.trim();
      if (!v) return "Укажите контактное лицо — как к вам обращаться.";
      if (v.length < 2) return "Имя слишком короткое — укажите хотя бы два символа.";
      return "";
    },
    contact: function (el) {
      var v = el.value.trim();
      if (!v) return "Укажите e-mail или телефон, чтобы мы могли ответить.";
      if (v.indexOf("@") >= 0) {
        return EMAIL.test(v) ? "" : "Проверьте e-mail: нужен адрес вида name@domain.ru.";
      }
      var digits = v.replace(/\D/g, "").length;
      if (PHONE_CHARS.test(v) && digits >= 10 && digits <= 15) return "";
      return "Проверьте e-mail или телефон: например, name@domain.ru или +7 900 000-00-00.";
    },
    task: function (el) {
      var v = el.value.trim();
      if (!v) return "Опишите задачу — хотя бы в одном-двух предложениях.";
      if (v.length < 10) return "Опишите задачу чуть подробнее — не меньше 10 символов.";
      return "";
    },
    consent: function (el) {
      return el.checked ? "" : "Без согласия на обработку персональных данных запрос не отправить.";
    }
  };

  function errorNode(el) {
    return document.getElementById(el.id + "-error");
  }

  function check(el) {
    var rule = RULES[el.name];
    if (!rule) return "";
    var msg = rule(el);
    var out = errorNode(el);
    if (msg) {
      el.setAttribute("aria-invalid", "true");
    } else {
      el.removeAttribute("aria-invalid");
    }
    if (out) out.textContent = msg;
    return msg;
  }

  function say(status, text, kind) {
    if (!status) return;
    status.classList.remove("is-error", "is-ok");
    status.textContent = "";
    /* re-announce even when the same text repeats */
    window.setTimeout(function () {
      status.textContent = text;
      if (kind) status.classList.add(kind);
    }, 60);
  }

  function errorsWord(n) {
    var m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return n + " поле";
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return n + " поля";
    return n + " полей";
  }

  function init(form) {
    var status = form.querySelector("[data-form-status]");
    var attempted = false;
    form.noValidate = true;

    function fields() {
      var list = [];
      for (var i = 0; i < form.elements.length; i++) {
        var el = form.elements[i];
        if (el.name && RULES[el.name]) list.push(el);
      }
      return list;
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      attempted = true;
      var bad = [];
      var list = fields();
      for (var i = 0; i < list.length; i++) {
        if (check(list[i])) bad.push(list[i]);
      }
      if (bad.length) {
        say(status, "Запрос не отправлен: исправьте " + errorsWord(bad.length) + " с ошибкой.", "is-error");
        bad[0].focus();
        return;
      }
      say(status, "В прототипе форма не отправляется. Проверка пройдена, данные никуда не переданы.", "is-ok");
    });

    /* After the first attempt, re-check a field as the visitor fixes it */
    function recheck(e) {
      var el = e.target;
      if (!attempted || !RULES[el.name]) return;
      check(el);
    }
    form.addEventListener("input", recheck);
    form.addEventListener("change", recheck);
  }

  function start() {
    var forms = document.querySelectorAll("[data-request-form]");
    for (var i = 0; i < forms.length; i++) init(forms[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
