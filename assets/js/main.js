/* Wealthymind Research — progressive enhancement only.
   Every feature below degrades to working HTML if this file fails to load. */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ---------------------------------------------------------- funding signal */

  /* The bulb lights only at the final stage. Driven by one custom property so
     the SVG needs no per-stage markup. */
  document.querySelectorAll("[data-signal]").forEach(function (signal) {
    var steps = Array.prototype.slice.call(
      signal.querySelectorAll("[data-signal-step]")
    );
    var status = signal.querySelector("[data-signal-status]");
    if (!steps.length) return;

    var LABELS = {
      1: "Not yet funded",
      2: "Not yet funded",
      3: "Not yet funded",
      4: "Funded"
    };
    var GLOW = { 1: 0, 2: 0.18, 3: 0.42, 4: 1 };

    function setStage(stage) {
      signal.dataset.stage = String(stage);
      signal.style.setProperty("--lit", String(GLOW[stage]));
      steps.forEach(function (btn) {
        btn.setAttribute(
          "aria-pressed",
          String(Number(btn.dataset.signalStep) === stage)
        );
      });
      if (status) status.textContent = LABELS[stage];
    }

    steps.forEach(function (btn, index) {
      btn.addEventListener("click", function () {
        setStage(Number(btn.dataset.signalStep));
      });

      // left/right arrows walk the stages, as a stepper should
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
        next.focus();
        setStage(Number(next.dataset.signalStep));
      });
    });

    setStage(1);
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
      /* No backend is wired up yet — see README. Prevent a broken POST and
         tell the user plainly instead of silently failing. */
      if (!form.getAttribute("action")) {
        event.preventDefault();
        if (status) {
          status.dataset.state = "ok";
          status.textContent =
            "Form endpoint is not configured yet. Please email us directly at the address in the footer.";
        }
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
