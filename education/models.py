from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def student_count(self):
        return self.student_profiles.count()

    def teacher_count(self):
        return self.teacher_groups.values('teacher').distinct().count()

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return self.name


class TeacherGroup(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_groups'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='teacher_groups'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='teacher_groups'
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('teacher', 'group', 'subject')
        ordering = ['group__name']
        verbose_name = 'Teacher Group'
        verbose_name_plural = 'Teacher Groups'

    def __str__(self):
        subject_name = self.subject.name if self.subject else "Fan yo‘q"
        return f"{self.teacher.username} - {self.group.name} - {subject_name}"