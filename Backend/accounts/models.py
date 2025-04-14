from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # Konum bilgileri
    latitude = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Enlem (örnek: 37.23)"
    )
    longitude = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Boylam (örnek: 42.54)"
    )
    location_name = models.CharField(
        max_length=255,
        blank=True, null=True,
        help_text="Şehir, semt ya da adres bilgisi"
    )
    is_location_visible = models.BooleanField(
        default=True,
        help_text="Kullanıcının konumu başkalarına gösterilsin mi?"
    )

    # Ek kullanıcı bilgileri
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        blank=True, null=True
    )
    website = models.URLField(blank=True, null=True)
    is_private = models.BooleanField(default=False)

    # Kayıt ve durum bilgileri
    signup_method = models.CharField(max_length=20, default='email')  # email, google, apple
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
