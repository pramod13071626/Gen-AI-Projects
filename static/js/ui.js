(function () {
  const ready = (fn) => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  };

  ready(() => {
    document.querySelectorAll(".premium-section, .premium-card, .metric-card, .coverage-card, .workflow-card, .data-card, .kpi-card").forEach((el) => {
      el.classList.add("reveal-on-scroll");
    });

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    document.querySelectorAll(".reveal-on-scroll").forEach((el) => observer.observe(el));

    const currentPath = window.location.pathname;
    document.querySelectorAll(".navbar .nav-link, .sidebar-nav a").forEach((link) => {
      const href = link.getAttribute("href");
      if (href && href !== "/" && currentPath.startsWith(href)) {
        link.classList.add("active");
      }
    });

    document.querySelectorAll("[data-count-to]").forEach((el) => {
      const target = Number(el.getAttribute("data-count-to") || "0");
      const suffix = el.getAttribute("data-count-suffix") || "";
      const start = performance.now();
      const duration = 900;
      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const value = Math.round(target * (1 - Math.pow(1 - progress, 3)));
        el.textContent = value.toLocaleString() + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });

    if (window.Chart) {
      Chart.defaults.font.family = "Inter, Poppins, system-ui, sans-serif";
      Chart.defaults.color = "#64748b";
      Chart.defaults.plugins.legend.labels.usePointStyle = true;
    }
  });
})();
