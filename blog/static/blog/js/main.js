/* BlogPlatform front-end behaviour (vanilla JS + Bootstrap) */
document.addEventListener("DOMContentLoaded", () => {
  // 1. Show Django messages as Bootstrap toasts.
  document.querySelectorAll("#toastContainer .toast").forEach((el) => {
    new bootstrap.Toast(el, { delay: 4000 }).show();
  });

  // 2. Home page: live search + category filter (no page reload).
  const grid = document.getElementById("postGrid");
  if (grid) {
    const searchInput = document.getElementById("searchInput");
    const pills = document.querySelectorAll("#categoryFilters .filter-pill");
    const items = Array.from(grid.querySelectorAll(".post-item"));
    const noResults = document.getElementById("noResults");
    let category = "All";

    const applyFilters = () => {
      const query = searchInput.value.trim().toLowerCase();
      let visible = 0;
      items.forEach((item) => {
        const matchesCategory = category === "All" || item.dataset.category === category;
        const matchesQuery = !query || item.dataset.search.includes(query);
        const show = matchesCategory && matchesQuery;
        item.classList.toggle("d-none", !show);
        if (show) visible += 1;
      });
      noResults.classList.toggle("d-none", visible > 0);
    };

    searchInput.addEventListener("input", applyFilters);
    pills.forEach((pill) => {
      pill.addEventListener("click", () => {
        category = pill.dataset.category;
        pills.forEach((p) => p.classList.toggle("active", p === pill));
        applyFilters();
      });
    });
    applyFilters();
  }

  // 3. Inline delete confirmation panels.
  document.querySelectorAll("[data-delete-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const panel = document.getElementById(btn.dataset.deleteToggle);
      if (panel) {
        panel.classList.toggle("d-none");
        if (!panel.classList.contains("d-none")) panel.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  });
  document.querySelectorAll("[data-delete-cancel]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const panel = document.getElementById(btn.dataset.deleteCancel);
      if (panel) panel.classList.add("d-none");
    });
  });

  // 4. Live character counter for the excerpt box.
  document.querySelectorAll("[data-char-counter]").forEach((area) => {
    const counter = document.getElementById(area.dataset.charCounter);
    if (!counter) return;
    const update = () => { counter.textContent = area.value.length; };
    area.addEventListener("input", update);
    update();
  });

  // 5. Disable the submit button and show a spinner while a form is submitting.
  document.querySelectorAll("form[data-loading-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn && form.checkValidity()) {
        btn.disabled = true;
        btn.insertAdjacentHTML("afterbegin", '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>');
      }
    });
  });
});
