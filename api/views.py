from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hello_world(request):
    return Response({'message': f'Hello, {request.user.username}!'})

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')

    if not username or not password or not password_confirm:
        return Response({'error': 'All fields are required.'}, status=400)

    if password != password_confirm:
        return Response({'error': 'Passwords do not match.'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken.'}, status=400)

    user = User.objects.create_user(username=username, password=password)
    token = Token.objects.create(user=user)

    return Response({'token': token.key}, status=201)

api_login = obtain_auth_token