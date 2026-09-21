from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Recipe, Category, Tag, ShoppingListItem, Favorite
from .forms import RecipeForm, IngredientFormSet, InstructionStepFormSet, RecipeNutritionForm

User = get_user_model()


def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        if not request.user.is_admin_role():
            raise PermissionDenied("Hanya administrator yang diizinkan mengakses halaman ini.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def home_view(request):
    featured_recipes = Recipe.objects.filter(
        is_featured=True, status=Recipe.Status.PUBLISHED
    ).select_related('category', 'author').order_by('-updated_at')[:3]

    recent_recipes = Recipe.objects.filter(
        status=Recipe.Status.PUBLISHED
    ).select_related('category', 'author').order_by('-created_at')[:6]

    categories = Category.objects.annotate(
        recipe_count=Count('recipes', filter=Q(recipes__status=Recipe.Status.PUBLISHED))
    ).filter(recipe_count__gt=0).order_by('-recipe_count', 'name')[:8]

    user_fav_ids = set()
    if request.user.is_authenticated:
        user_fav_ids = set(request.user.favorites.values_list('recipe_id', flat=True))

    context = {
        'featured_recipes': featured_recipes,
        'recent_recipes': recent_recipes,
        'categories': categories,
        'user_fav_ids': user_fav_ids,
        'is_home_empty': not recent_recipes,
    }
    return render(request, 'recipes/home.html', context)


def recipe_list_view(request):
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()
    max_time = request.GET.get('time', '').strip()
    tag_slug = request.GET.get('tag', '').strip()
    page_num = request.GET.get('page', '1').strip()

    recipes = Recipe.objects.filter(status=Recipe.Status.PUBLISHED).select_related('category', 'author')

    if q:
        recipes = recipes.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(ingredients__item_name__icontains=q)
        ).distinct()

    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    if difficulty in dict(Recipe.Difficulty.choices):
        recipes = recipes.filter(difficulty=difficulty)

    if max_time:
        try:
            mt = int(max_time)
            if mt > 0:
                recipes = recipes.annotate(
                    total_time_min=F('prep_time_minutes') + F('cook_time_minutes')
                ).filter(total_time_min__lte=mt)
        except ValueError:
            pass

    if tag_slug:
        recipes = recipes.filter(tags__slug=tag_slug)

    recipes = recipes.order_by('-created_at')

    # Pagination 12 item per halaman
    paginator = Paginator(recipes, 12)
    page_obj = paginator.get_page(page_num)

    user_fav_ids = set()
    if request.user.is_authenticated:
        user_fav_ids = set(request.user.favorites.values_list('recipe_id', flat=True))

    # Bangun query string untuk pagination yang mempertahankan filter
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'recipes': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'selected_q': q,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'selected_time': max_time,
        'selected_tag': tag_slug,
        'user_fav_ids': user_fav_ids,
    }

    if request.htmx:
        return render(request, 'recipes/partials/recipe_grid.html', context)

    return render(request, 'recipes/recipe_list.html', context)


def recipe_detail_view(request, slug):
    recipe = get_object_or_404(
        Recipe.objects.select_related('category', 'author').prefetch_related('ingredients', 'steps', 'tags'),
        slug=slug
    )

    # Periksa izin melihat status K4
    if recipe.status != Recipe.Status.PUBLISHED:
        is_author = request.user.is_authenticated and request.user == recipe.author
        is_admin_user = request.user.is_authenticated and request.user.is_admin_role()
        if not (is_author or is_admin_user):
            raise Http404("Resep tidak ditemukan atau belum dipublikasikan.")

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, recipe=recipe).exists()

    related_recipes = Recipe.objects.filter(
        status=Recipe.Status.PUBLISHED,
        category=recipe.category
    ).exclude(id=recipe.id).select_related('category')[:3]

    # Ambil nutrisi dengan aman jika ada
    nutrition = getattr(recipe, 'nutrition', None)

    context = {
        'recipe': recipe,
        'nutrition': nutrition,
        'is_favorited': is_favorited,
        'related_recipes': related_recipes,
    }
    return render(request, 'recipes/recipe_detail.html', context)


