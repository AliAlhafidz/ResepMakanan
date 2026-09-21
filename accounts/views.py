from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import RegisterForm, ProfileUpdateForm, StyledAuthenticationForm
from .models import UserProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('recipes:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Selamat datang di Dapur Nusa, {user.username}!')
            return redirect('recipes:home')
        else:
            messages.error(request, 'Terjadi kesalahan saat pendaftaran. Mohon periksa form kembali.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('recipes:home')
    
    # Ambil next dari POST atau GET
    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!')
            
            # Validasi open redirect K5
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect('recipes:home')
        else:
            # Periksa pesan spesifik akun dinonaktifkan
            error_msgs = [e for error_list in form.errors.values() for e in error_list]
            if any('dinonaktifkan' in m for m in error_msgs):
                messages.error(request, 'Akun Anda dinonaktifkan oleh administrator.')
            else:
                messages.error(request, 'Nama pengguna atau kata sandi tidak cocok.')
    else:
        form = StyledAuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Anda telah keluar dari akun.')
    return redirect('recipes:home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    active_tab = 'favorites'

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('accounts:profile')
        else:
            active_tab = 'edit'
            messages.error(request, 'Gagal memperbarui profil. Silakan periksa isian formulir.')
    else:
        form = ProfileUpdateForm(instance=profile)

    user_favorites = request.user.favorites.select_related('recipe', 'recipe__category').order_by('-created_at')
    user_recipes = request.user.recipes.select_related('category').order_by('-created_at')

    context = {
        'profile': profile,
        'form': form,
        'favorites': user_favorites,
        'my_recipes': user_recipes,
        'active_tab': active_tab,
    }
    return render(request, 'accounts/profile.html', context)
