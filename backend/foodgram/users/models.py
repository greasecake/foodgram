from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=254, unique=True, verbose_name='Логин'
    )
    first_name = models.CharField(
        max_length=254, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=254, verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name='Почта'
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
