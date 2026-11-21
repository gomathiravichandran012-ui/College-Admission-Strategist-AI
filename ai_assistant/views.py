
import os
import json
import re
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
from .admission_tools import search_college_courses


load_dotenv()


# ==========================================
# GEMINI COLLEGE SEARCH TOOL
# ==========================================

COLLEGE_SEARCH_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_college_courses",
            description=(
                "Search the college database for available courses, "
                "college names, locations and verified fee details. "
                "Use this tool when students ask about colleges, "
                "courses, fees or college availability."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "course_name": types.Schema(
                        type=types.Type.STRING,
                        description="Course name, such as B.com or BCA"
                    ),
                    "state": types.Schema(
                        type=types.Type.STRING,
                        description="State name, such as Tamil Nadu"
                    )
                }
            )
        )
    ]
)


# ==========================================
# CHAT PAGE
# ==========================================

@login_required
def chat_view(request):
    return render(request, 'ai_assistant/chat.html')


# ==========================================
# AI ADMISSION STRATEGIST AGENT
# ==========================================

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

        # Get logged-in student's profile
        student = StudentProfile.objects.get(user=request.user)

        # Gemini API configuration
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

        # Domain-specific short-answer admission assistant prompt
        prompt = (
            "You are College Admission Strategist AI, "
            "a domain-specific college admission assistant.\n\n"

            "IMPORTANT RULES:\n"
            "1. Answer only questions related to college admissions, "
            "courses, eligibility, colleges, fees and admission planning.\n"
            "2. Politely refuse unrelated questions and redirect "
            "the student to college admission topics.\n"
            "3. Use the college search tool when database information "
            "about colleges, courses or fees is required.\n"
            "4. Never invent college names, fees or official admission details.\n"
            "5. Clearly explain when information is not available "
            "in the database.\n"
            "6. Give simple and useful answers.\n"
            "7. Your entire answer MUST contain no more than 2 short sentences.\n"
            "8. Keep each sentence under 15 words whenever possible.\n"
            "9. Use simple English and direct answers.\n"
            "10. Never write long paragraphs or unnecessary explanations.\n"
            "11. Mention official verification when admission details are uncertain.\n\n"

            f"Student Name: {student.full_name}\n"
            f"Education Stream: {student.education_stream}\n"
            f"Percentage: {student.percentage}\n"
            f"State: {student.state}\n\n"

            f"Student Question: {message}"
        )

        # Create Gemini chat with database search tool
        chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                tools=[COLLEGE_SEARCH_TOOL],
                max_output_tokens=100
            )
        )

        # Send student question to Gemini
        response = chat.send_message(prompt)

        # ==========================================
        # AGENT TOOL EXECUTION LOOP
        # ==========================================

        for _ in range(3):

            function_calls = response.function_calls

            if not function_calls:
                break

            function_responses = []

            for function_call in function_calls:

                if function_call.name == "search_college_courses":

                    arguments = function_call.args or {}

                    # Execute Django database search
                    results = search_college_courses(
                        course_name=arguments.get(
                            'course_name', ''
                        ),
                        state=arguments.get(
                            'state', ''
                        )
                    )

                    # Return database results to Gemini
                    function_responses.append(
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={
                                "result": results
                            }
                        )
                    )

            if not function_responses:
                break

            # Gemini processes the tool result
            response = chat.send_message(
                function_responses
            )

        # ==========================================
        # FINAL AI RESPONSE
        # ==========================================

        ai_reply = (response.text or "").strip()

        if not ai_reply:
            return JsonResponse(
                {
                    'error': (
                        'AI returned an empty response. '
                        'Please try again.'
                    )
                },
                status=503
            )

        # Enforce maximum of 2 sentences
        sentences = re.split(
            r'(?<=[.!?])\s+',
            ai_reply
        )

        ai_reply = " ".join(sentences[:2]).strip()

        # Save conversation in database
        ChatHistory.objects.create(
            student=student,
            user_message=message,
            ai_response=ai_reply
        )

        return JsonResponse({
            'reply': ai_reply
        })

    except StudentProfile.DoesNotExist:

        return JsonResponse(
            {
                'error': 'Please update your student profile first.'
            },
            status=400
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                'error': 'Invalid request format.'
            },
            status=400
        )

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        error_message = str(e)

        if '503' in error_message or 'UNAVAILABLE' in error_message:
            return JsonResponse(
                {
                    'error': (
                        'Gemini server is busy. '
                        'Please try again after a minute.'
                    )
                },
                status=503
            )

        if '504' in error_message or 'DEADLINE_EXCEEDED' in error_message:
            return JsonResponse(
                {
                    'error': (
                        'Gemini response is taking too long. '
                        'Please try again.'
                    )
                },
                status=504
            )

        return JsonResponse(
            {
                'error': 'Something went wrong. Please try again.'
            },
            status=500
        )


# ==========================================
# CHAT HISTORY
# ==========================================

@login_required
def chat_history_view(request):

    try:

        student = StudentProfile.objects.get(
            user=request.user
        )

        chats = ChatHistory.objects.filter(
            student=student
        ).order_by('-created_at')

        for chat_item in chats:

            chat_item.formatted_response = markdown.markdown(
                chat_item.ai_response,
                extensions=['extra', 'nl2br']
            )

        return render(
            request,
            'ai_assistant/chat_history.html',
            {
                'chats': chats
            }
        )

    except StudentProfile.DoesNotExist:

        return render(
            request,
            'ai_assistant/chat_history.html',
            {
                'chats': []
            }
        )
