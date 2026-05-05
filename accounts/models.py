from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    full_name = models.CharField(max_length=150, blank=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    group = models.ForeignKey(
        'education.Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='student_profiles'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    coins = models.PositiveIntegerField(default=0)
    badge_count = models.PositiveIntegerField(default=0)

    def add_xp(self, amount):
        self.xp += amount
        self.coins += amount // 2

        new_level = (self.xp // 100) + 1

        if new_level > self.level:
            self.level = new_level
            self.badge_count += 1

        self.save()

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'

    def __str__(self):
        return self.full_name or self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}".strip()

    if not full_name:
        full_name = instance.username

    profile, created_profile = Profile.objects.get_or_create(
        user=instance,
        defaults={
            'full_name': full_name
        }
    )

    if not profile.full_name:
        profile.full_name = full_name

    profile.save()