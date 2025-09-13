from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.conf import settings
from .models import Namjestaj, Poruka
from .serializers import NamjestajSerializer, PorukaSerializer
from .permissions import IsStaffOrReadOnly


ADMIN_USERNAME = getattr(settings, "CHAT_ADMIN_USERNAME", "admin")


class NamjestajViewSet(viewsets.ModelViewSet):
    queryset = Namjestaj.objects.filter(izbrisano=False).order_by("-dodano_vrijeme")
    serializer_class = NamjestajSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsStaffOrReadOnly]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)



@api_view(["POST"])
@permission_classes([AllowAny])
def registruj_korisnika(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    password2 = data.get("password2")
    email = data.get("email")

    if not username or not password or not password2 or not email:
        return Response({"detail": "Sva polja su obavezna."}, status=status.HTTP_400_BAD_REQUEST)

    if password != password2:
        return Response({"detail": "Šifre se ne podudaraju."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"detail": "Korisničko ime je već zauzeto."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {
            "detail": "Korisnik uspješno registrovan.",
            "token": token.key,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def najnoviji_namjestaj(request):
    najnoviji_items = Namjestaj.objects.filter(izbrisano=False).order_by("-dodano_vrijeme")[:6]
    serializer = NamjestajSerializer(najnoviji_items, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trenutni_korisnik(request):
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lista_korisnika(request):
    users = User.objects.all()
    data = [{"id": u.id, "username": u.username} for u in users]
    return Response(data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_korisnik(request):
    admin_user = User.objects.filter(username=ADMIN_USERNAME).first()
    if not admin_user:
        return Response({"detail": "Nema dostupnog admin korisnika."}, status=404)
    return Response({"id": admin_user.id, "username": admin_user.username})



class PorukaViewSet(viewsets.ModelViewSet):
    serializer_class = PorukaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        target_user_id = self.request.query_params.get("user_id")

        if user.is_staff:
           
            if target_user_id:
                try:
                    target_user_id = int(target_user_id)
                except (ValueError, TypeError):
                    return Poruka.objects.none()

                return Poruka.objects.filter(
                    (Q(posiljalac__id=target_user_id) & Q(primalac=user)) |
                    (Q(primalac__id=target_user_id) & Q(posiljalac=user))
                ).order_by("timestamp")

          
            return Poruka.objects.none()

        else:
           
            admin_user = User.objects.filter(username=ADMIN_USERNAME).first()
            if not admin_user:
                return Poruka.objects.none()

            return Poruka.objects.filter(
                (Q(posiljalac=user) & Q(primalac=admin_user)) |
                (Q(primalac=user) & Q(posiljalac=admin_user))
            ).order_by("timestamp")

    def perform_create(self, serializer):
        posiljalac = self.request.user
        primalac = serializer.validated_data["primalac"]

        if not posiljalac.is_staff and not primalac.is_staff:
            raise ValidationError("Obični korisnici mogu slati poruke samo adminima.")

        serializer.save(posiljalac=posiljalac)

    @action(detail=True, methods=["post"])
    def oznaci_procitano(self, request, pk=None):
        poruka = self.get_object()

        if poruka.primalac != request.user:
            return Response({"detail": "Nemate pravo da označite ovu poruku."}, status=status.HTTP_403_FORBIDDEN)

        poruka.procitana = True
        poruka.save()
        return Response({"detail": "Poruka označena kao pročitana."})
