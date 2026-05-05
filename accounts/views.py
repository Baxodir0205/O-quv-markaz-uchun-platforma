from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User


# ============================================================
#  YORDAMCHI FUNKSIYA
# ============================================================

def _redirect_by_role(user):
    if user.is_superuser:
        return redirect('/admin-panel/')
    if hasattr(user, 'profile'):
        role = user.profile.role
        if role == 'admin':
            return redirect('/admin-panel/')
        if role == 'teacher':
            return redirect('/teacher/')
        if role == 'student':
            return redirect('/student/')
    return redirect('/')


# ============================================================
#  REGISTER
# ============================================================

def register_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        first_name       = request.POST.get('first_name', '').strip()
        last_name        = request.POST.get('last_name', '').strip()
        username         = request.POST.get('username', '').strip()
        password         = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()

        # Validatsiya
        if not all([first_name, last_name, username, password, password_confirm]):
            messages.error(request, "Barcha maydonlarni to'ldiring!")
            return render(request, 'accounts/register.html')

        if password != password_confirm:
            messages.error(request, "Parollar bir xil emas!")
            return render(request, 'accounts/register.html')

        if len(password) < 6:
            messages.error(request, "Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu username allaqachon band!")
            return render(request, 'accounts/register.html')

        # User yaratish
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Profile
        profile = user.profile
        profile.full_name = f"{first_name} {last_name}"
        profile.role = 'student'
        profile.save()

        messages.success(request, "Ro'yxatdan o'tish muvaffaqiyatli! Endi tizimga kiring.")
        return redirect('/login/')

    return render(request, 'accounts/register.html')


# ============================================================
#  LOGIN
# ============================================================

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Username va parolni kiriting!")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Login yoki parol noto'g'ri!")
            return render(request, 'accounts/login.html')

        login(request, user)
        messages.success(request, f"Xush kelibsiz, {user.first_name}!")
        return _redirect_by_role(user)

    return render(request, 'accounts/login.html')


# ============================================================
#  LOGOUT
# ============================================================

def logout_view(request):
    logout(request)
    messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz!")
    return redirect('/login/')