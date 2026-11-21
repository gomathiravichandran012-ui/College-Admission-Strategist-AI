
import os
import json
import markdown

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from dotenv import load_dotenv
from google import genai
from google.genai import types

from students.models import StudentProfile
from .models import ChatHistory

load_dotenv()


@login_required
def chat_view(request):
    return render(request, 'ai_assistant/chat.html')


@login_required
@require_POST
@csrf_protect
def chat_api(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse(
                {'error': 'Please enter a message.'},
                status=400
            )

        student = StudentProfile.objects.get(user=request.user)

        api_key = os.getenv('GEMINI_API_KEY')
        model = os.getenv('GEMINI_MODEL')

        if not api_key or not model:
            return JsonResponse(
                {'error': 'Gemini API settings are missing.'},
                status=500
            )

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=60000,
                retry_options=types.HttpRetryOptions(
                    attempts=2
                )
            )
        )

        prompt = (
            "You are a helpful College Admission Strategist AI. "
            "Answer in simple language. Keep answers short and useful. "
            "Never invent official admission details.\n"
            f"Student: {student.full_name}\n"
            f"Stream: {student.education_stream}\n"
            f"Percentage: {student.percentage}\n"
            f"State: {student.state}\n"
            f"Question: {message}"
        )

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=120
            )
        )

        ai_reply = response.text

        if not ai_reply:
            return JsonResponse(
                {'error': 'AI returned an empty response. Please try again.'},
                status=503
            )

        ChatHistory.objects.create(
            student=student,
            user_message=message,
            ai_response=ai_reply
        )

        return JsonResponse({'reply': ai_reply})

    except StudentProfile.DoesNotExist:
        return JsonResponse(
            {'error': 'Please update your student profile first.'},
            status=400
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid request format.'},
            status=400
        )

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        error_message = str(e)

        if '503' in error_message or 'UNAVAILABLE' in error_message:
            return JsonResponse(
                {'error': 'Gemini server is busy. Please try again after a minute.'},
                status=503
            )

        if '504' in error_message or 'DEADLINE_EXCEEDED' in error_message:
            return JsonResponse(
                {'error': 'Gemini response is taking too long. Please try again.'},
                status=504
            )

        return JsonResponse(
            {'error': error_message},
            status=500
        )
@login_required
def chat_history_view(request):
    try:
        student = StudentProfile.objects.get(user=request.user)

        chats = ChatHistory.objects.filter(
            student=student
        ).order_by('-created_at')

        for chat in chats:
            chat.formatted_response = markdown.markdown(
                chat.ai_response,
                extensions=['extra', 'nl2br']
            )

        return render(
            request,
            'ai_assistant/chat_history.html',
            {'chats': chats}
        )

    except StudentProfile.DoesNotExist:
        return render(
            request,
            'ai_assistant/chat_history.html',
            {'chats': []}
        )