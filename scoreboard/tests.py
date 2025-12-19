from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import Client, TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from . import views
from .forms import ScoreBoardForm
from .models import Scoreboard

User = get_user_model()


def dtfmt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M")


class ScoreboardModelTests(TestCase):
    def test_str(self):
        s = Scoreboard.objects.create(
            tim1="LAL",
            tim2="BOS",
            skor_tim1=101,
            skor_tim2=99,
            sport="NBA",
            status="live",
        )
        self.assertIn("LAL vs BOS (NBA) - live", str(s))


class ScoreboardFormTests(TestCase):
    def test_form_fields_and_widgets(self):
        form = ScoreBoardForm()

        for f in [
            "tim1",
            "tim2",
            "skor_tim1",
            "skor_tim2",
            "sport",
            "status",
            "tanggal",
            "logo_tim1",
            "logo_tim2",
        ]:
            self.assertIn(f, form.fields)

        self.assertIn("%Y-%m-%dT%H:%M", form.fields["tanggal"].input_formats)

    def test_form_valid_data(self):
        now = timezone.now()
        data = {
            "tim1": "Arsenal",
            "tim2": "Chelsea",
            "skor_tim1": 2,
            "skor_tim2": 1,
            "sport": "EPL",
            "status": "upcoming",
            "tanggal": dtfmt(now),
            "logo_tim1": "",
            "logo_tim2": "",
        }
        form = ScoreBoardForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_invalid_choice(self):
        now = timezone.now()
        data = {
            "tim1": "Foo",
            "tim2": "Bar",
            "skor_tim1": 0,
            "skor_tim2": 0,
            "sport": "UFC",
            "status": "live",
            "tanggal": dtfmt(now),
        }
        form = ScoreBoardForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("sport", form.errors)


class ScoreboardURLTests(TestCase):
    def test_urlpatterns_reverse_and_resolve(self):
        self.assertEqual(reverse("scoreboard:index"), "/scoreboard/")
        self.assertEqual(
            reverse("scoreboard:scoreboard_management"), "/scoreboard/admin/"
        )
        self.assertEqual(
            reverse("scoreboard:create_score"), "/scoreboard/admin/create/"
        )
        self.assertEqual(
            reverse("scoreboard:edit_score", args=[1]), "/scoreboard/admin/edit/1/"
        )
        self.assertEqual(
            reverse("scoreboard:delete_score", args=[1]), "/scoreboard/admin/delete/1/"
        )
        self.assertEqual(reverse("api_scoreboard:scores"), "/api/scoreboard/")
        self.assertIs(resolve("/scoreboard/").func, views.index)
        self.assertIs(resolve("/api/scoreboard/").func, views.filter_scores)


class BaseViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        self.user = User.objects.create_user(
            username="user", password="pass123", is_staff=False
        )

    def login_admin(self):
        self.client.login(username="admin", password="pass123")

    def login_user(self):
        self.client.login(username="user", password="pass123")

    def make_score(self, **kwargs):
        base = {
            "tim1": "A",
            "tim2": "B",
            "skor_tim1": 1,
            "skor_tim2": 2,
            "sport": "NBA",
            "status": "upcoming",
            "tanggal": timezone.now(),
        }
        base.update(kwargs)
        return Scoreboard.objects.create(**base)


class IndexViewTests(BaseViewTestCase):
    def test_index_groups_by_status_and_orders_desc(self):
        t1 = timezone.now()
        t2 = t1 + timezone.timedelta(hours=1)
        t3 = t1 + timezone.timedelta(hours=2)

        s_live_old = self.make_score(status="live", tanggal=t1, tim1="L1")
        s_live_new = self.make_score(status="live", tanggal=t3, tim1="L2")

        s_recent = self.make_score(status="recent", tanggal=t2, tim1="R1")
        s_upcoming = self.make_score(status="upcoming", tanggal=t1, tim1="U1")

        resp = self.client.get(reverse("scoreboard:index"))
        self.assertEqual(resp.status_code, 200)

        live = list(resp.context["live"])
        finished = list(resp.context["finished"])
        upcoming = list(resp.context["upcoming"])

        self.assertEqual({obj.status for obj in live}, {"live"})
        self.assertEqual({obj.status for obj in finished}, {"recent"})
        self.assertEqual({obj.status for obj in upcoming}, {"upcoming"})

        self.assertEqual(live[0].id, s_live_new.id)
        self.assertEqual(live[1].id, s_live_old.id)

        self.assertEqual(len(finished), 1)
        self.assertEqual(len(upcoming), 1)


