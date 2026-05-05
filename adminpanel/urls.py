from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),

    path('new-account/', views.new_account, name='new_account'),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/<int:user_id>/edit/', views.edit_account, name='edit_account'),
    path('accounts/<int:user_id>/delete/', views.delete_account, name='delete_account'),

    path('groups/', views.groups_list, name='groups_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path(
        'groups/<int:group_id>/remove-student/<int:profile_id>/',
        views.remove_student_from_group,
        name='remove_student_from_group'
    ),

    path('new-group/', views.new_group, name='new_group'),
    path('logout/', views.admin_logout, name='admin_logout'),
]