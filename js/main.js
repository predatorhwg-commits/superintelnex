/* SuperIntelNex — Interaktionen
   - Mobile-Navigation
   - Header-Schatten beim Scrollen
   - Scroll-Reveal für Sektionen
   - Aktuelles Jahr im Footer
   - FAQ-Akkordeon (nur ein Panel offen)
   - Aktiver Navigationslink beim Scrollen
   - Nach-oben-Button
*/
(function () {
  "use strict";

  // Kennzeichnet JS-Aktivitaet (FAQ-Panel sind ohne JS immer geoeffnet).
  document.documentElement.classList.add("js");

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
    ".section-head, .card, .feature, .timeline-item, .pending-item, .community-panel, .risk-banner, .faq-item"
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

  /* ---------------------------------------------------- FAQ-Akkordeon */
  var faqToggles = document.querySelectorAll(".faq-toggle");

  if (faqToggles.length) {
    faqToggles.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var open = btn.getAttribute("aria-expanded") === "true";
        // Akkordeon: nur ein Panel zugleich offen.
        faqToggles.forEach(function (other) {
          other.setAttribute("aria-expanded", "false");
          var otherItem = other.closest(".faq-item");
          if (otherItem) {
            otherItem.classList.remove("is-open");
          }
        });
        if (!open) {
          btn.setAttribute("aria-expanded", "true");
          var item = btn.closest(".faq-item");
          if (item) {
            item.classList.add("is-open");
          }
        }
      });
    });
  }

  /* ------------------------------------ Aktiver Navigationslink */
  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll(".site-nav a[href^='#']")
  );

  if (navLinks.length && "IntersectionObserver" in window) {
    var sectionMap = {};
    navLinks.forEach(function (a) {
      var id = a.getAttribute("href").slice(1);
      var section = document.getElementById(id);
      if (section) {
        sectionMap[section.id] = a;
      }
    });

    var activeObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) {
            return;
          }
          navLinks.forEach(function (a) {
            a.classList.remove("is-active");
          });
          var link = sectionMap[entry.target.id];
          if (link) {
            link.classList.add("is-active");
          }
        });
      },
      { rootMargin: "-40% 0px -55% 0px" }
    );

    Object.keys(sectionMap).forEach(function (id) {
      activeObserver.observe(document.getElementById(id));
    });
  }

  /* ------------------------------------------------- Nach-oben-Button */
  var topBtn = document.querySelector(".scroll-top");
  var bodyEl = document.body;

  if (topBtn && bodyEl) {
    topBtn.addEventListener("click", function () {
      var reduced = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
    });

    var onScrollTop = function () {
      bodyEl.classList.toggle("is-top-visible", window.scrollY > 900);
    };
    onScrollTop();
    window.addEventListener("scroll", onScrollTop, { passive: true });
  }

})();
