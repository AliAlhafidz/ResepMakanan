from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from PIL import Image

def validate_image_file(image):
    if not image:
        return
    max_size_mb = 2
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Ukuran gambar maksimal {max_size_mb} MB.")
    try:
        # Periksa format gambar menggunakan Pillow
        img = Image.open(image)
        img.verify()
        if img.format.upper() not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
            raise ValidationError("Format gambar harus JPEG, PNG, atau WEBP.")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError("File yang diunggah bukan file gambar yang valid.")


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True, help_text="Nama ikon misal: soup_kitchen, restaurant, local_fire_department")
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = (slugify(self.name) or "kategori")[:100]
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug[:90]}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = (slugify(self.name) or "tag")[:50]
            slug = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug[:40]}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        MUDAH = 'MUDAH', 'Mudah'
        SEDANG = 'SEDANG', 'Sedang'
        SULIT = 'SULIT', 'Sulit'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING = 'PENDING', 'Pending Moderasi'
        PUBLISHED = 'PUBLISHED', 'Diterbitkan'
        REJECTED = 'REJECTED', 'Ditolak'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='recipes')
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True, null=True, validators=[validate_image_file])
    default_servings = models.PositiveSmallIntegerField(default=4, validators=[MinValueValidator(1)])
    prep_time_minutes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], help_text="Waktu persiapan dalam menit")
    cook_time_minutes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], help_text="Waktu masak dalam menit")
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.SEDANG)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PUBLISHED)
    is_featured = models.BooleanField(default=False, db_index=True, help_text="Tampilkan di seksi Menu Hari Ini")
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_time(self):
        return self.prep_time_minutes + self.cook_time_minutes

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = (slugify(self.title) or "resep")[:200]
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug[:180]}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    amount = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)],
        help_text="Jumlah numerik untuk porsi standar (bisa kosong jika secukupnya)"
    )
    unit = models.CharField(max_length=30, blank=True, null=True, help_text="Contoh: gram, ml, sdm, sdt, butir, siung")
    item_name = models.CharField(max_length=150)
    notes = models.CharField(max_length=100, blank=True, null=True, help_text="Contoh: cincang halus, iris tipis, secukupnya")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        parts = []
        if self.amount is not None:
            amt_str = f"{self.amount:g}"
            parts.append(amt_str)
        if self.unit:
            parts.append(self.unit)
        parts.append(self.item_name)
        if self.notes:
            parts.append(f"({self.notes})")
        return " ".join(parts)


class InstructionStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    instruction = models.TextField()
    step_image = models.ImageField(upload_to='steps/', blank=True, null=True, validators=[validate_image_file])

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Langkah {self.step_number} - {self.recipe.title}"


class RecipeNutrition(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name='nutrition')
    calories = models.PositiveSmallIntegerField(blank=True, null=True, help_text="Kkal per porsi")
    protein_grams = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    carbs_grams = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    fat_grams = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return f"Nutrisi untuk {self.recipe.title}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} menyukai {self.recipe.title}"


class MealPlan(models.Model):
    class MealTime(models.TextChoices):
        SARAPAN = 'SARAPAN', 'Sarapan'
        SIANG = 'SIANG', 'Makan Siang'
        MALAM = 'MALAM', 'Makan Malam'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='meal_plans')
    plan_date = models.DateField(db_index=True)
    meal_time = models.CharField(max_length=15, choices=MealTime.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['plan_date', 'meal_time']

    def __str__(self):
        return f"{self.plan_date} [{self.meal_time}] - {self.recipe.title}"


class ShoppingListItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopping_items')
    amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=30, blank=True, null=True)
    item_name = models.CharField(max_length=150)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        parts = [self.item_name]
        amount_part = []
        if self.amount is not None:
            amount_part.append(f"{self.amount:g}")
        if self.unit:
            amount_part.append(self.unit)
        if amount_part:
            parts.append(f"({' '.join(amount_part)})")
        parts.append(f"- {'[X]' if self.is_checked else '[ ]'}")
        return " ".join(parts)
