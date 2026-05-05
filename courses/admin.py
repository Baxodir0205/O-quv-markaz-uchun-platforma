from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'level', 'is_published', 'created_at')
    list_filter = ('level', 'is_published')
    search_fields = ('title', 'teacher__username')
    prepopulated_fields = {'slug': ('title',)}