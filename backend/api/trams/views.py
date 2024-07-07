from django.utils import timezone
from django.db.models import Max, Q
from django.http import JsonResponse
from django.db.models import Prefetch
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta

from .models import TramStop , TramArrivals

@csrf_exempt
@require_POST
def get_tram_display_data(request):
    """
    Handles a GET request to retrieve tram display data.
    This endpoint queries TramStop and TramArrivals models to fetch the latest arrival information
    for each tram stop, combines outbound and inbound arrivals, and returns the data as a JSON response.

    :param request: HttpRequest object representing the incoming request.
    :type request: HttpRequest
    :return: JsonResponse object with tram display data for each tram stop.
    :rtype: JsonResponse
    """
    tram_stops = TramStop.objects.all()
    data_list = []

    now = datetime.now()
    formatted_datetime = now.strftime('%Y-%m-%dT%H:%M:%S')
    print(formatted_datetime)

    for stop in tram_stops:
        # Initialize an empty list for combined arrivals
        combined_arrivals = []
        
        # Fetch the latest outbound arrival
        latest_outbound_arrival = TramArrivals.objects.filter(
            stop_id=stop.code, direction='O'
        ).order_by('-arrival_time').values(
            'batch_id', 'arrival_time', 'stop_id', 'direction', 'destination', 'status'
        ).first()

        # Fetch the latest inbound arrival
        latest_inbound_arrival = TramArrivals.objects.filter(
            stop_id=stop.code, direction='I'
        ).order_by('-arrival_time').values(
            'batch_id', 'arrival_time', 'stop_id', 'direction', 'destination', 'status'
        ).first()

        # Check if the arrivals exist before adding them to the combined list
        if latest_outbound_arrival:
            combined_arrivals.append(latest_outbound_arrival)
        if latest_inbound_arrival:
            combined_arrivals.append(latest_inbound_arrival)

        # Append the stop information and its arrivals to the data list
        data_list.append({
            'stop_id': stop.id,
            'stop_name': stop.name,
            'latitude': stop.latitude,
            'longitude': stop.longitude,
            'line': stop.line,
            'arrivals': combined_arrivals
        })

    return JsonResponse(data_list, safe=False)

@csrf_exempt
@require_POST
def get_predictions(request):
    try:
        data = json.loads(request.body)
        selected_date = data.get('date')
        selected_line = data.get('line')
        print("selected_line",selected_line)

        model_path = os.path.join('trams/analytics/', f'{selected_line.lower().replace(" ", "_")}_model.pkl')
        print("model_path",model_path)
        if not os.path.exists(model_path):
            print("not found file")
            return JsonResponse({'error': 'Model file not found'}, status=404)
        
        print("file found")

        with open(model_path, 'rb') as file:
            model_data = pickle.load(file)
            model = model_data['model'] if 'model' in model_data else model_data
            forecast_timestamps = [datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(hours=i) for i in range(5, 24)]
            future = pd.DataFrame({ 'ds': forecast_timestamps })
            pred = model.predict(future)

            passengers = pred['yhat'].tolist()
            hours = list(range(5, 24))

            response_data = {'Hour': hours, 'Passengers': passengers}
            return JsonResponse(response_data, safe=False)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