@require_POST
def toggle_favorite_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # K8: Hanya resep PUBLISHED yang boleh difavoritkan
    if recipe.status != Recipe.Status.PUBLISHED:
        raise Http404("Hanya resep yang telah dipublikasikan yang dapat disimpan ke favorit.")

    # K8: Jika user belum login dan request lewat HTMX, kirim HX-Redirect
    if not request.user.is_authenticated:
        if request.htmx:
            login_url = reverse('accounts:login')
            next_url = request.META.get('HTTP_REFERER', reverse('recipes:home'))
            response = HttpResponse()
            response['HX-Redirect'] = f"{login_url}?next={next_url}"
            return response
        messages.info(request, "Silakan masuk terlebih dahulu untuk menyimpan resep favorit.")
        return redirect('accounts:login')

    fav = Favorite.objects.filter(user=request.user, recipe=recipe).first()
    if fav:
        fav.delete()
        is_favorited = False
    else:
        Favorite.objects.create(user=request.user, recipe=recipe)
        is_favorited = True

    # K8: Jika request biasa (non-HTMX), redirect ke referrer
    if not request.htmx:
        return redirect(request.META.get('HTTP_REFERER', reverse('recipes:detail', kwargs={'slug': recipe.slug})))

    remove_card = request.GET.get('remove_card') == '1'
    if remove_card and not is_favorited:
        # Kembalikan string kosong untuk menghapus elemen di profile.html
        return HttpResponse("")

    return render(request, 'recipes/partials/favorite_button.html', {
        'recipe': recipe,
        'is_favorited': is_favorited,
        'remove_card': remove_card
    })


@login_required
def create_recipe_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        nutrition_form = RecipeNutritionForm(request.POST)
        formset_ingredients = IngredientFormSet(request.POST, request.FILES)
        formset_steps = InstructionStepFormSet(request.POST, request.FILES)

        if form.is_valid() and formset_ingredients.is_valid() and formset_steps.is_valid() and nutrition_form.is_valid():
            with transaction.atomic():
                recipe = form.save(commit=False)
                recipe.author = request.user
                if request.user.is_admin_role():
                    recipe.status = Recipe.Status.PUBLISHED
                else:
                    recipe.status = Recipe.Status.PENDING
                recipe.save()
                form.save_m2m()

                formset_ingredients.instance = recipe
                formset_ingredients.save()

                formset_steps.instance = recipe
                formset_steps.save()

                # Simpan data nutrisi jika diisi
                nutr_data = nutrition_form.cleaned_data
                if any(nutr_data.values()):
                    nutrition = nutrition_form.save(commit=False)
                    nutrition.recipe = recipe
                    nutrition.save()

            if recipe.status == Recipe.Status.PUBLISHED:
                messages.success(request, f'Resep "{recipe.title}" berhasil diterbitkan!')
                return redirect('recipes:detail', slug=recipe.slug)
            else:
                messages.info(request, f'Resep "{recipe.title}" berhasil dikirim dan menunggu verifikasi Admin.')
                return redirect('accounts:profile')
        else:
            messages.error(request, 'Terjadi kesalahan saat menyimpan resep. Periksa kembali form.')
    else:
        form = RecipeForm()
        nutrition_form = RecipeNutritionForm()
        formset_ingredients = IngredientFormSet()
        formset_steps = InstructionStepFormSet()

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'nutrition_form': nutrition_form,
        'formset_ingredients': formset_ingredients,
        'formset_steps': formset_steps,
        'title': 'Kirim Resep Baru'
    })


@login_required
def edit_recipe_view(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    # K9: Hanya penulis atau admin yang boleh mengakses; selain itu 403
    if recipe.author != request.user and not request.user.is_admin_role():
        raise PermissionDenied("Anda tidak memiliki izin untuk mengedit resep ini.")

    nutrition_instance = getattr(recipe, 'nutrition', None)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        nutrition_form = RecipeNutritionForm(request.POST, instance=nutrition_instance)
        formset_ingredients = IngredientFormSet(request.POST, request.FILES, instance=recipe)
        formset_steps = InstructionStepFormSet(request.POST, request.FILES, instance=recipe)

        if form.is_valid() and formset_ingredients.is_valid() and formset_steps.is_valid() and nutrition_form.is_valid():
            with transaction.atomic():
                saved_recipe = form.save(commit=False)
                # K9: Jika diedit oleh non-admin, status otomatis PENDING dan reset rejection_reason
                if not request.user.is_admin_role():
                    saved_recipe.status = Recipe.Status.PENDING
                    saved_recipe.rejection_reason = ""
                saved_recipe.save()
                form.save_m2m()

                formset_ingredients.save()
                formset_steps.save()

                nutr_data = nutrition_form.cleaned_data
                if any(nutr_data.values()):
                    nutr = nutrition_form.save(commit=False)
                    nutr.recipe = saved_recipe
                    nutr.save()
                elif nutrition_instance:
                    nutrition_instance.delete()

            if not request.user.is_admin_role():
                messages.info(request, "Perubahan dikirim untuk ditinjau ulang oleh admin.")
                return redirect('accounts:profile')
            else:
                messages.success(request, f'Resep "{saved_recipe.title}" berhasil diperbarui!')
                return redirect('recipes:detail', slug=saved_recipe.slug)
        else:
            messages.error(request, 'Terjadi kesalahan saat memperbarui resep. Periksa isian form.')
    else:
        form = RecipeForm(instance=recipe)
        nutrition_form = RecipeNutritionForm(instance=nutrition_instance)
        formset_ingredients = IngredientFormSet(instance=recipe)
        formset_steps = InstructionStepFormSet(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'nutrition_form': nutrition_form,
        'formset_ingredients': formset_ingredients,
        'formset_steps': formset_steps,
        'recipe': recipe,
        'title': f'Edit Resep: {recipe.title}'
    })


