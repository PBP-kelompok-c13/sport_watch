(function () {
  const config = window.SportWatchSearch || {};
  const form = document.getElementById("search-form");
  if (!form) {
    return;
  }

  const preferenceSelect = document.getElementById("preference-select");
  const preferenceModal = document.getElementById("preference-modal");
  const preferenceList = document.getElementById("preference-list");
  const searchFeedback = document.getElementById("search-feedback");
  const newsContainer = document.getElementById("news-results");
  const productContainer = document.getElementById("product-results");
  const newsCountEl = document.getElementById("news-count");
  const productCountEl = document.getElementById("product-count");
  const summaryEl = document.getElementById("search-summary");
  const recentList = document.getElementById("recent-searches");
  const analyticsPanel = document.getElementById("analytics-panel");

  const endpoints = config.endpoints || {};
  const scopeLabels = {
    all: "Semua Konten",
    news: "Berita",
    products: "Produk",
  };

  function showFeedback(message, type = "info") {
    if (!searchFeedback) return;
    searchFeedback.textContent = message;
    searchFeedback.classList.remove("hidden", "bg-red-50", "text-red-700", "border-red-200", "bg-green-50", "text-green-700", "border-green-200");
    if (type === "error") {
      searchFeedback.classList.add("bg-red-50", "text-red-700", "border-red-200");
    } else if (type === "success") {
      searchFeedback.classList.add("bg-green-50", "text-green-700", "border-green-200");
    } else {
      searchFeedback.classList.add("bg-blue-50", "text-blue-700", "border-blue-200");
    }
    setTimeout(() => {
      searchFeedback.classList.add("hidden");
    }, 3500);
  }

  function buildQueryParams() {
    const params = new URLSearchParams();
    const formData = new FormData(form);
    for (const [key, value] of formData.entries()) {
      if (value === null || value === undefined) continue;
      if (typeof value === "string" && value.trim() === "") continue;
      params.append(key, value);
    }
    if (formData.has("only_discount")) {
      params.set("only_discount", "on");
    }
    return params;
  }

  async function fetchResults(event) {
    if (event) {
      event.preventDefault();
    }
    const params = buildQueryParams();
    const url = `${endpoints.results}?${params.toString()}`;
    showFeedback("Mengambil data pencarian...");
    try {
      const response = await fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const payload = await response.json();
      if (!response.ok) {
        const errorText = payload.errors ? Object.values(payload.errors).flat().join("; ") : "Terjadi kesalahan";
        showFeedback(errorText, "error");
        return;
      }
      renderResults(payload);
      showFeedback("Pencarian berhasil diperbarui.", "success");
      if (config.isStaff) {
        loadAnalytics();
      }
    } catch (error) {
      console.error(error);
      showFeedback("Gagal mengambil hasil pencarian.", "error");
    }
  }

  function renderResults(data) {
    const { summary, news = [], products = [], recent = [] } = data;

    if (summaryEl && summary) {
      const keyword = summary.query ? `"${summary.query}"` : "tanpa kata kunci";
      const scopeText = scopeLabels[summary.scope] || summary.scope;
      summaryEl.textContent = `Menampilkan ${summary.news_count + summary.product_count} hasil untuk ${keyword} (${scopeText}).`;
    }

    renderNews(news, data.role === "staff");
    renderProducts(products, data.role === "staff");
    updateCounters(news.length, products.length);
    renderRecent(recent);
  }

  function renderNews(items, isStaff) {
    if (!newsContainer) return;
    newsContainer.innerHTML = "";
    if (!items.length) {
      newsContainer.innerHTML = '<p class="text-sm text-gray-500">Tidak ditemukan berita sesuai pencarian.</p>';
      return;
    }
    items.forEach((item) => {
      const link = document.createElement("a");
      link.href = item.url || "#";
      link.className = "block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition";
      link.innerHTML = `
        <div class="flex gap-3">
          ${item.thumbnail ? `<img src="${item.thumbnail}" alt="${item.title}" class="h-16 w-16 object-cover rounded"/>` : ""}
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">${item.title}</h3>
            <p class="text-xs text-gray-500 mt-1">${item.category || "Umum"} · ${item.published_at || ""}</p>
            ${isStaff && item.views !== null ? `<p class="text-xs text-purple-600 mt-1">${item.views} kali dibaca</p>` : ""}
          </div>
        </div>`;
      newsContainer.appendChild(link);
    });
  }

  function renderProducts(items, isStaff) {
    if (!productContainer) return;
    productContainer.innerHTML = "";
    if (!items.length) {
      productContainer.innerHTML = '<p class="text-sm text-gray-500">Tidak ditemukan produk sesuai pencarian.</p>';
      return;
    }
    items.forEach((item) => {
      const card = document.createElement("a");
      card.href = item.url || "#";
      card.className = "block p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition";
      const discountBadge = item.discount ? `<span class="ml-2 text-xs text-green-600">-${item.discount}%</span>` : "";
      const stockInfo = isStaff && item.stock !== null ? `<p class="text-xs text-gray-500 mt-1">Stok: ${item.stock}</p>` : "";
      card.innerHTML = `
        <div class="flex gap-3">
          ${item.thumbnail ? `<img src="${item.thumbnail}" alt="${item.name}" class="h-16 w-16 object-cover rounded"/>` : ""}
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">${item.name}</h3>
            <p class="text-sm text-green-600 mt-1 font-semibold">${item.currency} ${Number(item.price).toLocaleString("id-ID")}${discountBadge}</p>
            ${stockInfo}
          </div>
        </div>`;
      productContainer.appendChild(card);
    });
  }

  function updateCounters(newsCount, productCount) {
    if (newsCountEl) newsCountEl.textContent = newsCount;
    if (productCountEl) productCountEl.textContent = productCount;
  }

  function renderRecent(recent) {
    if (!recentList) return;
    recentList.innerHTML = "";
    if (!recent || !recent.length) {
      recentList.innerHTML = '<li class="text-gray-500">Belum ada pencarian terbaru.</li>';
      return;
    }
    recent.forEach((item) => {
      const li = document.createElement("li");
      li.className = "flex items-center justify-between bg-gray-50 rounded px-3 py-2";
      const label = item.query ? item.query : "(tanpa kata kunci)";
      const scopeText = scopeLabels[item.scope] || item.scope || "Semua";
      li.innerHTML = `
        <span class="truncate">${label} · ${scopeText}</span>
        <button type="button" class="text-blue-600 hover:underline recent-search" data-query="${item.query || ""}" data-scope="${item.scope || ""}">Gunakan</button>
      `;
      recentList.appendChild(li);
    });
  }

  function attachRecentHandlers() {
    if (!recentList) return;
    recentList.addEventListener("click", (event) => {
      const trigger = event.target.closest(".recent-search");
      if (!trigger) return;
      const { query = "", scope = "" } = trigger.dataset;
      const queryField = document.getElementById("id_query");
      const scopeField = document.getElementById("id_search_in");
      if (queryField) queryField.value = query;
      if (scopeField && scope) scopeField.value = scope;
      if (preferenceSelect) preferenceSelect.value = "";
      fetchResults();
    });
  }

  function openModal() {
    if (!preferenceModal) return;
    preferenceModal.classList.add("active");
  }

  function closeModal() {
    if (!preferenceModal) return;
    preferenceModal.classList.remove("active");
  }

  async function loadPreferenceForm(id = "") {
    if (!config.isAuthenticated) {
      showFeedback("Silakan login untuk menyimpan preset.", "error");
      return;
    }
    const url = new URL(endpoints.preferenceForm, window.location.origin);
    if (id) {
      url.searchParams.set("id", id);
    }
    try {
      const response = await fetch(url.toString(), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      });
      const payload = await response.json();
      if (payload.form) {
        const container = document.getElementById("preference-form-container");
        if (container) {
          container.innerHTML = payload.form;
          bindPreferenceForm();
        }
        openModal();
      }
    } catch (error) {
      console.error(error);
      showFeedback("Gagal memuat form preset.", "error");
    }
  }

  function bindPreferenceForm() {
    const formElement = document.getElementById("preference-form");
    if (!formElement) return;
    formElement.addEventListener("submit", submitPreferenceForm);
    const cancelBtn = document.getElementById("cancel-preference");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => closeModal());
    }
  }

  function getCsrfToken() {
    const name = "csrftoken";
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(`${name}=`)) {
        return decodeURIComponent(trimmed.substring(name.length + 1));
      }
    }
    return "";
  }

  async function submitPreferenceForm(event) {
    event.preventDefault();
    const formElement = event.target;
    const submitUrl = preferenceList ? preferenceList.dataset.submitUrl : endpoints.preferenceSubmit;
    const formData = new FormData(formElement);
    try {
      const response = await fetch(submitUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
        credentials: "same-origin",
      });
      const payload = await response.json();
      if (!response.ok) {
        if (payload.form) {
          const container = document.getElementById("preference-form-container");
          if (container) {
            container.innerHTML = payload.form;
            bindPreferenceForm();
          }
        }
        showFeedback("Gagal menyimpan preset. Periksa kembali isian Anda.", "error");
        return;
      }
      updatePreferenceList(payload.card, payload.preference);
      showFeedback(payload.message || "Preset tersimpan.", "success");
      closeModal();
    } catch (error) {
      console.error(error);
      showFeedback("Terjadi kesalahan saat menyimpan preset.", "error");
    }
  }

  function updatePreferenceList(cardHtml, preference) {
    if (!preferenceList || !cardHtml || !preference) return;
    const temp = document.createElement("div");
    temp.innerHTML = cardHtml.trim();
    const newCard = temp.firstElementChild;
    const existing = preferenceList.querySelector(`.preference-card[data-id="${preference.id}"]`);
    if (existing) {
      preferenceList.replaceChild(newCard, existing);
    } else {
      preferenceList.prepend(newCard);
    }
    if (preferenceSelect) {
      const option = preferenceSelect.querySelector(`option[value="${preference.id}"]`);
      if (!option) {
        const newOption = document.createElement("option");
        newOption.value = preference.id;
        newOption.textContent = preference.label;
        preferenceSelect.appendChild(newOption);
      }
      preferenceSelect.value = preference.id;
    }
  }

  function attachPreferenceListHandler() {
    if (!preferenceList) return;
    preferenceList.addEventListener("click", (event) => {
      const applyBtn = event.target.closest(".apply-preference");
      if (applyBtn) {
        const id = applyBtn.dataset.id;
        if (preferenceSelect) preferenceSelect.value = id;
        fetchResults();
        return;
      }
      const editBtn = event.target.closest(".edit-preference");
      if (editBtn) {
        loadPreferenceForm(editBtn.dataset.id);
      }
    });
  }

  function attachModalHandlers() {
    if (!preferenceModal) return;
    const openBtn = document.getElementById("open-preference-modal");
    const closeBtn = document.getElementById("close-preference-modal");
    if (openBtn) {
      openBtn.addEventListener("click", () => loadPreferenceForm(preferenceSelect ? preferenceSelect.value : ""));
    }
    if (closeBtn) {
      closeBtn.addEventListener("click", () => closeModal());
    }
    preferenceModal.addEventListener("click", (event) => {
      if (event.target.classList.contains("modal-overlay")) {
        closeModal();
      }
    });
  }

  async function loadAnalytics() {
    if (!analyticsPanel || !endpoints.analytics) return;
    try {
      const response = await fetch(endpoints.analytics, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      });
      const payload = await response.json();
      if (!response.ok) return;
      renderAnalytics(payload);
    } catch (error) {
      console.error(error);
    }
  }

  function renderAnalytics(data) {
    const loadingEl = document.getElementById("analytics-loading");
    const contentEl = document.getElementById("analytics-content");
    const topQueriesEl = document.getElementById("analytics-top-queries");
    const scopeEl = document.getElementById("analytics-scope");
    if (!loadingEl || !contentEl) return;
    loadingEl.classList.add("hidden");
    contentEl.classList.remove("hidden");
    if (topQueriesEl) {
      topQueriesEl.innerHTML = "";
      (data.top_queries || []).forEach((item, index) => {
        const li = document.createElement("li");
        li.textContent = `${index + 1}. ${item.keyword} (${item.total})`;
        topQueriesEl.appendChild(li);
      });
      if (!topQueriesEl.innerHTML) {
        topQueriesEl.innerHTML = '<li class="text-gray-500">Belum ada data.</li>';
      }
    }
    if (scopeEl) {
      scopeEl.innerHTML = "";
      (data.scope_breakdown || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.scope} - ${item.total} pencarian`;
        scopeEl.appendChild(li);
      });
      if (!scopeEl.innerHTML) {
        scopeEl.innerHTML = '<li class="text-gray-500">Belum ada data.</li>';
      }
    }
  }

  attachRecentHandlers();
  attachPreferenceListHandler();
  attachModalHandlers();
  bindPreferenceForm();
  if (config.isStaff) {
    loadAnalytics();
  }
  form.addEventListener("submit", fetchResults);
})();
