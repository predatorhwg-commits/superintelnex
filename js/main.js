/* SuperIntelNex — Interaktionen
   - Mobile-Navigation
   - Header-Schatten beim Scrollen
   - Scroll-Reveal für Sektionen
   - Aktuelles Jahr im Footer
*/
(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  var nav = document.getElementById("site-nav");
  var toggle = document.querySelector(".nav-toggle");
  var yearEl = document.getElementById("year");

  /* ------------------------------------------- Aktuelles Jahr im Footer */
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }

  /* ------------------------------------------------ Mobile-Navigation */
  if (toggle && nav) {
    var setNav = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
    };

    toggle.addEventListener("click", function () {
      setNav(toggle.getAttribute("aria-expanded") !== "true");
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        setNav(false);
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        setNav(false);
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) {
        setNav(false);
      }
    });
  }

  /* ------------------------------------------ Header-Zustand beim Scroll */
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ------------------------------------------------------ Scroll-Reveal */
  var revealTargets = document.querySelectorAll(
    ".section-head, .card, .feature, .timeline-item, .pending-item, .community-panel, .risk-banner"
  );

  if (revealTargets.length) {
    revealTargets.forEach(function (el, i) {
      el.classList.add("reveal");
      // Leichte Staffelung, aber gedeckelt, damit nichts zu langsam wirkt.
      el.style.transitionDelay = Math.min(i % 4, 3) * 70 + "ms";
    });

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
      );

      revealTargets.forEach(function (el) {
        observer.observe(el);
      });
    } else {
      revealTargets.forEach(function (el) {
        el.classList.add("is-visible");
      });
    }
  }
})();
