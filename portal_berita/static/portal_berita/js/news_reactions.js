'use strict';
(function (window, document) {
    if (window.SportWatchReactions) {
        return;
    }

    var state = {
        userReactions: {},
        loginUrl: '/',
        csrfToken: null,
    };

    function getCookie(name) {
        var value = '; ' + document.cookie;
        var parts = value.split('; ' + name + '=');
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }

    function ensureCsrfToken() {
        if (!state.csrfToken) {
            state.csrfToken = getCookie('csrftoken') || '';
        }
        return state.csrfToken;
    }

    function updateCounts(group, summary) {
        if (!Array.isArray(summary)) {
            return;
        }
        summary.forEach(function (item) {
            var selector = '.reaction-button[data-reaction="' + item.key + '"]';
            var button = group.querySelector(selector);
            if (button) {
                var counter = button.querySelector('.reaction-count');
                if (counter) {
                    counter.textContent = item.count;
                }
            }
        });
    }

    function updateGroupState(group, activeReaction) {
        var buttons = group.querySelectorAll('.reaction-button');
        buttons.forEach(function (button) {
            var isActive = button.dataset.reaction === activeReaction;
            button.classList.toggle('active', isActive);
            button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
    }

    function handleResponse(group, payload) {
        if (!payload || payload.status !== 'ok') {
            return;
        }
        var newsId = payload.news_id || group.dataset.newsId;
        if (payload.user_reaction) {
            state.userReactions[newsId] = payload.user_reaction;
        } else {
            delete state.userReactions[newsId];
        }
        updateGroupState(group, state.userReactions[newsId] || null);
        updateCounts(group, payload.reactions || []);
    }

    function sendReaction(group, reactionType) {
        var reactUrl = group.dataset.reactUrl;
        if (!reactUrl) {
            return;
        }
        var params = new URLSearchParams();
        params.append('reaction', reactionType);

        fetch(reactUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': ensureCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: params,
        })
            .then(function (response) {
                if (response.status === 401) {
                    window.location.href = state.loginUrl;
                    return null;
                }
                if (!response.ok) {
                    return null;
                }
                return response.json();
            })
            .then(function (data) {
                if (data) {
                    handleResponse(group, data);
                }
            })
            .catch(function (error) {
                console.error('Unable to submit reaction:', error);
            });
    }

    function bindGroup(group) {
        if (group.dataset.reactionBound === 'true') {
            updateGroupState(group, state.userReactions[group.dataset.newsId] || null);
            return;
        }
        group.dataset.reactionBound = 'true';
        updateGroupState(group, state.userReactions[group.dataset.newsId] || null);
        group.addEventListener('click', function (event) {
            var button = event.target.closest('.reaction-button');
            if (!button) {
                return;
            }
            event.preventDefault();
            sendReaction(group, button.dataset.reaction);
        });
    }

    function bindAll(scope) {
        var root = scope || document;
        var groups = root.querySelectorAll('.news-reactions');
        groups.forEach(function (group) {
            bindGroup(group);
        });
    }

    window.SportWatchReactions = {
        init: function (options) {
            if (options && options.userReactions) {
                state.userReactions = Object.assign({}, options.userReactions);
            } else {
                state.userReactions = {};
            }
            state.loginUrl = (options && options.loginUrl) || state.loginUrl;
            state.csrfToken = getCookie('csrftoken') || '';
            bindAll(document);
        },
        bind: function (target) {
            bindAll(target || document);
        },
        mergeUserReactions: function (entries) {
            if (!entries) {
                return;
            }
            Object.keys(entries).forEach(function (key) {
                var value = entries[key];
                if (value) {
                    state.userReactions[key] = value;
                } else {
                    delete state.userReactions[key];
                }
            });
        },
        getState: function () {
            return Object.assign({}, state);
        },
    };
})(window, document);
