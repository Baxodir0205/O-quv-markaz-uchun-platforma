from django.contrib import admin
from .models import Group, Subject, TeacherGroup


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TeacherGroup)
class TeacherGroupAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'group', 'subject')
    list_filter = ('group', 'subject')
    search_fields = ('teacher__username', 'group__name', 'subject__name')