# shop/tests.py
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from shop.models import Category, Brand, Product

# Create your tests here.


User = get_user_model()

def make_user(username="u", is_staff=False, is_superuser=False, password="pass"):
    u = User.objects.create_user(username=username, password=password)
    u.is_staff = is_staff
    u.is_superuser = is_superuser
    u.save()
    return u

def make_category(name="Accessories", parent=None, slug=None):
    return Category.objects.create(name=name, slug=slug or slugify(name), parent=parent)

def make_brand(name="Nike"):
    return Brand.objects.create(name=name, slug=slugify(name))

def make_product(**kwargs):
    kwargs.setdefault("category", make_category())
    kwargs.setdefault("brand", make_brand())
    kwargs.setdefault("price", 10000)
    kwargs.setdefault("stock", 10)
    kwargs.setdefault("status", "active")
    kwargs.setdefault("thumbnail", "https://example.com/img.jpg")
    return Product.objects.create(**kwargs)


class TestProductModel(TestCase):
    def test_final_price_and_discount(self):
        p = make_product(price=Decimal("100.00"), sale_price=None)
        self.assertEqual(p.final_price, Decimal("100.00"))
        self.assertEqual(p.discount_percent, 0)

        p2 = make_product(name="with-sale", price=Decimal("200.00"), sale_price=Decimal("150.00"))
        self.assertEqual(p2.final_price, Decimal("150.00"))
        self.assertEqual(p2.discount_percent, 25)

    def test_in_stock(self):
        self.assertFalse(make_product(stock=0, status="active").in_stock)
        self.assertFalse(make_product(name="x", stock=5, status="draft").in_stock)
        self.assertTrue(make_product(name="y", stock=3, status="active").in_stock)


class TestPublicViews(TestCase):
    def setUp(self):
        self.cat_acc = make_category("accessories", slug="accessories")
        self.cat_jer = make_category("jerseys", slug="jerseys")
        self.brand = make_brand("Adidas")
        self.p1 = make_product(name="A", category=self.cat_acc, brand=self.brand, price=100, is_featured=True)
        self.p2 = make_product(name="B", category=self.cat_acc, brand=self.brand, price=300, sale_price=200)
        self.p3 = make_product(name="C", category=self.cat_jer, brand=self.brand, price=50, stock=0)
        self.p_draft = make_product(name="Hidden", status="draft")

    def test_product_list_basic(self):
        r = self.client.get(reverse("shop:list"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, self.p1.name)
        self.assertNotContains(r, self.p_draft.name)

    def test_product_detail_json(self):
        r = self.client.get(reverse("api_shop:product_detail", args=[self.p1.slug]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["slug"], self.p1.slug)


class TestReviews(TestCase):
    def setUp(self):
        self.user = make_user("alice", password="x")
        self.p = make_product(name="Reviewable")

    def test_create_review_updates_aggregate(self):
        self.client.login(username="alice", password="x")
        url = reverse("api_shop:review_create", args=[self.p.id])
        r = self.client.post(url, {"rating": 5, "title": "ok", "content": "nice"})
        self.assertEqual(r.status_code, 201)
        self.p.refresh_from_db()
        self.assertEqual(self.p.rating_count, 1)


class TestAdminViews(TestCase):
    def setUp(self):
        self.staff = make_user("staff", password="x", is_staff=True)
        self.cat = make_category("Accessories", slug="accessories")
        self.brand = make_brand("Nike")
        self.p = make_product(category=self.cat, brand=self.brand)

    def test_manage_shop_requires_staff(self):
        url = reverse("shop:manage_shop")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.login(username="staff", password="x")
        self.assertEqual(self.client.get(url).status_code, 200)