class AdminGuardTests(BaseViewTestCase):
    def test_management_requires_admin(self):
        resp = self.client.get(reverse("scoreboard:scoreboard_management"))
        self.assertEqual(resp.status_code, 302)
        login_url = resolve_url(settings.LOGIN_URL)
        self.assertIn(login_url, resp["Location"])

        self.login_user()
        resp = self.client.get(reverse("scoreboard:scoreboard_management"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(login_url, resp["Location"])

        self.login_admin()
        resp = self.client.get(reverse("scoreboard:scoreboard_management"))
        self.assertEqual(resp.status_code, 200)

    def test_create_edit_delete_flow(self):
        self.login_admin()

        now = timezone.now()
        payload = {
            "tim1": "Madrid",
            "tim2": "Barca",
            "skor_tim1": 3,
            "skor_tim2": 1,
            "sport": "NBA",
            "status": "live",
            "tanggal": dtfmt(now),
            "logo_tim1": "",
            "logo_tim2": "",
        }
        resp = self.client.post(reverse("scoreboard:create_score"), data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Scoreboard.objects.count(), 1)
        obj = Scoreboard.objects.first()
        self.assertEqual(obj.tim1, "Madrid")

        payload_edit = payload.copy()
        payload_edit["skor_tim1"] = 5
        resp = self.client.post(
            reverse("scoreboard:edit_score", args=[obj.pk]), data=payload_edit
        )
        self.assertEqual(resp.status_code, 302)
        obj.refresh_from_db()
        self.assertEqual(obj.skor_tim1, 5)

        resp = self.client.get(reverse("scoreboard:delete_score", args=[obj.pk]))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse("scoreboard:delete_score", args=[obj.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Scoreboard.objects.count(), 0)


class FilterScoresAPITests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        base_time = timezone.now()

        self.s_recent = self.make_score(
            status="recent", sport="NBA", tim1="REC", tanggal=base_time
        )
        self.s_live = self.make_score(
            status="live", sport="EPL", tim1="LIV", tanggal=base_time
        )
        self.s_upcoming = self.make_score(
            status="upcoming", sport="NFL", tim1="UPC", tanggal=base_time
        )

    def get_json(self, **params):
        return self.client.get(
            reverse("api_scoreboard:scores"),
            params,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    def test_no_filter_returns_all(self):
        resp = self.get_json()
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["scores"]

        self.assertEqual(len(data), 3)

    def test_filter_by_status_live(self):
        resp = self.get_json(status="live")
        data = resp.json()["scores"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "live")
        self.assertEqual(data[0]["tim1"], "LIV")

    def test_filter_by_status_finished_maps_to_recent(self):
        resp = self.get_json(status="finished")
        data = resp.json()["scores"]
        self.assertEqual(len(data), 1)
        # API returns 'finished' for items stored as 'recent' in the DB.
        self.assertEqual(data[0]["status"], "finished")
        self.assertEqual(data[0]["tim1"], "REC")

    def test_filter_by_status_upcoming(self):
        resp = self.get_json(status="upcoming")
        data = resp.json()["scores"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "upcoming")
        self.assertEqual(data[0]["tim1"], "UPC")

    def test_filter_by_sport_case_insensitive(self):
        resp = self.get_json(sport="epl")
        data = resp.json()["scores"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["sport"], "EPL")

    def test_json_schema_fields_exist(self):
        resp = self.get_json()
        item = resp.json()["scores"][0]
        for key in [
            "tim1",
            "tim2",
            "skor_tim1",
            "skor_tim2",
            "tanggal",
            "sport",
            "status",
            "sport_display",
        ]:
            self.assertIn(key, item)


class ManagementListTests(BaseViewTestCase):
    def test_management_lists_scores_desc(self):
        self.login_admin()
        t1 = timezone.now()
        t2 = t1 + timezone.timedelta(minutes=10)
        s_old = self.make_score(tanggal=t1, tim1="Old")
        s_new = self.make_score(tanggal=t2, tim1="New")

        resp = self.client.get(reverse("scoreboard:scoreboard_management"))
        self.assertEqual(resp.status_code, 200)
        scores = list(resp.context["scores"])
        self.assertEqual(scores[0].id, s_new.id)
        self.assertEqual(scores[1].id, s_old.id)
