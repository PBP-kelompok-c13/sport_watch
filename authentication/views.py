import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
import json
import requests


@csrf_exempt
@require_POST
def login_user(request):
    try:
        data = json.loads(request.body)
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
                    "message": "Login successful!"
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
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        password_confirm = data.get('password_confirm') # Standardized naming

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

    except json.JSONDecodeError:
        return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"status": False, "message": str(e)}, status=500)
    
@csrf_exempt
@require_POST
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)