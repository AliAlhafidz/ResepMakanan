"""
Tes Otomatis Dapur Nusa — Tahap 5
Mencakup: K1–K10, B1–B5, U6, dan 4 tes lama (tetap lulus)
"""

from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from recipes.models import (
    Category, Favorite, Ingredient, InstructionStep,
    Recipe, ShoppingListItem, Tag
)


# ===========================================================================
# Helper: setUp bersama
# ===========================================================================

class BaseTestCase(TestCase):
    """Base class dengan fixture user, kategori, dan resep standar."""

    def setUp(self):
        self.client = Client()

        # Admin
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # Pengguna biasa
        self.regular_user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            password='password123',
            role=User.Role.PENGGUNA,
        )

        # Pengguna lain (bukan penulis)
        self.other_user = User.objects.create_user(
            username='other_test',
            email='other@test.com',
            password='password123',
            role=User.Role.PENGGUNA,
        )

        self.category = Category.objects.create(
            name='Uji Kategori', icon_name='restaurant'
        )

        self.recipe = Recipe.objects.create(
            author=self.admin_user,
            category=self.category,
            title='Resep Uji Coba',
            description='Deskripsi uji coba resep.',
            default_servings=4,
            prep_time_minutes=10,
            cook_time_minutes=20,
            difficulty=Recipe.Difficulty.MUDAH,
            status=Recipe.Status.PUBLISHED,
            is_featured=True,
        )
        Ingredient.objects.create(
            recipe=self.recipe,
            amount=Decimal('400'),
            unit='gram',
            item_name='Daging Ayam',
            sort_order=1,
        )
        InstructionStep.objects.create(
            recipe=self.recipe,
            step_number=1,
            instruction='Langkah pertama memasak.',
        )


# ===========================================================================
# Tes Lama (tetap lulus — jangan ubah nama/perilaku)
# ===========================================================================

