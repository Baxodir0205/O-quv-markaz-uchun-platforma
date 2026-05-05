from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class CaseStudy(models.Model):
    LEVEL_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    short_description = models.CharField(max_length=255, blank=True)
    situation = models.TextField()
    task = models.TextField()
    expected_result = models.TextField(blank=True, null=True)

    group = models.ForeignKey(
        'education.Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='case_studies'
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_cases'
    )

    thumbnail = models.ImageField(
        upload_to='cases/thumbnails/',
        blank=True,
        null=True
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='easy'
    )

    max_score = models.PositiveIntegerField(default=100)
    xp_reward = models.PositiveIntegerField(default=20)
    coin_reward = models.PositiveIntegerField(default=10)

    is_published = models.BooleanField(default=True)
    deadline = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'

    def __str__(self):
        return self.title

    def submission_count(self):
        return self.submissions.count()

    def is_submitted_by(self, user):
        return self.submissions.filter(student=user).exists()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)

            if not base_slug:
                base_slug = "case-study"

            slug = base_slug
            count = 1

            while CaseStudy.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


class CaseSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('checked', 'Checked'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='case_submissions'
    )

    case = models.ForeignKey(
        CaseStudy,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    answer = models.TextField()

    score = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )

    is_rewarded = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)
    checked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('student', 'case')
        verbose_name = 'Case Submission'
        verbose_name_plural = 'Case Submissions'

    def __str__(self):
        return f"{self.student.username} - {self.case.title}"

    def give_reward(self):
        if self.status == 'checked' and not self.is_rewarded:
            profile = self.student.profile

            profile.add_xp(self.case.xp_reward)
            profile.coins += self.case.coin_reward
            profile.save()

            self.is_rewarded = True
            self.save()