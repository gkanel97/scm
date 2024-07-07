from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):
    """
    Handles a GET request to the home endpoint, requiring authentication.
    This endpoint returns a JSON response indicating successful access.

    :param request: HttpRequest object representing the incoming request.
    :type request: HttpRequest
    :return: JsonResponse object with a success message and status code 200.
    :rtype: JsonResponse
    """
    return JsonResponse({'msg': 'success', 'status': 200})