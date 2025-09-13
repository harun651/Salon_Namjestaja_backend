from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings

@api_view(['POST'])
@permission_classes([AllowAny])
def registruj_korisnika(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    password2 = data.get('password2')
    email = data.get('email')

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
    user.save()
    return Response({"detail": "Korisnik uspješno registrovan."}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trenutni_korisnik(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_korisnika(request):
    users = User.objects.all()
    data = [{"id": user.id, "username": user.username} for user in users]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_korisnik(request):
    admin_user = User.objects.filter(username=settings.CHAT_ADMIN_USERNAME).first()
    if not admin_user:
        return Response({'detail': 'Nema dostupnog admin korisnika.'}, status=404)
    return Response({'id': admin_user.id, 'username': admin_user.username})