import json

from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
@require_POST
def login_user(request):
    """
    View function for user login. Authenticates the user based on provided username and password.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :returns: JSON response indicating the result of the login attempt.
    :rtype: JsonResponse
    """

    # Authenticate the user
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password') # Should not be hashed with make_password()
    user = authenticate(username=username, password=password)
    
    # Login user if authentication is successful
    if user is not None:
        login(request, user)
        # Create refresh and access JWT
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        access_token = str(refresh.access_token)
        return JsonResponse({'status': 'success', 'msg': 'Login successful', 'refresh_token': refresh_token, 'access_token': access_token}, status=200)
    else:
        return JsonResponse({'status': 'failure', 'msg': 'Wrong username or password'}, status=401)

@csrf_exempt
@require_POST
def create_user(request):
    """
    View function for creating a new user.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :returns: JSON response indicating the result of the user creation attempt.
    :rtype: JsonResponse
    """
    
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user_group_str = data.get('group')

    # Check if the username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'username-exists', 'msg': 'Username already exists'}, status=400)



    # Create the user
    hashed_password = make_password(password)
    user = User.objects.create(
        username=username,
        password=hashed_password
    )
    # Add the user to the group
    user.save()

    # Return success response
    return JsonResponse({'success': 'User registered successfully'}, status=201)

@csrf_exempt
@require_POST
def create_group(request):
    """
    View function for creating a new group.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :returns: JSON response indicating the result of the group creation attempt.
    :rtype: JsonResponse
    """
    data = json.loads(request.body)
    group_name = data.get('group_name')

    # Check if the group already exists
    if Group.objects.filter(name=group_name).exists():
        return JsonResponse({'error': 'group-exists', 'msg': 'Group already exists'}, status=400)

    # Create the group
    group = Group.objects.create(
        name=group_name
    )
    group.save()

    # Return success response
    return JsonResponse({'success': 'Group created successfully'}, status=201)