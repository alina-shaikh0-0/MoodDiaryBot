from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return str(self.chat_id)


# Create your models here.
"""class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_users_groups',  # Уникальное имя обратной связи
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_users_permissions',  # Уникальное имя обратной связи
    )"""


class Emotion(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()


class MoodEntry(models.Model):
    """MOOD_CHOICES = [
        ('Joy', 'Joy'),
        ('Sadness', 'Sadness'),
        ('Anger', 'Anger'),
        ('Calm', 'Calm'),
        ('Surprise', 'Surprise'),
        ('Love', 'Love'),
    ]"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    emotion = models.CharField(max_length=50)
    """, choices=MOOD_CHOICES"""

    def __str__(self):
        return f"{self.user.username}'s mood entry on {self.date}"


class Statistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    average_mood = models.FloatField(default=0.0)


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f'{self.user.username}\'s event: {self.title}'


class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_date = models.DateTimeField()
    message = models.TextField()


class Tag(models.Model):
    name = models.CharField(max_length=50)


class DiaryPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    title = models.CharField(max_length=100)
    content = models.TextField()

    def save(self, *args, **kwargs):
        # Формирование заголовка при первом сохранении
        if not self.title:
            today = timezone.localdate()
            count = DiaryPage.objects.filter(date=today).count()
            self.title = f"{today:%d.%m.%Y} {count + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s diary page on {self.date}: {self.title}"

"""class DiaryPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    tags = models.ManyToManyField(Tag)"""