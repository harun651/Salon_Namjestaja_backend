from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

class NamjestajModelTestCase(TestCase):

    def setUp(self):
        from .models import Namjestaj, Kategorija

        self.test_image = SimpleUploadedFile(name='test.jpg',
                                             content=b'',  
                                             content_type='image/jpeg')

        self.namjestaj = Namjestaj.objects.create(
            naziv="Test Stol",
            kategorija=Kategorija.TRPEZARIJA,
            materijali="Drvo, metal",
            količina_u_skladistu=10,
            opis="Opis stola.",
            slika=self.test_image
        )

    def test_namjestaj_kreiran(self):
        from .models import Namjestaj, Kategorija
        self.assertEqual(Namjestaj.objects.count(), 1)
        namjestaj = Namjestaj.objects.first()
        self.assertEqual(namjestaj.naziv, "Test Stol")
        self.assertEqual(namjestaj.kategorija, "TR")
        self.assertEqual(namjestaj.materijali, "Drvo, metal")
        self.assertEqual(namjestaj.količina_u_skladistu, 10)
        self.assertEqual(namjestaj.opis, "Opis stola.")
        self.assertTrue(namjestaj.slika.name.startswith("namjestaj/test"))
        self.assertFalse(namjestaj.izbrisano)

    def test_namjestaj_str_method(self):
        from .models import Namjestaj, Kategorija
        self.assertEqual(str(self.namjestaj), "Test Stol")

    def test_namjestaj_kategorija_choices(self):
        from .models import Namjestaj, Kategorija
        self.assertIn(self.namjestaj.kategorija, dict(Kategorija.choices).keys())


class PorukaModelTestCase(TestCase):

    def setUp(self):
        from .models import Poruka

        self.posiljalac = User.objects.create_user(username='posiljalac', password='testpass')
        self.primalac = User.objects.create_user(username='primalac', password='testpass')

        self.poruka = Poruka.objects.create(
            posiljalac=self.posiljalac,
            primalac=self.primalac,
            tekst='Test poruka',
            procitana=False
        )

    def test_poruka_kreirana(self):
        from .models import Poruka
        self.assertEqual(Poruka.objects.count(), 1)
        poruka = Poruka.objects.first()
        self.assertEqual(poruka.posiljalac, self.posiljalac)
        self.assertEqual(poruka.primalac, self.primalac)
        self.assertEqual(poruka.tekst, 'Test poruka')
        self.assertFalse(poruka.procitana)

    def test_poruka_timestamp(self):
        from .models import Poruka
        poruka = Poruka.objects.first()
        self.assertIsNotNone(poruka.timestamp)

    def test_poruka_procitana(self):
        from .models import Poruka
        self.poruka.procitana = True
        self.poruka.save()
        self.poruka.refresh_from_db()
        self.assertTrue(self.poruka.procitana)

    def test_poruka_ordering(self):
        from .models import Poruka
        poruka2 = Poruka.objects.create(
            posiljalac=self.posiljalac,
            primalac=self.primalac,
            tekst='Test poruka 2',
            procitana=True
        )

        poruke = Poruka.objects.all()
        self.assertEqual(poruke[0].timestamp.replace(microsecond=0), self.poruka.timestamp.replace(microsecond=0))
        self.assertEqual(poruke[1].timestamp.replace(microsecond=0), poruka2.timestamp.replace(microsecond=0))


class NamjestajAPITestCase(TestCase):

    def setUp(self):
        from .models import Namjestaj

        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.token = Token.objects.create(user=self.admin_user)

        self.namjestaj = Namjestaj.objects.create(
            naziv="Test Stol",
            kategorija="TR",
            materijali="Drvo, metal",
            količina_u_skladistu=10,
            opis="Opis stola",
            slika=None
        )

        self.url = reverse('namjestaj-list')

    def test_get_namjestaj(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['naziv'], "Test Stol")
   
    def test_delete_namjestaj(self):
        from .models import Namjestaj
        url = reverse('namjestaj-detail', kwargs={'pk': self.namjestaj.pk})
        response = self.client.delete(
            url,
            HTTP_AUTHORIZATION=f'Token {self.token.key}'  
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Namjestaj.objects.count(), 0)
