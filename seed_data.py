import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from recipes.models import Category, Tag, Recipe, Ingredient, InstructionStep, RecipeNutrition

User = get_user_model()

def seed():
    print("Memulai seeding data contoh...")

    # 1. Buat Admin & Pengguna Biasa
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@dapurnusa.id',
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_user.set_password('admin123')
    admin_user.role = User.Role.ADMIN
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

    budi_user, _ = User.objects.get_or_create(
        username='budi_santoso',
        defaults={
            'email': 'budi@example.com',
            'role': User.Role.PENGGUNA
        }
    )
    budi_user.set_password('budi123')
    budi_user.save()

    print("Pengguna berhasil dibuat (admin:admin123, budi_santoso:budi123)")

    # 2. Buat Kategori
    categories_data = [
        ('Daging Sapi', 'soup_kitchen', 'Aneka masakan daging sapi empuk khas tradisi nusantara'),
        ('Ayam & Bebek', 'restaurant', 'Olahan ayam dan unggas dengan bumbu rempah melimpah'),
        ('Sayur & Sup', 'local_florist', 'Hidangan sayur mayur segar penyejuk selera'),
        ('Sambal & Cocolan', 'local_fire_department', 'Pedas nikmat menggigit pelengkap santap'),
        ('Ikan & Laut', 'set_meal', 'Sajian boga bahari berlimpah rempah nusantara'),
    ]

    cats = {}
    for name, icon, desc in categories_data:
        c, _ = Category.objects.get_or_create(name=name, defaults={'icon_name': icon, 'description': desc})
        cats[name] = c

    # 3. Buat Tags
    tag_names = ['Tradisional', 'Pedas', 'Cepat', 'Tanpa Santan', 'Menu Lebaran', 'Keluarga']
    tags = {}
    for tname in tag_names:
        t, _ = Tag.objects.get_or_create(name=tname)
        tags[tname] = t

    # 4. Buat Resep 1: Rendang Sapi Padang Asli (Featured / Menu Hari Ini)
    r1, created = Recipe.objects.get_or_create(
        title='Rendang Sapi Padang Asli',
        defaults={
            'author': admin_user,
            'category': cats['Daging Sapi'],
            'description': 'Rendang daging sapi otentik Minangkabau dengan bumbu rempah kelapa sangrai berjam-jam hingga hitam kecokelatan meresap sempurna.',
            'default_servings': 6,
            'prep_time_minutes': 30,
            'cook_time_minutes': 180,
            'difficulty': Recipe.Difficulty.SULIT,
            'status': Recipe.Status.PUBLISHED,
            'is_featured': True
        }
    )
    if created:
        r1.tags.add(tags['Tradisional'], tags['Menu Lebaran'], tags['Keluarga'])
        
        # Bahan Terstruktur
        Ingredient.objects.bulk_create([
            Ingredient(recipe=r1, sort_order=1, amount=1000, unit='gram', item_name='Daging Sapi Gandik', notes='potong melawan serat'),
            Ingredient(recipe=r1, sort_order=2, amount=1500, unit='ml', item_name='Santan Kental', notes='dari 3 butir kelapa tua'),
            Ingredient(recipe=r1, sort_order=3, amount=500, unit='ml', item_name='Santan Encer'),
            Ingredient(recipe=r1, sort_order=4, amount=4, unit='batang', item_name='Serai', notes='memarkan'),
            Ingredient(recipe=r1, sort_order=5, amount=5, unit='lembar', item_name='Daun Jeruk Purut'),
            Ingredient(recipe=r1, sort_order=6, amount=2, unit='lembar', item_name='Daun Kunyit', notes='ikat simpul'),
            Ingredient(recipe=r1, sort_order=7, amount=150, unit='gram', item_name='Cabai Merah Keriting', notes='haluskan bersama bawang'),
            Ingredient(recipe=r1, sort_order=8, amount=None, unit=None, item_name='Garam & Asam Kandis', notes='secukupnya'),
        ])

        # Langkah
        InstructionStep.objects.bulk_create([
            InstructionStep(recipe=r1, step_number=1, instruction='Haluskan bumbu halus (bawang merah, bawang putih, cabai merah, jahe, lengkuas).'),
            InstructionStep(recipe=r1, step_number=2, instruction='Rebus santan kental dan santan encer bersama bumbu halus, serai, daun jeruk, dan daun kunyit dengan api sedang sambil terus diaduk perlahan agar santan tidak pecah.'),
            InstructionStep(recipe=r1, step_number=3, instruction='Setelah santan mulai mengeluarkan minyak (tahap gulai), masukkan potongan daging sapi.'),
            InstructionStep(recipe=r1, step_number=4, instruction='Kecilkan api kompor, aduk sesekali hingga kuah mengental dan berubah warna menjadi cokelat kemerahan (tahap kalio).'),
            InstructionStep(recipe=r1, step_number=5, instruction='Lanjutkan memasak dengan api sangat kecil sambil diaduk perlahan hingga minyak terserap dan bumbu menghitam kering mengkilap.'),
        ])

        # Nutrisi
        RecipeNutrition.objects.create(recipe=r1, calories=450, protein_grams=34.5, carbs_grams=8.2, fat_grams=31.0)

    # 5. Buat Resep 2: Soto Ayam Lamongan Gurih Koya
    r2, created = Recipe.objects.get_or_create(
        title='Soto Ayam Lamongan Gurih Koya',
        defaults={
            'author': admin_user,
            'category': cats['Ayam & Bebek'],
            'description': 'Soto ayam berkuah kuning bening nan gurih dengan taburan bubuk koya renyah dari kerupuk udang dan bawang putih goreng.',
            'default_servings': 4,
            'prep_time_minutes': 25,
            'cook_time_minutes': 45,
            'difficulty': Recipe.Difficulty.SEDANG,
            'status': Recipe.Status.PUBLISHED,
            'is_featured': True
        }
    )
    if created:
        r2.tags.add(tags['Tradisional'], tags['Keluarga'])
        Ingredient.objects.bulk_create([
            Ingredient(recipe=r2, sort_order=1, amount=500, unit='gram', item_name='Ayam Kampung', notes='rebus dan suwir'),
            Ingredient(recipe=r2, sort_order=2, amount=1500, unit='ml', item_name='Air Kaldu Ayam'),
            Ingredient(recipe=r2, sort_order=3, amount=3, unit='batang', item_name='Serai', notes='memarkan'),
            Ingredient(recipe=r2, sort_order=4, amount=4, unit='lembar', item_name='Daun Jeruk'),
            Ingredient(recipe=r2, sort_order=5, amount=100, unit='gram', item_name='Soun', notes='seduh air panas'),
            Ingredient(recipe=r2, sort_order=6, amount=2, unit='butir', item_name='Telur Rebus', notes='belah dua'),
            Ingredient(recipe=r2, sort_order=7, amount=3, unit='sdm', item_name='Bubuk Koya Udang', notes='taburan'),
        ])
        InstructionStep.objects.bulk_create([
            InstructionStep(recipe=r2, step_number=1, instruction='Rebus ayam kampung hingga empuk, tiriskan lalu suwir-suwir dagingnya. Sisihkan air kaldunya.'),
            InstructionStep(recipe=r2, step_number=2, instruction='Tumis bumbu halus kuning bersama daun jeruk dan serai hingga harum semerbak, lalu tuang ke dalam air rebusan kaldu ayam.'),
            InstructionStep(recipe=r2, step_number=3, instruction='Bumbui kuah dengan garam, gula, dan merica bubuk. Masak hingga mendidih.'),
            InstructionStep(recipe=r2, step_number=4, instruction='Tata soun, kol iris, toge, dan suwiran ayam di mangkuk saji. Siram dengan kuah soto panas dan taburi bubuk koya melimpah.'),
        ])
        RecipeNutrition.objects.create(recipe=r2, calories=320, protein_grams=28.0, carbs_grams=22.0, fat_grams=12.5)

    # 6. Buat Resep 3: Sambal Bawang Korek Pedas Nampol
    r3, created = Recipe.objects.get_or_create(
        title='Sambal Bawang Korek Pedas Nampol',
        defaults={
            'author': budi_user,
            'category': cats['Sambal & Cocolan'],
            'description': 'Sambal korek khas bebek goreng Surabaya yang pedasnya menggelegar disiram minyak goreng panas mendesis.',
            'default_servings': 4,
            'prep_time_minutes': 5,
            'cook_time_minutes': 5,
            'difficulty': Recipe.Difficulty.MUDAH,
            'status': Recipe.Status.PUBLISHED,
            'is_featured': True
        }
    )
    if created:
        r3.tags.add(tags['Pedas'], tags['Cepat'], tags['Tanpa Santan'])
        Ingredient.objects.bulk_create([
            Ingredient(recipe=r3, sort_order=1, amount=25, unit='buah', item_name='Cabai Rawit Merah'),
            Ingredient(recipe=r3, sort_order=2, amount=8, unit='siung', item_name='Bawang Putih'),
            Ingredient(recipe=r3, sort_order=3, amount=5, unit='sdm', item_name='Minyak Goreng Panas'),
            Ingredient(recipe=r3, sort_order=4, amount=0.5, unit='sdt', item_name='Garam'),
        ])
        InstructionStep.objects.bulk_create([
            InstructionStep(recipe=r3, step_number=1, instruction='Ulek kasar cabai rawit merah, bawang putih, dan garam di atas cobek batu.'),
            InstructionStep(recipe=r3, step_number=2, instruction='Panaskan minyak sisa goreng ayam/bebek sampai benar-benar panas.'),
            InstructionStep(recipe=r3, step_number=3, instruction='Siram minyak mendidih langsung ke atas ulekan sambal, aduk cepat dengan sendok. Siap dihidangkan!'),
        ])
        RecipeNutrition.objects.create(recipe=r3, calories=110, protein_grams=1.2, carbs_grams=4.0, fat_grams=10.0)

    # 7. Buat Resep 4 (Pending Moderasi - untuk demonstrasi Tahap 2)
    r4, created = Recipe.objects.get_or_create(
        title='Sayur Asem Segar Jakarta',
        defaults={
            'author': budi_user,
            'category': cats['Sayur & Sup'],
            'description': 'Sayur asem bening menyegarkan dengan asam jawa muda, labu siam, kacang panjang, dan jagung manis.',
            'default_servings': 4,
            'prep_time_minutes': 15,
            'cook_time_minutes': 20,
            'difficulty': Recipe.Difficulty.MUDAH,
            'status': Recipe.Status.PENDING,
            'is_featured': False
        }
    )
    if created:
        r4.tags.add(tags['Cepat'], tags['Tanpa Santan'], tags['Keluarga'])
        Ingredient.objects.bulk_create([
            Ingredient(recipe=r4, sort_order=1, amount=1, unit='buah', item_name='Jagung Manis', notes='potong 4 bagian'),
            Ingredient(recipe=r4, sort_order=2, amount=1, unit='buah', item_name='Labu Siam', notes='potong dadu'),
            Ingredient(recipe=r4, sort_order=3, amount=5, unit='batang', item_name='Kacang Panjang'),
            Ingredient(recipe=r4, sort_order=4, amount=3, unit='buah', item_name='Asam Jawa Muda'),
        ])
        InstructionStep.objects.bulk_create([
            InstructionStep(recipe=r4, step_number=1, instruction='Didihkan air bersama asam jawa muda, lengkuas, dan daun salam.'),
            InstructionStep(recipe=r4, step_number=2, instruction='Masukkan sayuran keras terlebih dahulu seperti jagung dan kacang tanah.'),
            InstructionStep(recipe=r4, step_number=3, instruction='Masukkan labu siam dan kacang panjang, bumbui dengan garam dan gula merah hingga rasa asam gurih seimbang.'),
        ])

    print("Data contoh nusantara berhasil di-seed!")

if __name__ == '__main__':
    seed()
