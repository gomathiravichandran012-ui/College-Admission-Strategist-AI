from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import StudentRegistrationForm, StudentProfileForm
from students.models import StudentProfile
from django.contrib.auth.decorators import login_required


def register_view(request):

    if request.method == 'POST':

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            full_name = form.cleaned_data['full_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            StudentProfile.objects.create(
                user=user,
                full_name=full_name
            )

            messages.success(
                request,
                "Registration successful! Please login."
            )

            return redirect('login')

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )
from django.contrib.auth import authenticate, login, logout


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(request, 'accounts/login.html')


def logout_view(request):

    logout(request)

    return redirect('login')
@login_required
def dashboard_view(request):

    student = StudentProfile.objects.get(user=request.user)

    return render(
        request,
        'accounts/dashboard.html',
        {'student': student}
    )


@login_required
def profile_update_view(request):

    student, created = StudentProfile.objects.get_or_create(
    user=request.user
)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')

    else:
        form = StudentProfileForm(instance=student)

    return render(
        request,
        'accounts/profile_update.html',
        {'form': form, 'student': student}
    )


