from django.db import models
from django.contrib.auth.models import User
from education.models import Group


class Lesson(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_lessons'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='dashboard_lessons'
    )

    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='lessons/files/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title or "Lesson"


class Assignment(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='dashboard_assignments'
    )

    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    deadline = models.DateTimeField(blank=True, null=True)
    file = models.FileField(upload_to='assignments/files/', blank=True, null=True)

    max_score = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title or "Assignment"


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    answer_text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='submissions/files/', blank=True, null=True)

    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


# ==================================================
# TEST SYSTEM
# Test = bitta umumiy test
# TestQuestion = test ichidagi savollar
# TestResult = studentning umumiy natijasi
# TestAnswer = studentning har bir savolga javobi
# ==================================================

class Test(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_tests'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='dashboard_tests'
    )

    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Eski fieldlar qoladi.
    # Bularni o‘chirmaymiz, chunki migratsiyada savol chiqmasin.
    question = models.TextField(blank=True, null=True)
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title or "Test"


class TestQuestion(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    question = models.TextField(blank=True, null=True)

    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)

    correct_answer = models.CharField(max_length=1, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.question[:50] if self.question else "Test Question"


class TestResult(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='results'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Eski fieldlar qoladi.
    selected_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    # Yangi umumiy natija
    total_questions = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        unique_together = ('test', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.test.title}"


class TestAnswer(models.Model):
    result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        TestQuestion,
        on_delete=models.CASCADE,
        related_name='student_answers'
    )

    selected_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.result.student.username} - {self.question.id}"


class CaseStudy(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_case_studies'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='dashboard_case_studies'
    )

    title = models.CharField(max_length=255, blank=True, null=True)

    short_description = models.TextField(blank=True, null=True)
    situation = models.TextField(blank=True, null=True)
    task = models.TextField(blank=True, null=True)
    expected_result = models.TextField(blank=True, null=True)

    thumbnail = models.ImageField(upload_to='cases/thumbnails/', blank=True, null=True)

    level = models.CharField(max_length=20, default='easy')
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=100)

    is_published = models.BooleanField(default=True)
    deadline = models.DateTimeField(blank=True, null=True)

    # Eski variantli case fieldlari qoladi.
    question = models.TextField(blank=True, null=True)
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title or "Case Study"


class CaseStudyResult(models.Model):
    case = models.ForeignKey(
        CaseStudy,
        on_delete=models.CASCADE,
        related_name='results'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        unique_together = ('case', 'student')