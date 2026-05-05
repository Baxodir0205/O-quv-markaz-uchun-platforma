from django.contrib import admin
from .models import CaseStudy, CaseSubmission


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'teacher',
        'group',
        'level',
        'max_score',
        'xp_reward',
        'coin_reward',
        'is_published',
        'created_at',
    )

    list_filter = (
        'level',
        'group',
        'is_published',
        'created_at',
    )

    search_fields = (
        'title',
        'short_description',
        'situation',
        'task',
        'teacher__username',
        'group__name',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'created_at',
    )


@admin.register(CaseSubmission)
class CaseSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'case',
        'score',
        'status',
        'is_rewarded',
        'submitted_at',
        'checked_at',
    )

    list_filter = (
        'status',
        'is_rewarded',
        'submitted_at',
    )

    search_fields = (
        'student__username',
        'case__title',
        'answer',
    )

    readonly_fields = (
        'submitted_at',
        'checked_at',
    )