@admin_required
def admin_dashboard_view(request):
    total_recipes = Recipe.objects.count()
    published_recipes = Recipe.objects.filter(status=Recipe.Status.PUBLISHED).count()
    rejected_recipes = Recipe.objects.filter(status=Recipe.Status.REJECTED).count()
    pending_recipes = Recipe.objects.filter(status=Recipe.Status.PENDING).select_related('author', 'category')

    # B3: Statistik pengguna aktual
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()

    context = {
        'total_recipes': total_recipes,
        'published_recipes': published_recipes,
        'rejected_recipes': rejected_recipes,
        'pending_recipes': pending_recipes,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
    }
    return render(request, 'recipes/admin_dashboard.html', context)


@admin_required
@require_POST
def moderate_recipe_view(request, recipe_id, action):
    # K7: Whitelist action & hanya resep PENDING
    if action not in ['approve', 'reject']:
        raise Http404("Aksi moderasi tidak valid.")

    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PENDING)

    if action == 'approve':
        recipe.status = Recipe.Status.PUBLISHED
        recipe.rejection_reason = ""
        recipe.save()
        messages.success(request, f'Resep "{recipe.title}" telah disetujui dan dipublikasikan.')
    elif action == 'reject':
        reason = request.POST.get('reason', '').strip()
        if len(reason) < 10:
            messages.error(request, "Alasan penolakan wajib diisi minimal 10 karakter.")
            return redirect('recipes:admin_dashboard')
        recipe.status = Recipe.Status.REJECTED
        recipe.rejection_reason = reason
        recipe.save()
        messages.warning(request, f'Resep "{recipe.title}" telah ditolak dengan catatan.')

    return redirect('recipes:admin_dashboard')


@login_required
@require_POST
def add_to_shopping_list_view(request, recipe_id):
    # K1 & K4: Hanya resep PUBLISHED
    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)

    # Validasi porsi 1 sampai 100 dengan fallback default_servings
    raw_servings = request.POST.get('servings', '').strip()
    default_s = recipe.default_servings if recipe.default_servings >= 1 else 4
    try:
        servings = int(raw_servings)
        if servings < 1 or servings > 100:
            servings = default_s
    except (ValueError, TypeError):
        servings = default_s

    multiplier = (Decimal(servings) / Decimal(default_s)).quantize(Decimal("0.0001"))

    with transaction.atomic():
        count = 0
        for ing in recipe.ingredients.all():
            scaled_amount = None
            if ing.amount is not None:
                scaled_amount = (ing.amount * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Gabungkan dengan item yang sudah ada milik user jika item_name dan unit sama dan belum dicentang
            existing_item = ShoppingListItem.objects.filter(
                user=request.user,
                item_name__iexact=ing.item_name,
                unit__iexact=(ing.unit or ''),
                is_checked=False
            ).first()

            if existing_item:
                if scaled_amount is not None:
                    if existing_item.amount is not None:
                        existing_item.amount += scaled_amount
                    else:
                        existing_item.amount = scaled_amount
                    existing_item.save()
            else:
                ShoppingListItem.objects.create(
                    user=request.user,
                    item_name=ing.item_name,
                    amount=scaled_amount,
                    unit=ing.unit
                )
            count += 1

    messages.success(request, f'{count} bahan dari "{recipe.title}" ({servings} porsi) telah ditambahkan ke Daftar Belanja Anda!')
    return redirect('recipes:shopping_list')


@login_required
def shopping_list_view(request):
    items = request.user.shopping_items.order_by('-created_at')
    return render(request, 'recipes/shopping_list.html', {'items': items})


@login_required
@require_POST
def toggle_shopping_item_view(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    item.is_checked = not item.is_checked
    item.save()
    return render(request, 'recipes/partials/shopping_item.html', {'item': item})


@login_required
@require_POST
def delete_shopping_item_view(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    item.delete()
    return HttpResponse("")


@login_required
@require_POST
def clear_checked_shopping_items_view(request):
    request.user.shopping_items.filter(is_checked=True).delete()
    if request.htmx:
        items = request.user.shopping_items.order_by('-created_at')
        return render(request, 'recipes/partials/shopping_item_list.html', {'items': items})
    return redirect('recipes:shopping_list')
