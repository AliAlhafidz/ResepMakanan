from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes.models import validate_image_file

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        PENGGUNA = 'PENGGUNA', 'Pengguna'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PENGGUNA
    )

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, validators=[validate_image_file])
    bio = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil {self.display_name or self.user.username}"
