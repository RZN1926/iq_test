from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        blank=True,
        verbose_name='Аватар'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='О себе'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def save(self, *args, **kwargs):
        # Сохраняем без оптимизации размера
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаем профиль при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняем профиль при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Question(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)  # ← добавили
    option1 = models.ImageField(upload_to='answers/', blank=True, null=True)
    option2 = models.ImageField(upload_to='answers/', blank=True, null=True)
    option3 = models.ImageField(upload_to='answers/', blank=True, null=True)
    option4 = models.ImageField(upload_to='answers/', blank=True, null=True)
    option5 = models.ImageField(upload_to='answers/', blank=True, null=True)
    option6 = models.ImageField(upload_to='answers/', blank=True, null=True)
    correct_option = models.IntegerField()  # 1-4

    def __str__(self):
        return self.text

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}"
