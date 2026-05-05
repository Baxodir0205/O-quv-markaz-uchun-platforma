from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from accounts.models import Profile
from education.models import Group, TeacherGroup


def admin_dashboard(request):
    total_accounts = User.objects.count()
    teachers_count = Profile.objects.filter(role='teacher').count()
    students_count = Profile.objects.filter(role='student').count()
    groups_count = Group.objects.count()

    latest_users = User.objects.select_related(
        'profile',
        'profile__group'
    ).order_by('-id')[:5]

    students_without_group = Profile.objects.filter(
        role='student',
        group__isnull=True
    ).count()

    empty_groups = Group.objects.filter(
        student_profiles__isnull=True
    ).distinct().count()

    return render(request, 'adminpanel/dashboard.html', {
        'total_accounts': total_accounts,
        'teachers_count': teachers_count,
        'students_count': students_count,
        'groups_count': groups_count,
        'latest_users': latest_users,
        'students_without_group': students_without_group,
        'empty_groups': empty_groups,
    })


def accounts_list(request):
    search = request.GET.get('search', '').strip()
    no_group = request.GET.get('no_group')
    role = request.GET.get('role', '').strip()

    users = User.objects.select_related(
        'profile',
        'profile__group'
    ).order_by('-id')

    if role in ['teacher', 'student']:
        users = users.filter(profile__role=role)

    if no_group == '1':
        users = users.filter(
            profile__role='student',
            profile__group__isnull=True
        )

    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(username__icontains=search) |
            Q(profile__full_name__icontains=search) |
            Q(profile__role__icontains=search) |
            Q(profile__group__name__icontains=search)
        )

    return render(request, 'adminpanel/accounts_list.html', {
        'users': users,
        'search': search,
        'no_group': no_group,
        'role': role,
    })


def new_account(request):
    groups = Group.objects.all().order_by('name')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        role = request.POST.get('role', 'student')
        group_id = request.POST.get('group')
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()

        if not first_name or not last_name:
            messages.error(request, "Ism va familiya kiritilishi shart!")
            return redirect('adminpanel:new_account')

        if not username:
            messages.error(request, "Username kiritilishi shart!")
            return redirect('adminpanel:new_account')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu username allaqachon mavjud!")
            return redirect('adminpanel:new_account')

        if not password:
            messages.error(request, "Parol kiritilishi shart!")
            return redirect('adminpanel:new_account')

        if password != password_confirm:
            messages.error(request, "Parollar bir xil emas!")
            return redirect('adminpanel:new_account')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        profile = user.profile
        profile.full_name = f"{first_name} {last_name}"
        profile.role = role

        if role == 'student' and group_id:
            profile.group_id = group_id
        else:
            profile.group = None

        profile.save()

        if role == 'teacher' and group_id:
            TeacherGroup.objects.get_or_create(
                teacher=user,
                group_id=group_id,
                subject=None
            )

        messages.success(request, f"Account yaratildi. Username: {username}")
        return redirect('adminpanel:accounts_list')

    return render(request, 'adminpanel/new_account.html', {
        'groups': groups
    })


def edit_account(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    groups = Group.objects.all().order_by('name')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        role = request.POST.get('role', 'student')
        group_id = request.POST.get('group')
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()

        if not first_name or not last_name:
            messages.error(request, "Ism va familiya bo‘sh bo‘lmasin!")
            return redirect('adminpanel:edit_account', user_id=user.id)

        if not username:
            messages.error(request, "Username bo‘sh bo‘lmasin!")
            return redirect('adminpanel:edit_account', user_id=user.id)

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, "Bu username boshqa accountda mavjud!")
            return redirect('adminpanel:edit_account', user_id=user.id)

        if password or password_confirm:
            if password != password_confirm:
                messages.error(request, "Parollar bir xil emas!")
                return redirect('adminpanel:edit_account', user_id=user.id)

            user.set_password(password)

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.save()

        profile.full_name = f"{first_name} {last_name}"
        profile.role = role

        if role == 'student':
            TeacherGroup.objects.filter(teacher=user).delete()
            profile.group_id = group_id if group_id else None

        elif role == 'teacher':
            profile.group = None
            TeacherGroup.objects.filter(teacher=user).delete()

            if group_id:
                TeacherGroup.objects.get_or_create(
                    teacher=user,
                    group_id=group_id,
                    subject=None
                )

        profile.save()

        messages.success(request, "Account yangilandi!")
        return redirect('adminpanel:accounts_list')

    return render(request, 'adminpanel/edit_account.html', {
        'edit_user': user,
        'profile': profile,
        'groups': groups,
    })


def delete_account(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, "Account o'chirildi!")
        return redirect('adminpanel:accounts_list')

    return redirect('adminpanel:accounts_list')


def groups_list(request):
    groups = Group.objects.all().order_by('name')

    return render(request, 'adminpanel/groups_list.html', {
        'groups': groups
    })


def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    students = Profile.objects.filter(
        role='student',
        group=group
    ).select_related('user')

    teachers = TeacherGroup.objects.filter(
        group=group
    ).select_related('teacher')

    return render(request, 'adminpanel/group_detail.html', {
        'group': group,
        'students': students,
        'teachers': teachers,
    })


def remove_student_from_group(request, group_id, profile_id):
    profile = get_object_or_404(
        Profile,
        id=profile_id,
        role='student',
        group_id=group_id
    )

    if request.method == 'POST':
        profile.group = None
        profile.save()
        messages.success(request, "Student guruhdan chiqarildi!")

    return redirect('adminpanel:group_detail', group_id=group_id)


def new_group(request):
    teachers = Profile.objects.filter(
        role='teacher'
    ).select_related('user').order_by('user__first_name')

    students = Profile.objects.filter(
        role='student'
    ).select_related('user').order_by('user__first_name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        teacher_ids = request.POST.getlist('teachers')
        student_ids = request.POST.getlist('students')

        if not name:
            messages.error(request, "Guruh nomi kiritilishi shart!")
            return redirect('adminpanel:new_group')

        if Group.objects.filter(name=name).exists():
            messages.error(request, "Bu guruh oldin yaratilgan!")
            return redirect('adminpanel:new_group')

        group = Group.objects.create(name=name)

        for teacher_profile_id in teacher_ids:
            teacher_profile = Profile.objects.get(
                id=teacher_profile_id,
                role='teacher'
            )

            TeacherGroup.objects.get_or_create(
                teacher=teacher_profile.user,
                group=group,
                subject=None
            )

        for student_profile_id in student_ids:
            student_profile = Profile.objects.get(
                id=student_profile_id,
                role='student'
            )
            student_profile.group = group
            student_profile.save()

        messages.success(request, "Guruh yaratildi!")
        return redirect('adminpanel:group_detail', group_id=group.id)

    return render(request, 'adminpanel/new_group.html', {
        'teachers': teachers,
        'students': students,
    })


def admin_logout(request):
    logout(request)
    return redirect('login')
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        group.delete()
        messages.success(request, "Guruh butunlay o‘chirildi!")
        return redirect('adminpanel:groups_list')

    return redirect('adminpanel:group_detail', group_id=group.id)