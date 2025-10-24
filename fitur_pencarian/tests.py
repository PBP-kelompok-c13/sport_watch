from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import SearchPreference


class SearchPreferenceAjaxTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", email="tester@example.com", password="secret123"
        )
        self.client.login(username="tester", password="secret123")

    def test_update_existing_preference(self):
        preference = SearchPreference.objects.create(
            user=self.user,
            label="Diskon Sneakers",
            default_scope=SearchPreference.SearchScope.ALL,
            is_public=True,
        )

        response = self.client.post(
            reverse("fitur_pencarian:ajax_preference_submit"),
            {
                "id": str(preference.id),
                "label": "Diskon Sepak Bola",
                "description": "",
                "default_scope": SearchPreference.SearchScope.NEWS,
                "default_news_category": "",
                "default_product_category": "",
                "default_brand": "",
                "min_price": "",
                "max_price": "",
                "only_discount": "",
                "is_public": "on",
                "role_visibility": SearchPreference.RoleVisibility.ALL,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        preference.refresh_from_db()
        self.assertEqual(preference.label, "Diskon Sepak Bola")
        self.assertEqual(preference.default_scope, SearchPreference.SearchScope.NEWS)
