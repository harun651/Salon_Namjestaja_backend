from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NamjestajViewSet, PorukaViewSet
from .views import registruj_korisnika, trenutni_korisnik, lista_korisnika, admin_korisnik, najnoviji_namjestaj

router = DefaultRouter()
router.register(r"namjestaj", NamjestajViewSet)
router.register(r"poruke", PorukaViewSet, basename="poruke")

urlpatterns = [
    path("", include(router.urls)),
    path("registracija/", registruj_korisnika, name="registracija"),
    path("current-user/", trenutni_korisnik, name="trenutni_korisnik"),
    path("najnoviji/", najnoviji_namjestaj, name="najnoviji_namjestaj"),
    path("users/", lista_korisnika, name="lista_korisnika"),
    path("admin-korisnik/", admin_korisnik, name="admin_korisnik"),
]
