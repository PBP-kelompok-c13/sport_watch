(function () {
    document.addEventListener('DOMContentLoaded', function () {
        const moduleRoot = document.getElementById('search-module');
        if (!moduleRoot) {
            return;
        }

        const config = window.SportWatchSearch || { endpoints: {} };
        const form = document.getElementById('search-form');
        if (!form) {
            return;
        }
        const summary = document.getElementById('search-summary');
        const newsContainer = document.getElementById('news-results');
        const productContainer = document.getElementById('product-results');
        const newsCount = document.getElementById('news-count');
        const productCount = document.getElementById('product-count');
        const feedback = document.getElementById('search-feedback');
        const recentList = document.getElementById('recent-searches');
        const preferenceSelect = document.getElementById('preference-select');
        const preferenceList = document.getElementById('preference-list');
        const openPreferenceBtn = document.getElementById('open-preference-modal');
        const modal = document.getElementById('preference-modal');
        const analyticsPanel = document.getElementById('analytics-panel');

        const queryInput = form.querySelector('input[name="query"]');
        const scopeSelect = form.querySelector('select[name="search_in"]');

        function showFeedback(message, type = 'success') {
            if (!feedback) return;
            feedback.textContent = message;
            feedback.classList.remove('hidden', 'bg-red-50', 'border-red-200', 'text-red-700');
            feedback.classList.remove('bg-blue-50', 'border-blue-100', 'text-blue-700');

            if (type === 'error') {
                feedback.classList.add('bg-red-50', 'border', 'border-red-200', 'text-red-700');
            } else {
                feedback.classList.add('bg-blue-50', 'border', 'border-blue-100', 'text-blue-700');
            }
        }

        function hideFeedback() {
            if (!feedback) return;
            feedback.classList.add('hidden');
        }

        function renderNewsItems(items) {
            if (!items || !items.length) {
                newsContainer.innerHTML = '<p class="text-gray-500 text-sm">Belum ada hasil berita.</p>';
                return;
            }

            const html = items.map(function (item) {
                return [
                    '<a href="', item.url, '" class="block p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition">',
                    '<h3 class="font-semibold text-gray-900">', item.title, '</h3>',
                    '<p class="text-xs text-gray-500 mt-1">Kategori: ', item.category || 'Umum', '</p>',
                    item.published_at ? '<p class="text-xs text-gray-400">Terbit ' + item.published_at + '</p>' : '',
                    item.views !== null && item.views !== undefined ? '<p class="text-xs text-gray-400">Dilihat ' + item.views + ' kali</p>' : '',
                    '</a>'
                ].join('');
            }).join('');
            newsContainer.innerHTML = html;
        }

        function renderProductItems(items) {
            if (!items || !items.length) {
                productContainer.innerHTML = '<p class="text-gray-500 text-sm">Belum ada hasil produk.</p>';
                return;
            }

            const html = items.map(function (item) {
                const price = new Intl.NumberFormat('id-ID', {
                    style: 'currency',
                    currency: item.currency || 'IDR',
                    minimumFractionDigits: 0
                }).format(item.price || 0);
                return [
                    '<a href="', item.url, '" class="block p-4 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition">',
                    '<h3 class="font-semibold text-gray-900">', item.name, '</h3>',
                    '<p class="text-xs text-gray-500 mt-1">Harga: ', price, '</p>',
                    item.discount ? '<p class="text-xs text-green-600">Diskon ' + item.discount + '%</p>' : '',
                    item.stock !== null && item.stock !== undefined ? '<p class="text-xs text-gray-400">Stok: ' + item.stock + '</p>' : '',
                    '</a>'
                ].join('');
            }).join('');
            productContainer.innerHTML = html;
        }

        function renderRecentSearches(items) {
            if (!recentList) return;
            if (!items || !items.length) {
                recentList.innerHTML = '<li class="text-gray-500">Belum ada pencarian terbaru.</li>';
                return;
            }

            const html = items.map(function (item) {
                const queryText = item.query ? item.query : '(tanpa kata kunci)';
                const queryAttr = (item.query || '').replace(/"/g, '&quot;');
                return [
                    '<li class="flex items-center justify-between bg-gray-50 rounded px-3 py-2">',
                    '<span class="truncate">', queryText, ' · ', (item.scope || '').toUpperCase(), '</span>',
                    '<button type="button" class="text-blue-600 hover:underline recent-search" data-query="',
                    queryAttr, '" data-scope="', item.scope || '', '">Gunakan</button>',
                    '</li>'
                ].join('');
            }).join('');
            recentList.innerHTML = html;
        }

        function updateSummary(summaryData) {
            if (!summary || !summaryData) return;
            const queryLabel = summaryData.query ? '"' + summaryData.query + '"' : 'tanpa kata kunci';
            summary.textContent = 'Menampilkan ' + summaryData.news_count + ' berita dan ' + summaryData.product_count + ' produk untuk ' + queryLabel + '.';
        }

        function updateCounters(summaryData) {
            if (!summaryData) return;
            if (newsCount) {
                newsCount.textContent = summaryData.news_count;
            }
            if (productCount) {
                productCount.textContent = summaryData.product_count;
            }
        }

        async function executeSearch() {
            const params = new URLSearchParams(new FormData(form));
            if (preferenceSelect && preferenceSelect.value) {
                params.set('preference', preferenceSelect.value);
            }

            hideFeedback();
            summary.textContent = 'Mengambil data pencarian...';

            try {
                const response = await fetch(config.endpoints.results + '?' + params.toString(), {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    credentials: 'same-origin'
                });

                if (!response.ok) {
                    const errorPayload = await response.json().catch(function () { return {}; });
                    const errorMessages = errorPayload.errors ? Object.values(errorPayload.errors).flat().join(' ') : 'Terjadi kesalahan saat memproses pencarian.';
                    showFeedback(errorMessages, 'error');
                    summary.textContent = 'Terjadi kesalahan saat memuat hasil pencarian.';
                    return;
                }

                const data = await response.json();
                updateSummary(data.summary);
                updateCounters(data.summary);
                renderNewsItems(data.news);
                renderProductItems(data.products);
                renderRecentSearches(data.recent);
                showFeedback('Pencarian berhasil diperbarui.', 'success');
            } catch (error) {
                showFeedback('Tidak dapat terhubung ke server pencarian.', 'error');
                summary.textContent = 'Gagal terhubung dengan server pencarian.';
            }
        }

        form.addEventListener('submit', function (event) {
            event.preventDefault();
            executeSearch();
        });

        if (recentList) {
            recentList.addEventListener('click', function (event) {
                const target = event.target;
                if (target && target.classList.contains('recent-search')) {
                    event.preventDefault();
                    if (queryInput) {
                        queryInput.value = target.dataset.query || '';
                    }
                    if (scopeSelect && target.dataset.scope) {
                        scopeSelect.value = target.dataset.scope;
                    }
                    form.requestSubmit();
                }
            });
        }

        if (preferenceList) {
            // Helper: ambil CSRF dari cookie (untuk POST delete)
            function getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return '';
            }

            preferenceList.addEventListener('click', function (event) {
                const targetEl = event.target;
                if (!targetEl) return;

                // APPLY
                const applyBtn = targetEl.closest('.apply-preference');
                if (applyBtn) {
                    const id = applyBtn.dataset.id;
                    if (preferenceSelect && id) {
                        preferenceSelect.value = id;
                        showFeedback('Preset diterapkan.', 'success');
                        form.requestSubmit();
                    }
                    return;
                }

                // EDIT
                const editBtn = targetEl.closest('.edit-preference');
                if (editBtn) {
                    const id = editBtn.dataset.id;
                    if (id) openPreferenceModal(id);
                    return;
                }

                // DELETE
                const deleteBtn = targetEl.closest('.delete-preference');
                if (deleteBtn) {
                    const id = deleteBtn.dataset.id;
                    if (!id) return;

                    if (!confirm('Hapus preset ini? Tindakan ini tidak dapat dibatalkan.')) {
                        return;
                    }

                    const formData = new FormData();
                    formData.append('id', id);
                    formData.append('csrfmiddlewaretoken', getCookie('csrftoken') || '');

                    fetch(config.endpoints.preferenceDelete, {
                        method: 'POST',
                        body: formData,
                        headers: { 'X-Requested-With': 'XMLHttpRequest' },
                        credentials: 'same-origin'
                    })
                        .then(async (res) => {
                            let data = {};
                            try { data = await res.json(); } catch (e) {}
                            return { ok: res.ok, data };
                        })
                        .then(({ ok, data }) => {
                            if (!ok) {
                                showFeedback(data.error || 'Gagal menghapus preset.', 'error');
                                return;
                            }
                            // Hapus kartu di list
                            const card = deleteBtn.closest('.preference-card');
                            if (card) card.remove();

                            // Hapus option di <select> & reset jika sedang dipilih
                            if (preferenceSelect) {
                                const opt = preferenceSelect.querySelector('option[value="' + id + '"]');
                                if (opt) opt.remove();
                                if (preferenceSelect.value === id) {
                                    preferenceSelect.value = '';
                                }
                            }

                            showFeedback(data.message || 'Preset pencarian berhasil dihapus.', 'success');
                        })
                        .catch(() => {
                            showFeedback('Tidak dapat menghapus preset saat ini.', 'error');
                        });

                    return;
                }
            });
        }

        function ensurePreferenceOption(preference) {
            if (!preferenceSelect) return;
            let option = preferenceSelect.querySelector('option[value="' + preference.id + '"]');
            if (!option) {
                option = document.createElement('option');
                option.value = preference.id;
                preferenceSelect.appendChild(option);
            }
            option.textContent = preference.label;
            preferenceSelect.value = preference.id;
        }

        async function loadPreferenceForm(id) {
            if (!modal) return;
            const container = document.getElementById('preference-form-container');
            if (!container) return;

            // gunakan /api/preferences/<id>/form/ saat edit
            const url = id
                ? config.endpoints.preferenceForm.replace(/form\/?$/, `${encodeURIComponent(id)}/form/`)
                : config.endpoints.preferenceForm;

            try {
                const response = await fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    },
                    credentials: 'same-origin'
                });

                // Anggap perlu login hanya jika 401/403 ATAU redirect ke halaman login
                if (response.status === 401 || response.status === 403 || (response.redirected && /login/i.test(response.url))) {
                    showFeedback('Silakan login untuk mengelola preset pencarian.', 'error');
                    closePreferenceModal();
                    return;
                }

                if (!response.ok) {
                    showFeedback('Gagal memuat formulir preset.', 'error');
                    closePreferenceModal();
                    return;
                }

                const data = await response.json();
                container.innerHTML = data.form;
            } catch (error) {
                showFeedback('Tidak dapat memuat formulir preset.', 'error');
                closePreferenceModal();
            }
        }

        function openPreferenceModal(id) {
            if (!modal) return;
            modal.classList.remove('hidden');
            modal.classList.add('active');
            loadPreferenceForm(id);
        }

        function closePreferenceModal() {
            if (!modal) return;
            modal.classList.remove('active');
            modal.classList.add('hidden');
        }

        if (openPreferenceBtn) {
            openPreferenceBtn.addEventListener('click', function () {
                openPreferenceModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', function (event) {
                const target = event.target;
                if (target.id === 'close-preference-modal' || target.id === 'cancel-preference' || target.classList.contains('modal-overlay')) {
                    closePreferenceModal();
                }
            });

            // Guard anti double-submit
            let isSavingPreference = false;

            // Handler submit form preset (pakai capture di document)
            async function onPreferenceFormSubmit(event) {
                // tangkap form apapun yang memicu submit di dalam modal
                const formElement = (event.target && event.target.closest) ? event.target.closest('#preference-form') : null;
                if (!formElement) return;  // bukan form kita

                event.preventDefault(); // cegah reload halaman

                // cegah double-submit
                if (isSavingPreference) return;
                isSavingPreference = true;

                const submitBtn = formElement.querySelector('[type="submit"]');
                const oldText = submitBtn ? submitBtn.textContent : null;
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Menyimpan...';
                }

                const formData = new FormData(formElement);

                // Pakai endpoint ber-ID jika ada hidden input "id"
                const idVal = formData.get('id');
                const submitUrl = idVal
                    ? config.endpoints.preferenceSubmit.replace(/submit\/?$/, `${encodeURIComponent(idVal)}/submit/`)
                    : config.endpoints.preferenceSubmit;

                try {
                    const response = await fetch(submitUrl, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': formData.get('csrfmiddlewaretoken') || '',
                            'Accept': 'application/json'
                        },
                        credentials: 'same-origin'
                    });

                    // Anggap perlu login hanya jika 401/403 ATAU redirect ke halaman login
                    if (response.status === 401 || response.status === 403 || (response.redirected && /login/i.test(response.url))) {
                        showFeedback('Silakan login untuk menyimpan preset pencarian.', 'error');
                        closePreferenceModal();
                        return;
                    }

                    const data = await response.json().catch(function () { return {}; });

                    if (!response.ok) {
                        if (data.form) {
                            const container = document.getElementById('preference-form-container');
                            if (container) {
                                container.innerHTML = data.form;
                            }
                        }
                        if (data.errors) {
                            const errors = Object.values(data.errors).flat().join(' ');
                            showFeedback(errors || 'Gagal menyimpan preset.', 'error');
                        } else {
                            showFeedback('Gagal menyimpan preset.', 'error');
                        }
                        return;
                    }

                    if (data.card && preferenceList) {
                        const existingCard = preferenceList.querySelector('[data-id="' + data.preference.id + '"]');
                        if (existingCard) {
                            existingCard.outerHTML = data.card;
                        } else {
                            preferenceList.insertAdjacentHTML('afterbegin', data.card);
                        }
                    }

                    if (data.preference) {
                        ensurePreferenceOption(data.preference);
                    }

                    showFeedback(data.message || 'Preset berhasil disimpan.', 'success');
                    closePreferenceModal();
                } catch (error) {
                    showFeedback('Tidak dapat menyimpan preset saat ini.', 'error');
                } finally {
                    isSavingPreference = false;
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = oldText || 'Simpan Preset';
                    }
                }
            }

            // Pakai SATU listener: capture di document
            document.addEventListener('submit', onPreferenceFormSubmit, true);
        }

        async function loadAnalytics() {
            if (!analyticsPanel || !config.isStaff || !config.endpoints.analytics) {
                return;
            }
            const loadingEl = document.getElementById('analytics-loading');
            const contentEl = document.getElementById('analytics-content');
            const topQueriesEl = document.getElementById('analytics-top-queries');
            const scopeEl = document.getElementById('analytics-scope');
            try {
                const response = await fetch(config.endpoints.analytics, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    credentials: 'same-origin'
                });
                if (!response.ok) {
                    throw new Error('Gagal memuat analitik.');
                }
                const data = await response.json();
                if (topQueriesEl) {
                    if (data.top_queries && data.top_queries.length) {
                        topQueriesEl.innerHTML = data.top_queries.map(function (item) {
                            return '<li>' + item.keyword + ' · ' + item.total + ' pencarian</li>';
                        }).join('');
                    } else {
                        topQueriesEl.innerHTML = '<li>Tidak ada data pencarian.</li>';
                    }
                }
                if (scopeEl) {
                    if (data.scope_breakdown && data.scope_breakdown.length) {
                        scopeEl.innerHTML = data.scope_breakdown.map(function (item) {
                            return '<li>' + (item.scope || 'all') + ' · ' + item.total + ' kali</li>';
                        }).join('');
                    } else {
                        scopeEl.innerHTML = '<li>Tidak ada data scope.</li>';
                    }
                }
                if (loadingEl) {
                    loadingEl.classList.add('hidden');
                }
                if (contentEl) {
                    contentEl.classList.remove('hidden');
                }
            } catch (error) {
                if (loadingEl) {
                    loadingEl.textContent = error.message;
                }
            }
        }

        loadAnalytics();
    });
})();