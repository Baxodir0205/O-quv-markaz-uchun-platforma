from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'xp', 'level', 'coins', 'badge_count')
    list_filter = ('role',)
    search_fields = ('user__username', 'full_name')


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass