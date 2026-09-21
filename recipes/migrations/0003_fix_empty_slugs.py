from django.db import migrations
from django.utils.text import slugify

def fix_empty_slugs(apps, schema_editor):
    Category = apps.get_model('recipes', 'Category')
    Tag = apps.get_model('recipes', 'Tag')
    Recipe = apps.get_model('recipes', 'Recipe')

    for cat in Category.objects.all():
        if not cat.slug or not cat.slug.strip():
            base = (slugify(cat.name) or 'kategori')[:100]
            slug = base
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=cat.pk).exists():
                slug = f"{base[:90]}-{counter}"
                counter += 1
            cat.slug = slug
            cat.save(update_fields=['slug'])

    for tag in Tag.objects.all():
        if not tag.slug or not tag.slug.strip():
            base = (slugify(tag.name) or 'tag')[:50]
            slug = base
            counter = 1
            while Tag.objects.filter(slug=slug).exclude(pk=tag.pk).exists():
                slug = f"{base[:40]}-{counter}"
                counter += 1
            tag.slug = slug
            tag.save(update_fields=['slug'])

    for recipe in Recipe.objects.all():
        if not recipe.slug or not recipe.slug.strip():
            base = (slugify(recipe.title) or 'resep')[:200]
            slug = base
            counter = 1
            while Recipe.objects.filter(slug=slug).exclude(pk=recipe.pk).exists():
                slug = f"{base[:180]}-{counter}"
                counter += 1
            recipe.slug = slug
            recipe.save(update_fields=['slug'])

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_ingredient_amount_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs, reverse_func),
    ]
