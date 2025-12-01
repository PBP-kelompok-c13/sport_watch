import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils.html import strip_tags
import requests


def _extract_request_data(request):
    """
    Support both JSON payloads (Flutter register) and form-encoded payloads
    (pbp_django_auth login). Falls back to {} when no payload is provided.
    """
    content_type = (request.headers.get('Content-Type') or '').lower()
    body = request.body or b''

    if 'application/json' in content_type:
        try:
            return json.loads(body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return {}

    if request.POST:
        return request.POST.dict()

    if not body:
        return {}

    try:
        return json.loads(body.decode('utf-8'))
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_POST
def login_user(request):
    try:
        data = _extract_request_data(request)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                "status": False,
                "message": "Username and password are required."
            }, status=400)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return JsonResponse({
                    "username": user.username,
                    "status": True,
                    "message": "Login successful!",
                    "id": user.id,  # TAMBAHAN BARU KALAU ADA ERROR COBA LIHAT INI TAPI GAK MUNGKIN SI
                }, status=200)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Account is disabled."
                }, status=401)
        else:
            return JsonResponse({
                "status": False,
                "message": "Invalid username or password."
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"status": False, "message": str(e)}, status=500)

@csrf_exempt
@require_POST
def register_user(request):
    try:
        data = _extract_request_data(request)
        username = data.get('username')
        password = data.get('password')
        password_confirm = data.get('password_confirm')  # Standardized naming

        if not username or not password or not password_confirm:
            return JsonResponse({
                "status": False,
                "message": "All fields are required."
            }, status=400)

        if password != password_confirm:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already taken."
            }, status=400)

        user = User.objects.create_user(username=username, password=password)
        user.save()

        return JsonResponse({
            "status": True,
            "message": "User created successfully!",
            "username": user.username
        }, status=201)

    except Exception as e:
        return JsonResponse({"status": False, "message": str(e)}, status=500)
    
@csrf_exempt
@require_POST
def logout_user(request):
    username = getattr(request.user, "username", None)
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except Exception:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)


from urllib.parse import urlparse

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)

    # Kalau yang datang cuma "/media/..." → jadikan absolute URL
    parsed = urlparse(image_url)
    if not parsed.scheme:  # tidak ada http/https
        image_url = request.build_absolute_uri(image_url)

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg'),
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)


@login_required
@require_GET
def profile(request):
    user = request.user
    return JsonResponse(
        {
            "username": user.username,
            "email": user.email or "",
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        },
        status=200,
    )
