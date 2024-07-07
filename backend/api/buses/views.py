import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .monitor import BusDelayMonitor
from .timetables import TimetableOptimizer

@csrf_exempt
@require_POST
def get_bus_display_data(request):
    """
    Handles a POST request containing start and end times and returns bus delay data between these times.

    :param request: HttpRequest object containing JSON with 'start_time' and 'end_time'.
    :type request: HttpRequest
    :return: JsonResponse object with bus delays data.
    :rtype: JsonResponse
    """
    request_data = json.loads(request.body)
    start_time = request_data['start_time']
    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
    end_time = request_data['end_time']
    end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M')

    bus_monitor = BusDelayMonitor(start_time, end_time)
    delays_df = bus_monitor.calculate_delays()

    return JsonResponse(delays_df.to_dict('records'), safe=False, status = 200)

@csrf_exempt
@require_POST
def optimize_timetable(request):
    """
    Receives a POST request with first and last bus times and the target number of services,
    runs a genetic algorithm to optimize the bus timetable based on these parameters,
    and returns the optimized timetables.

    :param request: HttpRequest object that should contain 'first_bus', 'last_bus', and 'target_services' in its body.
    :type request: HttpRequest
    :return: JsonResponse containing the optimized bus timetables.
    :rtype: JsonResponse
    """
    
    data = json.loads(request.body)
    first_bus = data['first_bus']
    first_bus = datetime.strptime(first_bus, '%Y-%m-%d %H:%M')
    last_bus = data['last_bus']
    last_bus = datetime.strptime(last_bus, '%Y-%m-%d %H:%M')
    target_services = int(data['target_services'])
    
    timetable_optimizer = TimetableOptimizer(
        first_bus=first_bus,
        last_bus=last_bus,
        target_services=target_services
    )
    optimal_timetables = timetable_optimizer.genetic_algorithm()
    return JsonResponse({'optimal_timetables': optimal_timetables}, status=200)