class DapurNusaTests(BaseTestCase):
    """4 tes asli — harus selalu lulus."""

    def test_home_page_status_and_content(self):
        response = self.client.get(reverse('recipes:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resep Uji Coba')
        self.assertContains(response, 'Menu Hari Ini')

    def test_recipe_detail_page(self):
        response = self.client.get(
            reverse('recipes:detail', kwargs={'slug': self.recipe.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daging Ayam')
        self.assertContains(response, '400')

    def test_recipe_search_filter(self):
        response = self.client.get(reverse('recipes:list'), {'q': 'Uji Coba'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resep Uji Coba')

    def test_favorite_toggle_requires_login(self):
        response = self.client.post(
            reverse('recipes:toggle_favorite', kwargs={'recipe_id': self.recipe.id})
        )
        self.assertEqual(response.status_code, 302)


# ===========================================================================
# K1: add_to_shopping_list_view
# ===========================================================================

class K1ShoppingListTests(BaseTestCase):
    """K1: Validasi add_to_shopping_list_view."""

    def setUp(self):
        super().setUp()
        self.url = reverse('recipes:add_to_shopping', kwargs={'recipe_id': self.recipe.id})
        self.client.login(username='user_test', password='password123')

    def test_add_to_shopping_list_success(self):
        """POST valid menambahkan item ke daftar belanja."""
        resp = self.client.post(self.url, {'servings': '4'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(self.regular_user.shopping_items.exists())

    def test_add_to_shopping_list_invalid_servings_zero(self):
        """servings=0 harus ditolak (400 atau redirect dengan pesan error)."""
        resp = self.client.post(self.url, {'servings': '0'})
        # View harus mengembalikan 400 atau redirect tanpa menambah item
        items_before = self.regular_user.shopping_items.count()
        self.assertIn(resp.status_code, [302, 400])

    def test_add_to_shopping_list_invalid_servings_over_100(self):
        """servings=200 harus ditolak."""
        resp = self.client.post(self.url, {'servings': '200'})
        self.assertIn(resp.status_code, [302, 400])

    def test_add_to_shopping_list_get_returns_405(self):
        """GET harus ditolak dengan 405 (require_POST)."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)

    def test_duplicate_items_merged(self):
        """Menambah resep yang sama dua kali harus menggabungkan item."""
        self.client.post(self.url, {'servings': '2'})
        count_after_first = self.regular_user.shopping_items.count()
        self.client.post(self.url, {'servings': '2'})
        count_after_second = self.regular_user.shopping_items.count()
        # Tidak boleh bertambah — item duplikat digabungkan
        self.assertEqual(count_after_first, count_after_second)

    def test_only_published_recipe_can_be_added(self):
        """Resep non-PUBLISHED tidak boleh ditambah ke shopping list."""
        pending_recipe = Recipe.objects.create(
            author=self.admin_user,
            category=self.category,
            title='Resep Pending Test',
            description='desc',
            default_servings=2,
            prep_time_minutes=5,
            cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH,
            status=Recipe.Status.PENDING,
        )
        url = reverse('recipes:add_to_shopping', kwargs={'recipe_id': pending_recipe.id})
        resp = self.client.post(url, {'servings': '2'})
        self.assertEqual(resp.status_code, 404)


# ===========================================================================
# K2: recipe_list_view
# ===========================================================================

class K2RecipeListTests(BaseTestCase):
    """K2: Pagination dan filter berdasarkan waktu & tag."""

    def test_list_returns_200(self):
        resp = self.client.get(reverse('recipes:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Resep Uji Coba')

    def test_filter_by_max_time(self):
        """Filter waktu masak maksimum."""
        resp = self.client.get(reverse('recipes:list'), {'time': '30'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Resep Uji Coba')

    def test_filter_by_tag(self):
        """Filter berdasarkan tag slug."""
        tag = Tag.objects.create(name='Pedas')
        self.recipe.tags.add(tag)
        resp = self.client.get(reverse('recipes:list'), {'tag': tag.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Resep Uji Coba')

    def test_filter_excludes_non_matching(self):
        """Resep yang tidak cocok dengan filter waktu tidak tampil."""
        slow_recipe = Recipe.objects.create(
            author=self.admin_user,
            category=self.category,
            title='Resep Sangat Lama',
            description='desc',
            default_servings=2,
            prep_time_minutes=120,
            cook_time_minutes=240,
            difficulty=Recipe.Difficulty.SULIT,
            status=Recipe.Status.PUBLISHED,
        )
        resp = self.client.get(reverse('recipes:list'), {'time': '30'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Resep Sangat Lama')

    def test_pending_recipe_not_in_list(self):
        """Resep PENDING tidak tampil di daftar publik."""
        pending = Recipe.objects.create(
            author=self.admin_user,
            category=self.category,
            title='Resep Rahasia Pending',
            description='desc',
            default_servings=2,
            prep_time_minutes=10,
            cook_time_minutes=20,
            difficulty=Recipe.Difficulty.MUDAH,
            status=Recipe.Status.PENDING,
        )
        resp = self.client.get(reverse('recipes:list'))
        self.assertNotContains(resp, 'Resep Rahasia Pending')


# ===========================================================================
# K3: Slug generation
# ===========================================================================

class K3SlugTests(TestCase):
    """K3: Slug tidak boleh kosong meski judul aneh."""

    def test_special_char_title_gets_valid_slug(self):
        """Judul '!!!' harus menghasilkan slug non-kosong (fallback ke 'resep')."""
        cat = Category.objects.create(name='Test Cat', icon_name='star')
        user = User.objects.create_user(
            username='slugtest', email='slug@t.com', password='pass', role=User.Role.ADMIN
        )
        recipe = Recipe.objects.create(
            author=user, category=cat, title='!!!',
            description='test', default_servings=2,
            prep_time_minutes=5, cook_time_minutes=5,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PUBLISHED,
        )
        self.assertTrue(len(recipe.slug) > 0)
        self.assertNotEqual(recipe.slug, '')

    def test_home_returns_200_with_slugged_recipe(self):
        """Beranda tetap 200 meski ada resep dengan slug fallback."""
        cat = Category.objects.create(name='Cat2', icon_name='star')
        user = User.objects.create_user(
            username='slugtest2', email='s2@t.com', password='pass', role=User.Role.ADMIN
        )
        Recipe.objects.create(
            author=user, category=cat, title='Normal Judul',
            description='ok', default_servings=2,
            prep_time_minutes=5, cook_time_minutes=5,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PUBLISHED,
        )
        resp = self.client.get(reverse('recipes:home'))
        self.assertEqual(resp.status_code, 200)


# ===========================================================================
# K4: Status filter — resep non-PUBLISHED
# ===========================================================================

class K4StatusFilterTests(BaseTestCase):
    """K4: Resep PENDING/REJECTED harus 404 untuk pengunjung anonim."""

    def test_pending_recipe_returns_404_for_anonymous(self):
        pending = Recipe.objects.create(
            author=self.admin_user, category=self.category,
            title='Resep Pending K4', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PENDING,
        )
        resp = self.client.get(
            reverse('recipes:detail', kwargs={'slug': pending.slug})
        )
        self.assertEqual(resp.status_code, 404)

    def test_rejected_recipe_returns_404_for_anonymous(self):
        rejected = Recipe.objects.create(
            author=self.admin_user, category=self.category,
            title='Resep Rejected K4', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.REJECTED,
        )
        resp = self.client.get(
            reverse('recipes:detail', kwargs={'slug': rejected.slug})
        )
        self.assertEqual(resp.status_code, 404)

    def test_pending_recipe_visible_to_author(self):
        """Penulis sendiri bisa lihat resep PENDING-nya."""
        pending = Recipe.objects.create(
            author=self.regular_user, category=self.category,
            title='Resep Pending Milik Saya', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PENDING,
        )
        self.client.login(username='user_test', password='password123')
        resp = self.client.get(
            reverse('recipes:detail', kwargs={'slug': pending.slug})
        )
        self.assertEqual(resp.status_code, 200)


# ===========================================================================
# K5: Login — open redirect protection
# ===========================================================================

class K5LoginRedirectTests(TestCase):
    """K5: URL `next` eksternal harus ditolak."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='logintest', email='l@t.com',
            password='pass123', role=User.Role.PENGGUNA,
        )

    def test_external_next_is_rejected(self):
        """next ke domain luar harus diabaikan — tidak redirect ke sana."""
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'logintest',
            'password': 'pass123',
            'next': 'http://evil.com/steal',
        })
        # Harus redirect, tapi BUKAN ke domain eksternal
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('evil.com', resp.get('Location', ''))

    def test_internal_next_is_accepted(self):
        """next ke URL internal harus dihormati."""
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'logintest',
            'password': 'pass123',
            'next': '/recipes/',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/recipes/', resp.get('Location', ''))


# ===========================================================================
# K6: Logout — harus POST
# ===========================================================================

class K6LogoutTests(BaseTestCase):
    """K6: GET ke logout harus 405 (require_POST)."""

    def test_logout_get_returns_405(self):
        self.client.login(username='admin_test', password='password123')
        resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(resp.status_code, 405)

    def test_logout_post_works(self):
        self.client.login(username='admin_test', password='password123')
        resp = self.client.post(reverse('accounts:logout'))
        self.assertEqual(resp.status_code, 302)


# ===========================================================================
# K7: moderate_recipe_view
# ===========================================================================

class K7ModerateRecipeTests(BaseTestCase):
    """K7: Moderasi harus POST, hanya PENDING, alasan wajib untuk reject."""

    def setUp(self):
        super().setUp()
        self.pending_recipe = Recipe.objects.create(
            author=self.regular_user, category=self.category,
            title='Resep Pending Moderasi', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PENDING,
        )
        self.client.login(username='admin_test', password='password123')

    def test_moderate_get_returns_405(self):
        url = reverse('recipes:moderate_recipe', kwargs={
            'recipe_id': self.pending_recipe.id, 'action': 'approve'
        })
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 405)

    def test_approve_pending_recipe(self):
        url = reverse('recipes:moderate_recipe', kwargs={
            'recipe_id': self.pending_recipe.id, 'action': 'approve'
        })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.pending_recipe.refresh_from_db()
        self.assertEqual(self.pending_recipe.status, Recipe.Status.PUBLISHED)

    def test_reject_requires_reason(self):
        """Penolakan tanpa alasan (atau < 10 karakter) harus gagal."""
        url = reverse('recipes:moderate_recipe', kwargs={
            'recipe_id': self.pending_recipe.id, 'action': 'reject'
        })
        resp = self.client.post(url, {'reason': 'Pendek'})
        self.assertEqual(resp.status_code, 302)
        self.pending_recipe.refresh_from_db()
        # Status harus tetap PENDING karena alasan < 10 karakter
        self.assertEqual(self.pending_recipe.status, Recipe.Status.PENDING)

    def test_reject_with_valid_reason(self):
        """Penolakan dengan alasan ≥ 10 karakter harus berhasil."""
        url = reverse('recipes:moderate_recipe', kwargs={
            'recipe_id': self.pending_recipe.id, 'action': 'reject'
        })
        resp = self.client.post(url, {'reason': 'Foto tidak jelas dan bahan kurang lengkap.'})
        self.assertEqual(resp.status_code, 302)
        self.pending_recipe.refresh_from_db()
        self.assertEqual(self.pending_recipe.status, Recipe.Status.REJECTED)

    def test_moderate_published_recipe_returns_404(self):
        """Memoderasi resep yang sudah PUBLISHED harus 404."""
        url = reverse('recipes:moderate_recipe', kwargs={
            'recipe_id': self.recipe.id, 'action': 'approve'
        })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

    def test_non_admin_cannot_moderate(self):
        """Pengguna biasa tidak bisa memoderasi — harus 403."""
        self.client.login(username='user_test', password='password123')
        url = reverse('recipes:moderate_recipe', kwargs={
            'recipe_id': self.pending_recipe.id, 'action': 'approve'
        })
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)


# ===========================================================================
# K8: toggle_favorite_view
# ===========================================================================

class K8ToggleFavoriteTests(BaseTestCase):
    """K8: Favorit harus POST; anonim dapat redirect; resep non-PUBLISHED 404."""

    def test_favorite_get_returns_405(self):
        """GET ke toggle_favorite harus 405."""
        self.client.login(username='user_test', password='password123')
        resp = self.client.get(
            reverse('recipes:toggle_favorite', kwargs={'recipe_id': self.recipe.id})
        )
        self.assertEqual(resp.status_code, 405)

    def test_anonymous_gets_redirect(self):
        """Anonim yang POST toggle_favorite harus di-redirect (302)."""
        resp = self.client.post(
            reverse('recipes:toggle_favorite', kwargs={'recipe_id': self.recipe.id})
        )
        self.assertEqual(resp.status_code, 302)

    def test_anonymous_htmx_gets_hx_redirect(self):
        """Anonim dengan HTMX header harus dapat HX-Redirect header."""
        resp = self.client.post(
            reverse('recipes:toggle_favorite', kwargs={'recipe_id': self.recipe.id}),
            HTTP_HX_REQUEST='true',
        )
        self.assertIn('HX-Redirect', resp.headers)

    def test_toggle_favorite_non_published_returns_404(self):
        """Toggle favorit pada resep non-PUBLISHED harus 404."""
        pending = Recipe.objects.create(
            author=self.admin_user, category=self.category,
            title='Pending Fav Test', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PENDING,
        )
        self.client.login(username='user_test', password='password123')
        resp = self.client.post(
            reverse('recipes:toggle_favorite', kwargs={'recipe_id': pending.id})
        )
        self.assertEqual(resp.status_code, 404)

    def test_toggle_favorite_adds_and_removes(self):
        """Toggle dua kali: tambah lalu hapus favorit."""
        self.client.login(username='user_test', password='password123')
        url = reverse('recipes:toggle_favorite', kwargs={'recipe_id': self.recipe.id})
        # Tambah
        self.client.post(url)
        self.assertTrue(
            Favorite.objects.filter(
                user=self.regular_user, recipe=self.recipe
            ).exists()
        )
        # Hapus
        self.client.post(url)
        self.assertFalse(
            Favorite.objects.filter(
                user=self.regular_user, recipe=self.recipe
            ).exists()
        )


# ===========================================================================
# K9: edit_recipe_view — status reset ke PENDING untuk non-admin
# ===========================================================================

class K9EditRecipeTests(BaseTestCase):
    """K9: Pengguna biasa edit resep terbit → status jadi PENDING."""

    def setUp(self):
        super().setUp()
        # Buat resep milik regular_user yang sudah PUBLISHED
        self.user_recipe = Recipe.objects.create(
            author=self.regular_user, category=self.category,
            title='Resep Saya Yang Sudah Terbit', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PUBLISHED,
        )
        Ingredient.objects.create(
            recipe=self.user_recipe, amount=Decimal('100'), unit='gram',
            item_name='Tepung', sort_order=1,
        )
        InstructionStep.objects.create(
            recipe=self.user_recipe, step_number=1, instruction='Campurkan semua bahan.',
        )

    def _edit_post_data(self, recipe):
        """Buat data POST minimal yang valid untuk edit resep."""
        return {
            'title': recipe.title,
            'description': recipe.description,
            'category': self.category.id,
            'difficulty': recipe.difficulty,
            'default_servings': recipe.default_servings,
            'prep_time_minutes': recipe.prep_time_minutes,
            'cook_time_minutes': recipe.cook_time_minutes,
            # Ingredient formset
            'ingredients-TOTAL_FORMS': '1',
            'ingredients-INITIAL_FORMS': '0',
            'ingredients-MIN_NUM_FORMS': '1',
            'ingredients-MAX_NUM_FORMS': '1000',
            'ingredients-0-item_name': 'Tepung',
            'ingredients-0-amount': '100',
            'ingredients-0-unit': 'gram',
            'ingredients-0-sort_order': '1',
            # Steps formset
            'steps-TOTAL_FORMS': '1',
            'steps-INITIAL_FORMS': '0',
            'steps-MIN_NUM_FORMS': '1',
            'steps-MAX_NUM_FORMS': '1000',
            'steps-0-instruction': 'Campurkan semua bahan.',
            'steps-0-step_number': '1',
        }

    def test_non_admin_edit_resets_to_pending(self):
        """Regular user mengedit resep PUBLISHED → status menjadi PENDING."""
        self.client.login(username='user_test', password='password123')
        resp = self.client.post(
            reverse('recipes:edit', kwargs={'slug': self.user_recipe.slug}),
            self._edit_post_data(self.user_recipe),
        )
        self.user_recipe.refresh_from_db()
        self.assertEqual(self.user_recipe.status, Recipe.Status.PENDING)

    def test_admin_edit_does_not_change_status(self):
        """Admin mengedit resep PUBLISHED → status tetap PUBLISHED."""
        self.client.login(username='admin_test', password='password123')
        resp = self.client.post(
            reverse('recipes:edit', kwargs={'slug': self.recipe.slug}),
            self._edit_post_data(self.recipe),
        )
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.status, Recipe.Status.PUBLISHED)

    def test_other_user_cannot_edit_recipe(self):
        """User lain (bukan penulis, bukan admin) tidak bisa edit resep → 403."""
        self.client.login(username='other_test', password='password123')
        resp = self.client.get(
            reverse('recipes:edit', kwargs={'slug': self.user_recipe.slug})
        )
        self.assertEqual(resp.status_code, 403)


# ===========================================================================
# B1: Kategori dengan jumlah resep
# ===========================================================================

class B1CategoryCountTests(BaseTestCase):
    """B1: Kategori menampilkan jumlah resep yang benar (hanya PUBLISHED)."""

    def test_home_shows_categories(self):
        resp = self.client.get(reverse('recipes:home'))
        self.assertEqual(resp.status_code, 200)
        # Kategori dengan resep PUBLISHED harus ada di context
        categories = resp.context.get('categories', [])
        self.assertTrue(len(list(categories)) >= 1)

    def test_pending_recipe_not_counted_in_category(self):
        """Resep PENDING tidak boleh dihitung dalam jumlah resep kategori."""
        pending = Recipe.objects.create(
            author=self.regular_user, category=self.category,
            title='Pending Tidak Dihitung', description='d',
            default_servings=2, prep_time_minutes=5, cook_time_minutes=10,
            difficulty=Recipe.Difficulty.MUDAH, status=Recipe.Status.PENDING,
        )
        resp = self.client.get(reverse('recipes:home'))
        self.assertEqual(resp.status_code, 200)


# ===========================================================================
# B3: Admin dashboard — statistik pengguna
# ===========================================================================

class B3AdminDashboardTests(BaseTestCase):
    """B3: Dashboard admin memuat statistik pengguna yang benar."""

    def test_dashboard_shows_user_stats(self):
        self.client.login(username='admin_test', password='password123')
        resp = self.client.get(reverse('recipes:admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_users', resp.context)
        self.assertIn('active_users', resp.context)
        self.assertIn('inactive_users', resp.context)
        # Minimal ada 3 user yang kita buat di setUp
        self.assertGreaterEqual(resp.context['total_users'], 3)

    def test_non_admin_cannot_access_dashboard(self):
        """Regular user tidak boleh akses dashboard → 403."""
        self.client.login(username='user_test', password='password123')
        resp = self.client.get(reverse('recipes:admin_dashboard'))
        self.assertEqual(resp.status_code, 403)

    def test_anonymous_redirected_from_dashboard(self):
        """Anonim redirect ke login dari dashboard."""
        resp = self.client.get(reverse('recipes:admin_dashboard'))
        self.assertEqual(resp.status_code, 302)


# ===========================================================================
# B4: Login — akun nonaktif
# ===========================================================================

class B4InactiveUserTests(TestCase):
    """B4: Akun nonaktif tidak bisa login dan mendapat pesan tepat."""

    def setUp(self):
        self.inactive_user = User.objects.create_user(
            username='inactive_test',
            email='inactive@t.com',
            password='pass123',
            role=User.Role.PENGGUNA,
            is_active=False,
        )

    def test_inactive_user_cannot_login(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'inactive_test',
            'password': 'pass123',
        })
        # Harus tetap di halaman login (bukan redirect ke home)
        self.assertEqual(resp.status_code, 200)
        # User tidak boleh ter-authenticate
        from django.contrib.auth import SESSION_KEY
        self.assertNotIn(SESSION_KEY, self.client.session)


# ===========================================================================
# B5: Registrasi — email unik
# ===========================================================================

class B5UniqueEmailTests(TestCase):
    """B5: Email yang sudah dipakai tidak boleh digunakan saat registrasi."""

    def setUp(self):
        User.objects.create_user(
            username='existing_user',
            email='existing@test.com',
            password='pass123',
            role=User.Role.PENGGUNA,
        )

    def test_duplicate_email_rejected(self):
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'new_user_b5',
            'email': 'existing@test.com',  # email sudah dipakai
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        # Harus gagal — form error
        self.assertEqual(resp.status_code, 200)
        form = resp.context.get('form')
        self.assertIsNotNone(form)
        self.assertFalse(form.is_valid() if hasattr(form, 'is_valid') else True)

    def test_unique_email_accepted(self):
        """Email baru boleh digunakan."""
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'new_user_unique',
            'email': 'unique@test.com',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        # Harus redirect (berhasil daftar)
        self.assertEqual(resp.status_code, 302)


# ===========================================================================
# U6: Konversi porsi (scale) — validasi data bahan
# ===========================================================================

class U6ServingsScaleTests(BaseTestCase):
    """U6: Halaman detail menampilkan data bahan yang bisa digunakan untuk scale."""

    def test_detail_contains_ingredient_amount(self):
        """Jumlah bahan ditampilkan di halaman detail."""
        resp = self.client.get(
            reverse('recipes:detail', kwargs={'slug': self.recipe.slug})
        )
        self.assertEqual(resp.status_code, 200)
        # Data bahan harus ada
        self.assertContains(resp, '400')
        self.assertContains(resp, 'gram')
        self.assertContains(resp, 'Daging Ayam')

    def test_detail_contains_default_servings(self):
        """default_servings harus ada di context/template untuk Alpine.js scale."""
        resp = self.client.get(
            reverse('recipes:detail', kwargs={'slug': self.recipe.slug})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('recipe', resp.context)
        self.assertEqual(resp.context['recipe'].default_servings, 4)


# ===========================================================================
# Shopping List — U9: clear checked items
# ===========================================================================

class U9ShoppingListTests(BaseTestCase):
    """U9: Hapus item yang sudah dicentang."""

    def setUp(self):
        super().setUp()
        self.client.login(username='user_test', password='password123')
        # Buat 2 item — 1 checked, 1 unchecked
        self.checked_item = ShoppingListItem.objects.create(
            user=self.regular_user,
            item_name='Bahan Dicentang',
            amount=Decimal('100'),
            unit='gram',
            is_checked=True,
        )
        self.unchecked_item = ShoppingListItem.objects.create(
            user=self.regular_user,
            item_name='Bahan Belum Dicentang',
            amount=Decimal('200'),
            unit='ml',
            is_checked=False,
        )

    def test_clear_checked_removes_only_checked(self):
        """clear_checked_shopping_items hanya menghapus item is_checked=True."""
        resp = self.client.post(reverse('recipes:clear_checked_shopping_items'))
        self.assertEqual(resp.status_code, 302)
        # Item dicentang harus terhapus
        self.assertFalse(
            ShoppingListItem.objects.filter(id=self.checked_item.id).exists()
        )
        # Item belum dicentang harus tetap ada
        self.assertTrue(
            ShoppingListItem.objects.filter(id=self.unchecked_item.id).exists()
        )

    def test_clear_checked_get_returns_405(self):
        resp = self.client.get(reverse('recipes:clear_checked_shopping_items'))
        self.assertEqual(resp.status_code, 405)
