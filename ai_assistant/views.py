from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .services import AIService


@login_required
def chat_view(request):
    return render(request, 'ai_assistant/chat.html')


@csrf_exempt
@require_POST
@login_required
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        response = AIService.get_response(user_message, conversation_history)

        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'response': 'Sorry, something went wrong. Please try again.'
        }, status=500)


@csrf_exempt
@require_POST
@login_required
def search_api(request):
    try:
        data = json.loads(request.body)
        source = data.get('source', '')
        destination = data.get('destination', '')
        date = data.get('date', '')

        results = AIService.search_buses(source, destination, date)

        return JsonResponse({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'results': []
        }, status=500)
