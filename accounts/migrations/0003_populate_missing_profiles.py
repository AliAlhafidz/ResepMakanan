from django.db import migrations

def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for user in User.objects.all():
        if not UserProfile.objects.filter(user=user).exists():
            display = user.first_name or user.username
            UserProfile.objects.create(user=user, display_name=display)

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_avatar'),
    ]

    operations = [
        migrations.RunPython(create_profiles_for_existing_users, reverse_func),
    ]
