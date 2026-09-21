import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from recipes.models import Category, Tag, Recipe, Ingredient, InstructionStep, RecipeNutrition

User = get_user_model()

def reset_and_seed_10_recipes():
    print("1. Menghapus resep lama...")
    Recipe.objects.all().delete()
    print("Resep lama berhasil dibersihkan.")

    # Ambil / buat user admin & pengguna
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@dapurnusa.id', 'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True}
    )
    budi_user, _ = User.objects.get_or_create(
        username='budi_santoso',
        defaults={'email': 'budi@example.com', 'role': User.Role.PENGGUNA}
    )

    # Kategori
    categories_data = [
        ('Daging Sapi', 'soup_kitchen', 'Aneka masakan daging sapi empuk khas tradisi nusantara'),
        ('Ayam & Bebek', 'restaurant', 'Olahan ayam dan unggas dengan bumbu rempah melimpah'),
        ('Ikan & Seafood', 'set_meal', 'Sajian boga bahari berlimpah rempah nusantara'),
        ('Sayur & Sup', 'local_florist', 'Hidangan sayur mayur segar penyejuk selera'),
        ('Nasi & Mi', 'dinner_dining', 'Olahan karbohidrat istimewa kaya bumbu'),
        ('Sambal & Cocolan', 'local_fire_department', 'Pedas nikmat menggigit pelengkap santap'),
    ]
    cats = {}
    for name, icon, desc in categories_data:
        c, _ = Category.objects.get_or_create(name=name, defaults={'icon_name': icon, 'description': desc})
        cats[name] = c

    # Tags
    tag_names = ['Tradisional', 'Pedas', 'Cepat', 'Tanpa Santan', 'Menu Lebaran', 'Keluarga', 'Favorit']
    tags = {}
    for tname in tag_names:
        t, _ = Tag.objects.get_or_create(name=tname)
        tags[tname] = t

    recipes_dataset = [
        # 1. Rendang Daging Sapi Padang
        {
            'title': 'Rendang Daging Sapi Padang Asli',
            'author': admin_user,
            'category': cats['Daging Sapi'],
            'tags': [tags['Tradisional'], tags['Menu Lebaran'], tags['Favorit']],
            'description': 'Resep rendang Minang otentik bersantan pekat dengan rempah kelapa sangrai berjam-jam hingga hitam kecokelatan, meresap sampai ke serat daging.',
            'default_servings': 6,
            'prep_time_minutes': 30,
            'cook_time_minutes': 180,
            'difficulty': Recipe.Difficulty.SULIT,
            'is_featured': True,
            'ingredients': [
                (1000, 'gram', 'Daging Sapi Gandik / Sengkel', 'potong searah serat'),
                (1500, 'ml', 'Santan Kental', 'dari 3 butir kelapa tua parut'),
                (500, 'ml', 'Santan Encer', 'perasan kedua'),
                (4, 'batang', 'Serai', 'memarkan'),
                (6, 'lembar', 'Daun Jeruk Purut', 'buang tulang daun'),
                (2, 'lembar', 'Daun Kunyit', 'ikat simpul'),
                (3, 'buah', 'Asam Kandis', None),
                (150, 'gram', 'Cabai Merah Keriting', 'haluskan'),
                (12, 'siung', 'Bawang Merah', 'haluskan'),
                (6, 'siung', 'Bawang Putih', 'haluskan'),
                (4, 'cm', 'Lengkuas & Jahe', 'haluskan'),
                (1, 'sdm', 'Garam', 'sesuaikan selera')
            ],
            'steps': [
                'Haluskan cabai merah, bawang merah, bawang putih, jahe, lengkuas, dan ketumbar hingga lembut.',
                'Didihkan santan kental dan santan encer bersama bumbu halus, serai, daun jeruk, dan daun kunyit dengan api sedang sambil ditimba perlahan agar tidak pecah santan.',
                'Setelah kuah mengeluarkan minyak kemerahan (tahap gulai), masukkan potongan daging sapi.',
                'Kecilkan api, aduk berkala sampai air menyusut pekat dan berwarna cokelat gelap (tahap kalio).',
                'Masak terus dengan api sangat kecil sambil diaduk perlahan hingga bumbu mengering hitam mengkilap dan meresap sempurna.'
            ],
            'nutrition': (480, 36.0, 9.0, 34.0)
        },

        # 2. Rawon Daging Sapi Khas Surabaya
        {
            'title': 'Rawon Daging Sapi Khas Surabaya',
            'author': admin_user,
            'category': cats['Daging Sapi'],
            'tags': [tags['Tradisional'], tags['Keluarga']],
            'description': 'Sup daging sapi kuah hitam pekat khas Jawa Timur dengan aroma kluwek gurih yang kaya rasa, disajikan hangat bersama tauge pendek dan telur asin.',
            'default_servings': 5,
            'prep_time_minutes': 25,
            'cook_time_minutes': 60,
            'difficulty': Recipe.Difficulty.SEDANG,
            'is_featured': True,
            'ingredients': [
                (500, 'gram', 'Daging Sapi Sandung Lamur (Brisket)', 'potong dadu 2 cm'),
                (2000, 'ml', 'Air Bersih', 'untuk kuah kaldu'),
                (5, 'buah', 'Kluwek Tua', 'ambil isinya, rendam air hangat lalu haluskan'),
                (8, 'siung', 'Bawang Merah', 'haluskan'),
                (5, 'siung', 'Bawang Putih', 'haluskan'),
                (3, 'butir', 'Kemiri Sangrai', 'haluskan'),
                (3, 'batang', 'Serai', 'memarkan'),
                (4, 'lembar', 'Daun Jeruk Purut', 'sobek'),
                (2, 'batang', 'Daun Bawang', 'iris kasar'),
                (100, 'gram', 'Tauge Pendek', 'pelengkap segar'),
                (3, 'butir', 'Telur Asin', 'rebus belah dua')
            ],
            'steps': [
                'Rebus daging sandung lamur dalam 2 liter air hingga empuk. Saring air rebusan untuk dijadikan kaldu bening gurih.',
                'Tumis bumbu halus bersama kluwek, serai, daun jeruk, dan lengkuas sampai benar-benar matang dan harum.',
                'Tuangkan tumisan bumbu ke dalam panci kuah kaldu daging. Bumbui dengan garam, gula pasir, dan merica.',
                'Masak dengan api kecil hingga bumbu meresap ke dalam serat daging dan kuah berwarna hitam pekat mengilap.',
                'Sajikan selagi panas dengan taburan daun bawang, bawang goreng, tauge pendek mentah, dan telur asin.'
            ],
            'nutrition': (360, 29.5, 12.0, 21.0)
        },

        # 3. Ayam Betutu Khas Gilimanuk Bali
        {
            'title': 'Ayam Betutu Khas Gilimanuk Bali',
            'author': admin_user,
            'category': cats['Ayam & Bebek'],
            'tags': [tags['Tradisional'], tags['Pedas']],
            'description': 'Ayam utuh berbumbu Base Genep khas Bali yang kaya rempah kencur, jahe, kunyit, dan cabai rawit, dimasak perlahan hingga daging empuk merotol.',
            'default_servings': 4,
            'prep_time_minutes': 30,
            'cook_time_minutes': 75,
            'difficulty': Recipe.Difficulty.SEDANG,
            'is_featured': True,
            'ingredients': [
                (1, 'ekor', 'Ayam Kampung Utuh', 'bersihkan belah tengah tidak putus'),
                (12, 'siung', 'Bawang Merah', 'cincang kasar'),
                (7, 'siung', 'Bawang Putih', 'cincang kasar'),
                (15, 'buah', 'Cabai Rawit Merah', 'rajang halus'),
                (4, 'cm', 'Kencur', 'haluskan'),
                (4, 'cm', 'Kunyit Bakar', 'haluskan'),
                (3, 'cm', 'Lengkuas', 'haluskan'),
                (3, 'batang', 'Serai', 'iris halus bagian putih'),
                (1, 'sdm', 'Terasi Bakar', 'haluskan'),
                (50, 'ml', 'Minyak Kelapa Asli', 'untuk menumis'),
                (600, 'ml', 'Air Kaldu', None)
            ],
            'steps': [
                'Campur bumbu rajangan dan bumbu halus Base Genep dengan minyak kelapa dan garam hingga merata.',
                'Lumuri seluruh permukaan dan rongga ayam dengan separuh racikan bumbu, remas-remas agar meresap.',
                'Tumis sisa bumbu di wajan hingga harum, masukkan ayam dan tuang air secara bertahap.',
                'Ungkep ayam dengan api kecil sambil panci ditutup rapat selama kurang lebih 60-75 menit hingga air mengental dan daging empuk.',
                'Sajikan bersama siraman kuah pedas betutu, plecing kangkung, dan kacang tanah goreng renyah.'
            ],
            'nutrition': (410, 38.0, 6.5, 26.0)
        },

        # 4. Soto Ayam Lamongan Kuah Gurih Koya
        {
            'title': 'Soto Ayam Lamongan Kuah Gurih Koya',
            'author': budi_user,
            'category': cats['Ayam & Bebek'],
            'tags': [tags['Tradisional'], tags['Keluarga']],
            'description': 'Soto ayam berkuah kuning bening gurih kaldu asli dengan pelengkap taburan koya kerupuk udang renyah dan sambal rawit rebus.',
            'default_servings': 4,
            'prep_time_minutes': 25,
            'cook_time_minutes': 45,
            'difficulty': Recipe.Difficulty.MUDAH,
            'is_featured': True,
            'ingredients': [
                (500, 'gram', 'Ayam Kampung', 'cuci bersih'),
                (1800, 'ml', 'Air Kaldu', 'air rebusan ayam'),
                (8, 'siung', 'Bawang Merah', 'haluskan'),
                (5, 'siung', 'Bawang Putih', 'haluskan'),
                (4, 'butir', 'Kemiri Sangrai', 'haluskan'),
                (3, 'cm', 'Kunyit Bakar', 'haluskan'),
                (2, 'cm', 'Jahe', 'memarkan'),
                (3, 'batang', 'Serai & Daun Jeruk', 'memarkan'),
                (100, 'gram', 'Soun Kering', 'seduh air hangat tiriskan'),
                (100, 'gram', 'Kol Putih', 'iris tipis'),
                (4, 'sdm', 'Bubuk Koya Udang', 'kerupuk udang + bawang putih goreng dihaluskan')
            ],
            'steps': [
                'Rebus ayam kampung dalam 1800 ml air dengan api sedang hingga mengeluarkan kaldu bening dan matang.',
                'Angkat ayam, goreng sebentar dalam minyak panas hingga berkulit, lalu suwir-suwir dagingnya.',
                'Tumis bumbu halus bersama serai, daun jeruk, dan daun salam sampai harum kekuningan.',
                'Masukkan tumisan bumbu ke dalam kuah kaldu mendidih. Bumbui garam, gula, dan merica sesuai selera.',
                'Tata soun, kol, dan suwiran ayam di mangkuk. Siram kuah soto panas dan taburi bubuk koya melimpah.'
            ],
            'nutrition': (315, 27.5, 24.0, 11.5)
        },

        # 5. Ikan Bakar Bumbu Jimbaran Bali
        {
            'title': 'Ikan Bakar Bumbu Jimbaran Asli Bali',
            'author': admin_user,
            'category': cats['Ikan & Seafood'],
            'tags': [tags['Tradisional'], tags['Keluarga']],
            'description': 'Ikan laut bakar dengan olesan saus manis pedas gurih khas pantai Jimbaran yang berkaramel harum saat dipanggang di atas arang.',
            'default_servings': 4,
            'prep_time_minutes': 20,
            'cook_time_minutes': 25,
            'difficulty': Recipe.Difficulty.SEDANG,
            'is_featured': False,
            'ingredients': [
                (2, 'ekor', 'Ikan Kakap Merah / Gurame (800g)', 'belah punggung bentuk kupu-kupu'),
                (8, 'siung', 'Bawang Merah', 'haluskan'),
                (5, 'siung', 'Bawang Putih', 'haluskan'),
                (6, 'buah', 'Cabai Merah Keriting', 'haluskan'),
                (1, 'buah', 'Tomat Merah Segar', 'haluskan'),
                (3, 'sdm', 'Kecap Manis', None),
                (2, 'sdm', 'Saus Tiram', None),
                (1, 'sdm', 'Gula Merah Sisir', None),
                (2, 'sdm', 'Margarin Leleh', 'untuk olesan'),
                (1, 'buah', 'Jeruk Nipis', 'untuk perasan ikan')
            ],
            'steps': [
                'Lumuri ikan kakap dengan air jeruk nipis dan garam, diamkan selama 10 menit agar tidak amis.',
                'Tumis bumbu halus dengan margarin hingga harum dan tidak berbau langu.',
                'Masukkan kecap manis, saus tiram, saus tomat, garam, dan gula merah. Aduk rata hingga saus olesan mengental.',
                'Panggang ikan di atas bara api / panggangan anti-lengket hingga setengah matang.',
                'Olesi bumbu Jimbaran tebal-tebal pada kedua sisi ikan, bakar bolak-balik sampai matang terkaramelisasi dan wangi.'
            ],
            'nutrition': (290, 32.0, 14.0, 11.0)
        },

        # 6. Pempek Palembang Kapal Selam Lembut
        {
            'title': 'Pempek Palembang Kapal Selam Lembut',
            'author': admin_user,
            'category': cats['Ikan & Seafood'],
            'tags': [tags['Tradisional'], tags['Favorit']],
            'description': 'Pempek khas Palembang dari daging ikan tenggiri murni dengan isian telur utuh yang kenyal gurih, disajikan dengan kuah cuko kental pedas asam.',
            'default_servings': 4,
            'prep_time_minutes': 40,
            'cook_time_minutes': 30,
            'difficulty': Recipe.Difficulty.SULIT,
            'is_featured': False,
            'ingredients': [
                (500, 'gram', 'Ikan Tenggiri Giling Dingin', 'kualitas segar'),
                (350, 'gram', 'Tepung Tapioka / Sagu Tani', None),
                (250, 'ml', 'Air Es Dingin', None),
                (4, 'butir', 'Kuning / Telur Ayam Utuh', 'untuk isian kapal selam'),
                (1, 'sdm', 'Garam Halus', None),
                (1, 'sdt', 'Gula Pasir & Kaldu Jamur', None),
                (250, 'gram', 'Gula Batok Linggau Hitam', 'untuk cuko'),
                (50, 'gram', 'Cabai Rawit Hijau & Bawang Putih', 'untuk cuko'),
                (2, 'sdm', 'Asam Jawa Pekat', 'untuk cuko')
            ],
            'steps': [
                'Uleni daging tenggiri dingin dengan air es hingga lengket dan lembut seperti pasta.',
                'Tambahkan garam, aduk hingga adonan mengental kencang, lalu masukkan tepung tapioka bertahap tanpa diuleni terlalu kuat agar tidak keras.',
                'Ambil adonan 100 gram, bentuk mangkuk lonjong berkantong, masukkan sebutir telur, lalu rapatkan ujung adonan dengan rapat.',
                'Rebus pempek dalam air mendidih banyak dengan api sedang sampai terapung dan matang hingga ke dalam (kurang lebih 20 menit).',
                'Goreng pempek hingga renyah keemasan, potong-potong, lalu siram dengan kuah cuko kental pedas asam.'
            ],
            'nutrition': (380, 24.0, 48.0, 10.5)
        },

        # 7. Sayur Asem Bening Segar Khas Jawa Barat
        {
            'title': 'Sayur Asem Bening Segar Khas Sunda',
            'author': budi_user,
            'category': cats['Sayur & Sup'],
            'tags': [tags['Tanpa Santan'], tags['Cepat'], tags['Keluarga']],
            'description': 'Sayur kuah bening asam manis gurih dengan aneka sayuran segar seperti jagung manis, melinjo, labu siam, dan kacang panjang yang menyegarkan.',
            'default_servings': 5,
            'prep_time_minutes': 15,
            'cook_time_minutes': 20,
            'difficulty': Recipe.Difficulty.MUDAH,
            'is_featured': False,
            'ingredients': [
                (1, 'buah', 'Jagung Manis', 'potong bulat 3 cm'),
                (1, 'buah', 'Labu Siam Sedang', 'kupas, potong dadu'),
                (5, 'lonjor', 'Kacang Panjang', 'potong 4 cm'),
                (50, 'gram', 'Daun & Buah Melinjo', 'cuci bersih'),
                (50, 'gram', 'Kacang Tanah Kupas', None),
                (3, 'buah', 'Asam Jawa Segar / Muda', 'memarkan'),
                (3, 'cm', 'Lengkuas', 'memarkan'),
                (3, 'lembar', 'Daun Salam', None),
                (6, 'butir', 'Bawang Merah & 3 Bawang Putih', 'haluskan / iris'),
                (3, 'buah', 'Cabai Merah Keriting', 'iris serong'),
                (1.5, 'sdm', 'Gula Merah & Garam', 'sesuaikan selera')
            ],
            'steps': [
                'Didihkan 1500 ml air bersih bersama asam jawa muda, lengkuas, daun salam, dan bumbu halus.',
                'Masukkan bahan keras terlebih dahulu: kacang tanah, jagung manis, dan buah melinjo hingga setengah empuk.',
                'Keluarkan buah asam jawa, lumatkan dengan sedikit air kuah lalu saring kembali ke dalam panci.',
                'Masukkan labu siam, kacang panjang, dan daun melinjo.',
                'Bumbui dengan garam dan gula merah hingga tercapai paduan rasa asam, manis, dan gurih yang seimbang. Sajikan hangat.'
            ],
            'nutrition': (120, 4.5, 22.0, 2.0)
        },

        # 8. Nasi Goreng Kampung Tradisional
        {
            'title': 'Nasi Goreng Kampung Terasi Tradisional',
            'author': budi_user,
            'category': cats['Nasi & Mi'],
            'tags': [tags['Tradisional'], tags['Cepat'], tags['Keluarga']],
            'description': 'Nasi goreng autentik rumahan tanpa saus instan, mengandalkan harum terasi bakar, cabai rawit, telur orak-arik, dan suwiran ayam gurih.',
            'default_servings': 3,
            'prep_time_minutes': 10,
            'cook_time_minutes': 15,
            'difficulty': Recipe.Difficulty.MUDAH,
            'is_featured': False,
            'ingredients': [
                (500, 'gram', 'Nasi Putih Dingin (Pera)', 'nasi sisa kemarin lebih bagus'),
                (2, 'butir', 'Telur Ayam', 'kocok lepas'),
                (100, 'gram', 'Daging Ayam Suwir', 'rebus matang'),
                (6, 'siung', 'Bawang Merah', 'haluskan'),
                (3, 'siung', 'Bawang Putih', 'haluskan'),
                (8, 'buah', 'Cabai Rawit Merah', 'haluskan kasar'),
                (1, 'sdt', 'Terasi Bakar Matang', 'haluskan'),
                (2, 'batang', 'Daun Bawang', 'iris halus'),
                (1, 'sdm', 'Kecap Asin / Ikan', None),
                (3, 'sdm', 'Minyak Goreng', 'untuk menumis')
            ],
            'steps': [
                'Panaskan wajan dengan minyak, orak-arik telur hingga matang berbutir, sisihkan di tepi wajan.',
                'Tumis bumbu halus bersama terasi bakar hingga harum kering dan tidak langu.',
                'Masukkan nasi putih dingin dan suwiran ayam, aduk cepat dengan api besar hingga bumbu merata ke setiap bulir nasi.',
                'Tambahkan kecap asin, garam, kaldu bubuk, dan irisan daun bawang.',
                'Aduk terus dengan teknik wok tossing (api besar) selama 3 menit hingga nasi beraroma wangi terbakar gurih. Angkat dan sajikan.'
            ],
            'nutrition': (390, 16.5, 54.0, 12.0)
        },

        # 9. Gulai Tunjang Khas Rumah Makan Padang
        {
            'title': 'Gulai Tunjang Khas Rumah Makan Padang',
            'author': admin_user,
            'category': cats['Daging Sapi'],
            'tags': [tags['Tradisional'], tags['Pedas']],
            'description': 'Kikil sapi bagian tunjang yang kenyal lembut berpadu kuah gulai kental kuning kemerahan kaya rempah kapulaga, cengkeh, dan serai.',
            'default_servings': 4,
            'prep_time_minutes': 25,
            'cook_time_minutes': 90,
            'difficulty': Recipe.Difficulty.SEDANG,
            'is_featured': False,
            'ingredients': [
                (700, 'gram', 'Kikil Tunjang Sapi Rebus', 'potong kotak 4x4 cm'),
                (1000, 'ml', 'Santan Sedang', 'dari 1,5 butir kelapa'),
                (10, 'buah', 'Cabai Merah Keriting', 'haluskan'),
                (8, 'siung', 'Bawang Merah', 'haluskan'),
                (4, 'siung', 'Bawang Putih', 'haluskan'),
                (3, 'cm', 'Kunyit & Jahe', 'haluskan'),
                (4, 'cm', 'Lengkuas', 'memarkan'),
                (2, 'batang', 'Serai', 'memarkan'),
                (4, 'lembar', 'Daun Jeruk Purut', None),
                (2, 'butir', 'Kapulaga & 3 Cengkeh', None),
                (1, 'keping', 'Asam Kandis', None)
            ],
            'steps': [
                'Rebus potongan tunjang sapi dalam air mendidih berisi jahe dan daun salam hingga kenyal empuk, buang air rebusan pertamanya.',
                'Didihkan santan bersama bumbu halus gulai, lengkuas, serai, daun jeruk, kapulaga, dan cengkeh.',
                'Aduk santan perlahan secara konstan agar santan tidak pecah hingga mengeluarkan aroma rempah dan minyak alami.',
                'Masukkan tunjang sapi dan asam kandis. Masak dengan api kecil hingga bumbu meresap ke dalam pori-pori kikil.',
                'Bumbui dengan garam dan sedikit gula. Angkat saat kuah gulai mengental keemasan.'
            ],
            'nutrition': (420, 22.0, 8.0, 33.5)
        },

        # 10. Sambal Terasi Ulek Matang Khas Sunda
        {
            'title': 'Sambal Terasi Ulek Matang Khas Sunda',
            'author': budi_user,
            'category': cats['Sambal & Cocolan'],
            'tags': [tags['Pedas'], tags['Cepat'], tags['Tanpa Santan']],
            'description': 'Sambal terasi goreng ulek tangan dengan tomat ceri segar, cabai rawit pedas, dan gula aren legit yang menyempurnakan lalapan dan ikan bakar.',
            'default_servings': 4,
            'prep_time_minutes': 8,
            'cook_time_minutes': 10,
            'difficulty': Recipe.Difficulty.MUDAH,
            'is_featured': False,
            'ingredients': [
                (15, 'buah', 'Cabai Rawit Merah', 'kerat sedikit agar tidak meletup'),
                (10, 'buah', 'Cabai Merah Keriting', 'potong kasar'),
                (6, 'siung', 'Bawang Merah', 'kupas'),
                (2, 'siung', 'Bawang Putih', 'kupas'),
                (2, 'buah', 'Tomat Merah Sedang', 'potong-potong'),
                (1.5, 'sdt', 'Terasi Udang Matang', 'bakar / goreng'),
                (1.5, 'sdm', 'Gula Aren Sisir', None),
                (1, 'sdt', 'Garam Halus', None),
                (1, 'buah', 'Jeruk Limau Segar', 'belah dua'),
                (4, 'sdm', 'Minyak Goreng', 'untuk menggoreng bahan')
            ],
            'steps': [
                'Panaskan minyak di wajan, goreng cabai merah, cabai rawit, bawang merah, bawang putih, dan potongan tomat sampai layu beraroma.',
                'Angkat semua bahan dan letakkan langsung di atas cobek batu.',
                'Tambahkan terasi bakar, gula aren, dan garam halus.',
                'Ulek semua bahan hingga tingkat kehalusan yang diinginkan (ulek kasar berserat lebih nikmat).',
                'Kucuri perasan jeruk limau segar di atas sambal, aduk rata dengan sendok. Siap dicocol dengan lalapan dan lauk favorit.'
            ],
            'nutrition': (95, 1.4, 7.5, 7.0)
        }
    ]

    print(f"2. Memasukkan {len(recipes_dataset)} resep nusantara akurat...")
    for idx, r_data in enumerate(recipes_dataset, start=1):
        recipe = Recipe.objects.create(
            title=r_data['title'],
            author=r_data['author'],
            category=r_data['category'],
            description=r_data['description'],
            default_servings=r_data['default_servings'],
            prep_time_minutes=r_data['prep_time_minutes'],
            cook_time_minutes=r_data['cook_time_minutes'],
            difficulty=r_data['difficulty'],
            status=Recipe.Status.PUBLISHED,
            is_featured=r_data.get('is_featured', False)
        )

        # Tags
        if r_data.get('tags'):
            recipe.tags.set(r_data['tags'])

        # Ingredients
        ing_objects = []
        for s_idx, ing in enumerate(r_data['ingredients'], start=1):
            amount, unit, name, notes = ing
            ing_objects.append(Ingredient(
                recipe=recipe,
                sort_order=s_idx,
                amount=amount,
                unit=unit,
                item_name=name,
                notes=notes
            ))
        Ingredient.objects.bulk_create(ing_objects)

        # Steps
        step_objects = []
        for st_idx, step_text in enumerate(r_data['steps'], start=1):
            step_objects.append(InstructionStep(
                recipe=recipe,
                step_number=st_idx,
                instruction=step_text
            ))
        InstructionStep.objects.bulk_create(step_objects)

        # Nutrition
        cal, prot, carbs, fat = r_data['nutrition']
        RecipeNutrition.objects.create(
            recipe=recipe,
            calories=cal,
            protein_grams=prot,
            carbs_grams=carbs,
            fat_grams=fat
        )

        print(f"   [{idx}/10] Berhasil menambahkan: {recipe.title}")

    print("\n✅ SELESAI! 10 Resep Nusantara Otentik & Akurat telah aktif di database Dapur Nusa.")

if __name__ == '__main__':
    reset_and_seed_10_recipes()
