from rest_framework import serializers
from .models import Namjestaj, Poruka
from django.contrib.auth.models import User

class NamjestajSerializer(serializers.ModelSerializer):
    kategorija_display = serializers.CharField(source='get_kategorija_display', read_only=True)
    slika = serializers.ImageField(use_url=True)

    class Meta:
        model = Namjestaj
        fields = ['id', 'naziv', 'slika', 'kategorija', 'kategorija_display',
            'materijali', 'opis', 'količina_u_skladistu']


class PorukaSerializer(serializers.ModelSerializer):
    posiljalac_username = serializers.ReadOnlyField(source='posiljalac.username')
    primalac_username = serializers.ReadOnlyField(source='primalac.username')

    class Meta:
        model = Poruka
        fields = ['id', 'posiljalac', 'posiljalac_username', 'primalac', 'primalac_username', 'tekst', 'timestamp', 'procitana']
        read_only_fields = ['posiljalac', 'timestamp', 'procitana']
