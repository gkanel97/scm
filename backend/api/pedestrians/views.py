import json
from .predictions import PedestrianPredictor

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

@require_POST
@csrf_exempt
@cache_page(60 * 5)
def get_pedestrian_predictions(request):
    """
    Handles a POST request containing target date and hour, predicts pedestrian footfall for each street,
    and returns the predictions as a JSON response.

    :param request: HttpRequest object containing JSON data with 'date' and 'hour'.
    :type request: HttpRequest
    :return: JsonResponse object containing predicted footfall for each street.
    :rtype: JsonResponse
    """
    request_data = json.loads(request.body)
    target_date = request_data.get('date')
    target_hour = request_data.get('hour')

    predictor = PedestrianPredictor()
    predictions = predictor.predict_footfall(target_date, target_hour)

    return JsonResponse({ 'pedestrian_predictions': predictions }, status=200)
    
