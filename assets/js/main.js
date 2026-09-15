/* Wealthymind Research — progressive enhancement only.
   Every feature below degrades to working HTML if this file fails to load. */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ---------------------------------------------------------- funding signal */

  /* The bulb brightens as the pointer moves down the stages and reaches full
     only at "Capital in the account". Hover previews, click commits, and focus
     mirrors hover so the keyboard gets the same feedback — hover alone would
     leave keyboard and touch users with a dead illustration. */
  document.querySelectorAll("[data-signal]").forEach(function (signal) {
    var steps = Array.prototype.slice.call(
      signal.querySelectorAll("[data-signal-step]")
    );
    var status = signal.querySelector("[data-signal-status]");
    if (!steps.length) return;

    var GLOW = { 0: 0, 1: 0.12, 2: 0.4, 3: 0.7, 4: 1 };
    var committed = 0; // nothing chosen yet, so the bulb starts dark

    function stageOf(btn) {
      return Number(btn.dataset.signalStep);
    }

    function paint(stage) {
      signal.dataset.stage = String(stage);
      signal.style.setProperty("--lit", String(GLOW[stage]));
      if (status) {
        status.textContent = stage === 4 ? "Funded" : "Not yet funded";
      }
    }

    function commit(stage) {
      committed = stage;
      steps.forEach(function (btn) {
        btn.setAttribute("aria-pressed", String(stageOf(btn) === stage));
      });
      paint(stage);
    }

    steps.forEach(function (btn, index) {
      // pointerenter rather than mouseenter so pen and touch behave sensibly
      btn.addEventListener("pointerenter", function () {
        paint(stageOf(btn));
      });

      btn.addEventListener("focus", function () {
        paint(stageOf(btn));
      });

      btn.addEventListener("click", function () {
        commit(stageOf(btn));
      });

      btn.addEventListener("keydown", function (event) {
        var delta =
          event.key === "ArrowRight" || event.key === "ArrowDown"
            ? 1
            : event.key === "ArrowLeft" || event.key === "ArrowUp"
            ? -1
            : 0;
        if (!delta) return;
        event.preventDefault();
        var next = steps[(index + delta + steps.length) % steps.length];
        next.focus(); // the focus handler repaints
      });
    });

    // leaving the group settles back to whatever was actually chosen
    signal.addEventListener("pointerleave", function () {
      paint(committed);
    });

    signal.addEventListener(
      "focusout",
      function (event) {
        if (!signal.contains(event.relatedTarget)) paint(committed);
      },
      true
    );

    paint(0);
  });

  /* --------------------------------------------------------------- drawer */

  var drawer = document.getElementById("mobile-drawer");
  var openBtn = document.querySelector("[data-drawer-open]");
  var lastFocused = null;

  function focusables() {
    if (!drawer) return [];
    return Array.prototype.slice
      .call(
        drawer.querySelectorAll(
          'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      )
      .filter(function (el) {
        return el.offsetParent !== null;
      });
  }

  function openDrawer() {
    if (!drawer) return;
    lastFocused = document.activeElement;
    drawer.hidden = false;
    document.body.style.overflow = "hidden";
    if (openBtn) openBtn.setAttribute("aria-expanded", "true");
    var first = focusables()[0];
    if (first) first.focus();
    document.addEventListener("keydown", onDrawerKeydown);
  }

  function closeDrawer() {
    if (!drawer || drawer.hidden) return;
    drawer.hidden = true;
    document.body.style.overflow = "";
    if (openBtn) openBtn.setAttribute("aria-expanded", "false");
    document.removeEventListener("keydown", onDrawerKeydown);
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
  }

  function onDrawerKeydown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      closeDrawer();
      return;
    }
    if (event.key !== "Tab") return;

    var items = focusables();
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  if (openBtn) openBtn.addEventListener("click", openDrawer);
  document.querySelectorAll("[data-drawer-close]").forEach(function (el) {
    el.addEventListener("click", closeDrawer);
  });

  /* --------------------------------------------------------------- reveal */

  var revealables = document.querySelectorAll(".reveal");

  if (!revealables.length) {
    /* nothing to do */
  } else if (reduceMotion.matches || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) {
      el.classList.add("is-in");
    });
  } else {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
    );

    revealables.forEach(function (el, index) {
      /* stagger siblings by 40ms without animating layout properties */
      var group = el.closest("[data-stagger]");
      if (group) {
        var peers = Array.prototype.slice.call(
          group.querySelectorAll(".reveal")
        );
        el.style.transitionDelay = peers.indexOf(el) * 40 + "ms";
      }
      observer.observe(el);
    });
  }

  /* ----------------------------------------------------------- nav state */

  var path = window.location.pathname.replace(/\/index\.html$/, "/");
  var here = path.split("/").pop() || "index.html";

  document.querySelectorAll("[data-nav] a[href]").forEach(function (link) {
    var target = link.getAttribute("href").split("#")[0].split("?")[0];
    if (!target) return;
    if (target === here || (here === "" && target === "index.html")) {
      link.setAttribute("aria-current", "page");
    }
  });

  /* ------------------------------------------------------- contact form */

  var form = document.querySelector("[data-validate]");
  if (!form) return;

  var summary = form.querySelector("[data-error-summary]");
  var summaryList = summary ? summary.querySelector("ul") : null;
  var status = form.querySelector("[data-form-status]");

  /* The markup ships without `novalidate` so that with JavaScript off the
     browser still validates. Now that we are here and can show better
     messages, turn the native bubbles off. */
  form.noValidate = true;

  /* Stamp when the page was rendered — contact.php rejects anything submitted
     within a few seconds, which no person manages but bots do. */
  var started = form.querySelector("[data-started]");
  if (started) started.value = String(Math.floor(Date.now() / 1000));

  /* contact.php redirects back with ?error=<code> when a submission is
     refused server-side. Surface it above the form rather than leaving the
     visitor on a page that looks like nothing happened. */
  var SERVER_ERRORS = {
    required: "Please fill in every required field, then send again.",
    email: "That email address does not look valid. Please check it and send again.",
    phone: "The mobile number must be 10 digits, starting 6\u20139.",
    topic: "Please choose a topic from the list.",
    message: "Please give us at least a couple of sentences about the enquiry.",
    consent: "Please tick the acknowledgement before sending.",
    length: "One of the fields is longer than we can accept. Please shorten it.",
    rate: "Several enquiries have already been sent from this connection. Please wait a little, or email us directly.",
    send: "Our mail server did not accept the message. Please email us directly at the address in the panel beside this form."
  };

  (function showServerError() {
    var banner = form.querySelector("[data-server-error]");
    var target = form.querySelector("[data-server-error-text]");
    if (!banner || !target) return;
    var code = new URLSearchParams(window.location.search).get("error");
    if (!code || !Object.prototype.hasOwnProperty.call(SERVER_ERRORS, code)) return;
    target.textContent = SERVER_ERRORS[code];
    banner.hidden = false;
    banner.focus();
    // drop the parameter so a refresh does not replay the error
    if (window.history.replaceState) {
      window.history.replaceState({}, "", window.location.pathname);
    }
  })();

  var MESSAGES = {
    valueMissing: "This field is required.",
    typeMismatch: {
      email: "Enter an email address in the format name@example.com.",
      tel: "Enter a valid phone number."
    },
    tooShort: "Please give us a little more detail (at least 20 characters).",
    patternMismatch: "Enter a 10-digit Indian mobile number."
  };

  function messageFor(input) {
    var v = input.validity;
    if (v.valueMissing) return MESSAGES.valueMissing;
    if (v.typeMismatch) {
      return MESSAGES.typeMismatch[input.type] || "Check this value.";
    }
    if (v.patternMismatch) {
      return input.dataset.errorPattern || MESSAGES.patternMismatch;
    }
    if (v.tooShort) return MESSAGES.tooShort;
    return "Check this value.";
  }

  function errorNodeFor(input) {
    return form.querySelector('[data-error-for="' + input.id + '"]');
  }

  function showError(input) {
    var node = errorNodeFor(input);
    var text = messageFor(input);
    input.setAttribute("aria-invalid", "true");
    if (node) {
      node.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg><span></span>';
      node.querySelector("span").textContent = text;
    }
    return text;
  }

  function clearError(input) {
    input.removeAttribute("aria-invalid");
    var node = errorNodeFor(input);
    if (node) node.textContent = "";
  }

  var fields = Array.prototype.slice.call(
    form.querySelectorAll("input, select, textarea")
  );

  /* validate on blur, not on keystroke */
  fields.forEach(function (input) {
    input.addEventListener("blur", function () {
      if (!input.value && !input.required) return;
      if (input.checkValidity()) clearError(input);
      else showError(input);
    });

    input.addEventListener("input", function () {
      if (input.getAttribute("aria-invalid") === "true" && input.checkValidity())
        clearError(input);
    });
  });

  form.addEventListener("submit", function (event) {
    var invalid = fields.filter(function (input) {
      return !input.checkValidity();
    });

    if (!invalid.length) {
      if (summary) summary.hidden = true;

      if (!form.getAttribute("action")) {
        /* No endpoint configured — say so rather than POST into nothing. */
        event.preventDefault();
        if (status) {
          status.dataset.state = "ok";
          status.textContent =
            "Form endpoint is not configured yet. Please email us directly at the address in the footer.";
        }
        return;
      }

      /* Let the browser submit normally. Disable the button so a slow
         connection cannot produce two enquiries from one person. */
      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending\u2026";
      }
      return;
    }

    event.preventDefault();

    var items = invalid.map(function (input) {
      var text = showError(input);
      var labelEl = form.querySelector('label[for="' + input.id + '"]');
      var label = labelEl
        ? labelEl.textContent.replace("*", "").trim()
        : input.name;
      return { id: input.id, label: label, text: text };
    });

    if (summary && summaryList) {
      summaryList.innerHTML = "";
      items.forEach(function (item) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#" + item.id;
        a.textContent = item.label + ": " + item.text;
        a.addEventListener("click", function (e) {
          e.preventDefault();
          var target = document.getElementById(item.id);
          if (target) target.focus();
        });
        li.appendChild(a);
        summaryList.appendChild(li);
      });
      summary.hidden = false;
      summary.focus();
    } else {
      invalid[0].focus();
    }
  });
})();
