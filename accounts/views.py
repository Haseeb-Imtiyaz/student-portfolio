from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegistrationForm, StudentProfileForm, EmployerProfileForm, UserUpdateForm
from .models import StudentProfile, EmployerProfile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Redirect to appropriate profile creation based on user type
            if user.user_type == 'student':
                return redirect('create_student_profile')
            elif user.user_type == 'employer':
                return redirect('create_employer_profile')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def create_student_profile(request):
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Student profile created successfully!')
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm()
    return render(request, 'accounts/create_student_profile.html', {'form': form})

@login_required
def create_employer_profile(request):
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Employer profile created successfully!')
            return redirect('employer_dashboard')
    else:
        form = EmployerProfileForm()
    return render(request, 'accounts/create_employer_profile.html', {'form': form})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if request.user.user_type == 'student':
            profile_form = StudentProfileForm(request.POST, request.FILES, 
                                            instance=request.user.student_profile)
        else:
            profile_form = EmployerProfileForm(request.POST, request.FILES, 
                                             instance=request.user.employer_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        if request.user.user_type == 'student':
            profile_form = StudentProfileForm(instance=request.user.student_profile)
        else:
            profile_form = EmployerProfileForm(instance=request.user.employer_profile)
    
    return render(request, 'accounts/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile(request):
    context = {}
    if request.user.user_type == 'student':
        context['profile'] = request.user.student_profile
    else:
        context['profile'] = request.user.employer_profile
    return render(request, 'accounts/profile.html', context) 