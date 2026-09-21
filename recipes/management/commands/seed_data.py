"""
Management command: seed_data
Mengisi database dengan data contoh untuk development dan demo.

Penggunaan:
    python manage.py seed_data
    python manage.py seed_data --force   # Hapus data lama sebelum seed
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import (
    Category, Ingredient, InstructionStep, Recipe, RecipeNutrition, Tag
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Mengisi database dengan data contoh resep nusantara untuk demo/development.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Hapus semua data resep, kategori, dan pengguna demo sebelum seed ulang.',
        )

    def handle(self, *args, **options):
        if options['force']:
            self.stdout.write(self.style.WARNING('Mode --force: menghapus data demo lama...'))
            Recipe.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            User.objects.filter(username__in=['admin', 'budi_santoso']).delete()

        self._seed()
        self.stdout.write(self.style.SUCCESS('✅ Data contoh nusantara berhasil di-seed!'))

    def _seed(self):
        # ----------------------------------------------------------------
        # 1. Pengguna
        # ----------------------------------------------------------------
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@dapurnusa.id',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
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
                'role': User.Role.PENGGUNA,
            }
        )
        budi_user.set_password('budi123')
        budi_user.save()

        self.stdout.write('  👤 Pengguna: admin / budi_santoso')

        # ----------------------------------------------------------------
        # 2. Kategori
        # ----------------------------------------------------------------
        categories_data = [
            ('Daging Sapi', 'soup_kitchen', 'Aneka masakan daging sapi empuk khas tradisi nusantara'),
            ('Ayam & Bebek', 'restaurant', 'Olahan ayam dan unggas dengan bumbu rempah melimpah'),
            ('Sayur & Sup', 'local_florist', 'Hidangan sayur mayur segar penyejuk selera'),
            ('Sambal & Cocolan', 'local_fire_department', 'Pedas nikmat menggigit pelengkap santap'),
            ('Ikan & Laut', 'set_meal', 'Sajian boga bahari berlimpah rempah nusantara'),
        ]
        cats = {}
        for name, icon, desc in categories_data:
            c, _ = Category.objects.get_or_create(
                name=name,
                defaults={'icon_name': icon, 'description': desc}
            )
            cats[name] = c
        self.stdout.write(f'  📂 Kategori: {len(cats)} dibuat/ditemukan')

        # ----------------------------------------------------------------
        # 3. Tags
        # ----------------------------------------------------------------
        tag_names = ['Tradisional', 'Pedas', 'Cepat', 'Tanpa Santan', 'Menu Lebaran', 'Keluarga']
        tags = {}
        for tname in tag_names:
            t, _ = Tag.objects.get_or_create(name=tname)
            tags[tname] = t
        self.stdout.write(f'  🏷️  Tag: {len(tags)} dibuat/ditemukan')

        # ----------------------------------------------------------------
        # 4. Resep 1: Rendang Sapi Padang Asli (Featured)
        # ----------------------------------------------------------------
        r1, created = Recipe.objects.get_or_create(
            title='Rendang Sapi Padang Asli',
            defaults={
                'author': admin_user,
                'category': cats['Daging Sapi'],
                'description': (
                    'Rendang daging sapi otentik Minangkabau dengan bumbu rempah kelapa sangrai '
                    'berjam-jam hingga hitam kecokelatan meresap sempurna. Makin enak keesokan harinya!'
                ),
                'default_servings': 6,
                'prep_time_minutes': 30,
                'cook_time_minutes': 180,
                'difficulty': Recipe.Difficulty.SULIT,
                'status': Recipe.Status.PUBLISHED,
                'is_featured': True,
                'notes': (
                    'Kunci rendang hitam sempurna ada di kesabaran — aduk terus dengan api kecil. '
                    'Gunakan wajan besi atau kuali tanah liat untuk hasil terbaik.'
                ),
            }
        )
        if created:
            r1.tags.add(tags['Tradisional'], tags['Menu Lebaran'], tags['Keluarga'])
            Ingredient.objects.bulk_create([
                Ingredient(recipe=r1, sort_order=1, amount=Decimal('1000'), unit='gram',
                           item_name='Daging Sapi Gandik', notes='potong melawan serat 4x6 cm'),
                Ingredient(recipe=r1, sort_order=2, amount=Decimal('1500'), unit='ml',
                           item_name='Santan Kental', notes='dari 3 butir kelapa tua'),
                Ingredient(recipe=r1, sort_order=3, amount=Decimal('500'), unit='ml',
                           item_name='Santan Encer'),
                # Bumbu halus
                Ingredient(recipe=r1, sort_order=4, amount=Decimal('150'), unit='gram',
                           item_name='Cabai Merah Keriting', notes='haluskan'),
                Ingredient(recipe=r1, sort_order=5, amount=Decimal('15'), unit='siung',
                           item_name='Bawang Merah', notes='haluskan'),
                Ingredient(recipe=r1, sort_order=6, amount=Decimal('8'), unit='siung',
                           item_name='Bawang Putih', notes='haluskan'),
                Ingredient(recipe=r1, sort_order=7, amount=Decimal('4'), unit='cm',
                           item_name='Jahe', notes='haluskan'),
                Ingredient(recipe=r1, sort_order=8, amount=Decimal('4'), unit='cm',
                           item_name='Lengkuas', notes='haluskan sebagian, sisanya memarkan'),
                Ingredient(recipe=r1, sort_order=9, amount=Decimal('3'), unit='cm',
                           item_name='Kunyit', notes='haluskan'),
                # Bumbu utuh
                Ingredient(recipe=r1, sort_order=10, amount=Decimal('4'), unit='batang',
                           item_name='Serai', notes='memarkan'),
                Ingredient(recipe=r1, sort_order=11, amount=Decimal('5'), unit='lembar',
                           item_name='Daun Jeruk Purut'),
                Ingredient(recipe=r1, sort_order=12, amount=Decimal('2'), unit='lembar',
                           item_name='Daun Kunyit', notes='ikat simpul'),
                Ingredient(recipe=r1, sort_order=13, amount=Decimal('2'), unit='buah',
                           item_name='Asam Kandis'),
                Ingredient(recipe=r1, sort_order=14, amount=None, unit=None,
                           item_name='Garam', notes='secukupnya'),
            ])
            InstructionStep.objects.bulk_create([
                InstructionStep(recipe=r1, step_number=1,
                                instruction='Haluskan bumbu: bawang merah, bawang putih, cabai merah, jahe, lengkuas, dan kunyit hingga benar-benar halus.'),
                InstructionStep(recipe=r1, step_number=2,
                                instruction='Rebus santan kental dan encer bersama bumbu halus, serai, daun jeruk, daun kunyit, dan asam kandis di atas api sedang sambil terus diaduk agar santan tidak pecah.'),
                InstructionStep(recipe=r1, step_number=3,
                                instruction='Setelah santan mulai mengeluarkan minyak (tahap gulai), masukkan potongan daging sapi. Aduk rata dan bumbui dengan garam.'),
                InstructionStep(recipe=r1, step_number=4,
                                instruction='Kecilkan api, aduk sesekali hingga kuah mengental dan berubah warna cokelat kemerahan (tahap kalio). Proses ini ±60 menit.'),
                InstructionStep(recipe=r1, step_number=5,
                                instruction='Lanjutkan memasak api sangat kecil sambil terus diaduk perlahan hingga minyak terserap dan bumbu menghitam kering mengkilap. Rendang sempurna!'),
            ])
            RecipeNutrition.objects.create(
                recipe=r1, calories=450, protein_grams=Decimal('34.5'),
                carbs_grams=Decimal('8.2'), fat_grams=Decimal('31.0')
            )
            self.stdout.write('  🍖 Rendang Sapi Padang Asli — dibuat')

        # ----------------------------------------------------------------
        # 5. Resep 2: Soto Ayam Lamongan (Featured)
        # ----------------------------------------------------------------
        r2, created = Recipe.objects.get_or_create(
            title='Soto Ayam Lamongan Gurih Koya',
            defaults={
                'author': admin_user,
                'category': cats['Ayam & Bebek'],
                'description': (
                    'Soto ayam berkuah kuning bening nan gurih dengan taburan bubuk koya renyah '
                    'dari kerupuk udang dan bawang putih goreng khas Lamongan, Jawa Timur.'
                ),
                'default_servings': 4,
                'prep_time_minutes': 25,
                'cook_time_minutes': 45,
                'difficulty': Recipe.Difficulty.SEDANG,
                'status': Recipe.Status.PUBLISHED,
                'is_featured': True,
            }
        )
        if created:
            r2.tags.add(tags['Tradisional'], tags['Keluarga'])
            Ingredient.objects.bulk_create([
                Ingredient(recipe=r2, sort_order=1, amount=Decimal('500'), unit='gram',
                           item_name='Ayam Kampung', notes='rebus dan suwir'),
                Ingredient(recipe=r2, sort_order=2, amount=Decimal('1500'), unit='ml',
                           item_name='Air Kaldu Ayam'),
                # Bumbu halus
                Ingredient(recipe=r2, sort_order=3, amount=Decimal('8'), unit='siung',
                           item_name='Bawang Merah', notes='haluskan'),
                Ingredient(recipe=r2, sort_order=4, amount=Decimal('5'), unit='siung',
                           item_name='Bawang Putih', notes='haluskan'),
                Ingredient(recipe=r2, sort_order=5, amount=Decimal('3'), unit='cm',
                           item_name='Kunyit', notes='haluskan'),
                Ingredient(recipe=r2, sort_order=6, amount=Decimal('2'), unit='cm',
                           item_name='Jahe', notes='haluskan'),
                # Bumbu utuh
                Ingredient(recipe=r2, sort_order=7, amount=Decimal('3'), unit='batang',
                           item_name='Serai', notes='memarkan'),
                Ingredient(recipe=r2, sort_order=8, amount=Decimal('4'), unit='lembar',
                           item_name='Daun Jeruk'),
                # Isian
                Ingredient(recipe=r2, sort_order=9, amount=Decimal('100'), unit='gram',
                           item_name='Soun', notes='seduh air panas'),
                Ingredient(recipe=r2, sort_order=10, amount=Decimal('2'), unit='butir',
                           item_name='Telur Rebus', notes='belah dua'),
                Ingredient(recipe=r2, sort_order=11, amount=Decimal('3'), unit='sdm',
                           item_name='Bubuk Koya Udang', notes='taburan'),
                Ingredient(recipe=r2, sort_order=12, amount=None, unit=None,
                           item_name='Garam, Gula & Merica', notes='secukupnya'),
            ])
            InstructionStep.objects.bulk_create([
                InstructionStep(recipe=r2, step_number=1,
                                instruction='Rebus ayam kampung dengan air hingga empuk. Angkat, suwir dagingnya. Saring kaldunya.'),
                InstructionStep(recipe=r2, step_number=2,
                                instruction='Haluskan bawang merah, bawang putih, kunyit, dan jahe. Tumis dengan sedikit minyak bersama serai dan daun jeruk hingga harum.'),
                InstructionStep(recipe=r2, step_number=3,
                                instruction='Tuangkan kaldu ayam ke dalam tumisan bumbu. Didihkan lalu bumbui dengan garam, gula, dan merica.'),
                InstructionStep(recipe=r2, step_number=4,
                                instruction='Tata soun, kol iris, toge rebus, dan suwiran ayam di mangkuk. Siram kuah soto panas dan taburi bubuk koya melimpah.'),
            ])
            RecipeNutrition.objects.create(
                recipe=r2, calories=320, protein_grams=Decimal('28.0'),
                carbs_grams=Decimal('22.0'), fat_grams=Decimal('12.5')
            )
            self.stdout.write('  🍜 Soto Ayam Lamongan — dibuat')

        # ----------------------------------------------------------------
        # 6. Resep 3: Sambal Bawang Korek (Featured, oleh Budi)
        # ----------------------------------------------------------------
        r3, created = Recipe.objects.get_or_create(
            title='Sambal Bawang Korek Pedas Nampol',
            defaults={
                'author': budi_user,
                'category': cats['Sambal & Cocolan'],
                'description': (
                    'Sambal korek khas bebek goreng Surabaya yang pedasnya menggelegar, '
                    'disiram minyak goreng panas mendesis. Mudah, cepat, dan bikin nagih!'
                ),
                'default_servings': 4,
                'prep_time_minutes': 5,
                'cook_time_minutes': 5,
                'difficulty': Recipe.Difficulty.MUDAH,
                'status': Recipe.Status.PUBLISHED,
                'is_featured': True,
            }
        )
        if created:
            r3.tags.add(tags['Pedas'], tags['Cepat'], tags['Tanpa Santan'])
            Ingredient.objects.bulk_create([
                Ingredient(recipe=r3, sort_order=1, amount=Decimal('25'), unit='buah',
                           item_name='Cabai Rawit Merah'),
                Ingredient(recipe=r3, sort_order=2, amount=Decimal('8'), unit='siung',
                           item_name='Bawang Putih'),
                Ingredient(recipe=r3, sort_order=3, amount=Decimal('5'), unit='sdm',
                           item_name='Minyak Goreng Panas', notes='sisa menggoreng ayam/bebek'),
                Ingredient(recipe=r3, sort_order=4, amount=Decimal('0.5'), unit='sdt',
                           item_name='Garam'),
            ])
            InstructionStep.objects.bulk_create([
                InstructionStep(recipe=r3, step_number=1,
                                instruction='Ulek kasar cabai rawit merah, bawang putih, dan garam di atas cobek batu. Jangan terlalu halus.'),
                InstructionStep(recipe=r3, step_number=2,
                                instruction='Panaskan minyak sisa menggoreng ayam/bebek sampai benar-benar panas dan mulai berasap.'),
                InstructionStep(recipe=r3, step_number=3,
                                instruction='Siramkan minyak panas mendesis ke atas ulekan sambal. Aduk rata dan sajikan segera.'),
            ])
            self.stdout.write('  🌶️  Sambal Bawang Korek — dibuat')

        # ----------------------------------------------------------------
        # 7. Resep 4: Sayur Asem (Pending, oleh Budi — untuk demo moderasi)
        # ----------------------------------------------------------------
        r4, created = Recipe.objects.get_or_create(
            title='Sayur Asem Bening Segar',
            defaults={
                'author': budi_user,
                'category': cats['Sayur & Sup'],
                'description': (
                    'Sayur asem bening menyegarkan khas Sunda dengan asam jawa muda, '
                    'labu siam, kacang panjang, dan jagung manis. Ringan dan penuh serat.'
                ),
                'default_servings': 4,
                'prep_time_minutes': 15,
                'cook_time_minutes': 20,
                'difficulty': Recipe.Difficulty.MUDAH,
                'status': Recipe.Status.PENDING,
                'is_featured': False,
            }
        )
        if created:
            r4.tags.add(tags['Cepat'], tags['Tanpa Santan'], tags['Keluarga'])
            Ingredient.objects.bulk_create([
                Ingredient(recipe=r4, sort_order=1, amount=Decimal('1'), unit='buah',
                           item_name='Jagung Manis', notes='potong 4 bagian'),
                Ingredient(recipe=r4, sort_order=2, amount=Decimal('1'), unit='buah',
                           item_name='Labu Siam', notes='kupas, potong dadu 3 cm'),
                Ingredient(recipe=r4, sort_order=3, amount=Decimal('5'), unit='batang',
                           item_name='Kacang Panjang', notes='potong 5 cm'),
                Ingredient(recipe=r4, sort_order=4, amount=Decimal('50'), unit='gram',
                           item_name='Kacang Tanah', notes='dengan kulit'),
                Ingredient(recipe=r4, sort_order=5, amount=Decimal('3'), unit='buah',
                           item_name='Asam Jawa', notes='larutkan dengan 2 sdm air'),
                Ingredient(recipe=r4, sort_order=6, amount=Decimal('5'), unit='siung',
                           item_name='Bawang Merah', notes='iris tipis'),
                Ingredient(recipe=r4, sort_order=7, amount=Decimal('3'), unit='siung',
                           item_name='Bawang Putih', notes='iris tipis'),
                Ingredient(recipe=r4, sort_order=8, amount=Decimal('2'), unit='cm',
                           item_name='Lengkuas', notes='memarkan'),
                Ingredient(recipe=r4, sort_order=9, amount=Decimal('2'), unit='lembar',
                           item_name='Daun Salam'),
                Ingredient(recipe=r4, sort_order=10, amount=None, unit=None,
                           item_name='Garam & Gula Merah', notes='secukupnya'),
            ])
            InstructionStep.objects.bulk_create([
                InstructionStep(recipe=r4, step_number=1,
                                instruction='Didihkan 1 liter air. Masukkan bawang merah, bawang putih, lengkuas, daun salam, dan kacang tanah. Rebus 5 menit.'),
                InstructionStep(recipe=r4, step_number=2,
                                instruction='Masukkan jagung manis dan asam jawa cair. Rebus hingga jagung setengah matang.'),
                InstructionStep(recipe=r4, step_number=3,
                                instruction='Masukkan labu siam dan kacang panjang. Bumbui dengan garam dan gula merah secukupnya.'),
                InstructionStep(recipe=r4, step_number=4,
                                instruction='Masak hingga semua sayuran matang namun masih renyah. Koreksi rasa asam-gurih dan sajikan hangat.'),
            ])
            self.stdout.write('  🥬 Sayur Asem Bening — dibuat (status: PENDING untuk demo moderasi)')
