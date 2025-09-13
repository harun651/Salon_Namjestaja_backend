from django.db import models
from django.contrib.auth.models import User


class Kategorija(models.TextChoices):
    DNEVNI_BORAVAK = 'DB', 'Dnevni boravak'
    SPAVACA_SOBA = 'SS', 'Spavaća soba'
    KUHINJA = 'KU', 'Kuhinja'
    DJECIJA_SOBA = 'DS', 'Dječija soba'
    TRPEZARIJA = 'TR', 'Trpezarija'
    HODNIK = 'HO', 'Hodnik'


class Namjestaj(models.Model):
    naziv = models.CharField(max_length=100)
    kategorija = models.CharField(max_length=2, choices=Kategorija.choices)
    materijali = models.CharField(max_length=200)
    količina_u_skladistu = models.PositiveIntegerField()
    opis = models.TextField()
    slika = models.ImageField(upload_to='namjestaj/')
    dodano_vrijeme = models.DateTimeField(auto_now_add=True)
    izbrisano = models.BooleanField(default=False)

    def __str__(self):
        return self.naziv


class Poruka(models.Model):
    posiljalac = models.ForeignKey(User, related_name='poslate_poruke', on_delete=models.CASCADE)
    primalac = models.ForeignKey(User, related_name='primljene_poruke', on_delete=models.CASCADE)
    tekst = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    procitana = models.BooleanField(default=False)


    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Poruka od {self.posiljalac.username} do {self.primalac.username} u {self.timestamp}'


