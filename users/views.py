from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from .forms import (
    UserRegistrationForm, StudentProfileForm, EmployerProfileForm, UserUpdateForm,
    AcademicRecordForm, ProjectForm, ProjectFileForm, ContestForm, JobForm,
    JobApplicationForm, SkillForm, StudentSkillForm, ResumeTemplateForm,
    NotificationForm, CollegeForm, CourseForm, PlacementOfficerForm,
    NotificationSettingsForm, JobFilterForm, PlacementOfficerProfileForm,
    AnnouncementForm
)
from .models import (
    StudentProfile, EmployerProfile, AcademicRecord, Project, Contest,
    Job, JobApplication, Skill, StudentSkill, ResumeTemplate,
    Notification, College, Course, PlacementOfficer, JobBookmark,
    ProjectFile, User, Announcement
)
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from reportlab.lib.colors import HexColor
from django.db.models import Q
from django.template.exceptions import TemplateDoesNotExist
import csv
from datetime import datetime
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # If user type is admin, set staff and superuser permissions
            if user.user_type == 'admin':
                user.is_staff = True
                user.is_superuser = True
            
            # Generate email verification token
            user.generate_email_verification_token()
            
            user.save()
            send_verification_email(request, user)
            messages.info(request, 'Please check your email to verify your account.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def create_student_profile(request):
    # Check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can create student profiles.')
        return redirect('home')
    
    # Check if profile already exists
    try:
        existing_profile = StudentProfile.objects.get(user=request.user)
        messages.info(request, 'You already have a profile. You can update it instead.')
        return redirect('update_profile')
    except StudentProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                profile = form.save(commit=False)
                profile.user = request.user
                
                # Get college and course from POST data
                college_id = request.POST.get('college')
                course_id = request.POST.get('course')
                
                if college_id:
                    profile.college = College.objects.get(id=college_id)
                if course_id:
                    profile.course = Course.objects.get(id=course_id)
                
                profile.save()
                messages.success(request, 'Your profile has been created successfully!')
                return redirect('student_dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred while creating your profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentProfileForm()
    
    context = {
        'form': form,
        'colleges': College.objects.filter(is_active=True),
        'courses': Course.objects.filter(is_active=True),
    }
    return render(request, 'users/create_student_profile.html', context)

@login_required
def create_employer_profile(request):
    # First check if user already has a profile
    try:
        existing_profile = EmployerProfile.objects.get(user=request.user)
        messages.info(request, 'You already have an employer profile. Use the update form to modify it.')
        return redirect('update_profile')
    except EmployerProfile.DoesNotExist:
        # Only proceed with creation if no profile exists
        if request.method == 'POST':
            form = EmployerProfileForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Create new profile
                    profile = form.save(commit=False)
                    profile.user = request.user
                    profile.save()
                    messages.success(request, 'Your employer profile has been created successfully!')
                    return redirect('employer_dashboard')
                except Exception as e:
                    messages.error(request, f'An error occurred while creating your profile: {str(e)}')
                    return redirect('create_employer_profile')
        else:
            form = EmployerProfileForm()
        
        return render(request, 'users/create_employer_profile.html', {'form': form})

@login_required
def update_profile(request):
    # Initialize forms
    u_form = UserUpdateForm(instance=request.user)
    p_form = None  # Initialize p_form as None
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if request.user.user_type == 'student':
            try:
                p_form = StudentProfileForm(request.POST, request.FILES, instance=request.user.student_profile)
            except StudentProfile.DoesNotExist:
                messages.error(request, 'Please create your student profile first.')
                return redirect('create_student_profile')
        elif request.user.user_type == 'employer':
            try:
                p_form = EmployerProfileForm(request.POST, request.FILES, instance=request.user.employer_profile)
            except EmployerProfile.DoesNotExist:
                messages.error(request, 'Please create your employer profile first.')
                return redirect('create_employer_profile')
        elif request.user.user_type == 'placement_officer':
            try:
                p_form = PlacementOfficerProfileForm(request.POST, instance=request.user.placement_officer_profile)
            except PlacementOfficer.DoesNotExist:
                messages.error(request, 'Please create your placement officer profile first.')
                return redirect('create_placement_officer_profile')
            
        # For admin users, we only need to validate and save the user form
        if request.user.user_type == 'admin':
            if u_form.is_valid():
                try:
                    u_form.save()
                    messages.success(request, 'Your profile has been updated!')
                    return redirect('admin_dashboard')
                except Exception as e:
                    messages.error(request, f'An error occurred while updating your profile: {str(e)}')
        else:
            # For other user types, validate both forms
            if u_form.is_valid() and (p_form is None or p_form.is_valid()):
                try:
                    u_form.save()
                    if p_form:
                        p_form.save()
                    messages.success(request, 'Your profile has been updated!')
                    
                    # Redirect based on user type
                    if request.user.user_type == 'student':
                        return redirect('student_dashboard')
                    elif request.user.user_type == 'employer':
                        return redirect('employer_dashboard')
                    elif request.user.user_type == 'placement_officer':
                        return redirect('placement_officer_dashboard')
                    else:
                        return redirect('home')
                except Exception as e:
                    messages.error(request, f'An error occurred while updating your profile: {str(e)}')
            else:
                if not u_form.is_valid():
                    for field, errors in u_form.errors.items():
                        for error in errors:
                            messages.error(request, f'Error in {field}: {error}')
                if p_form and not p_form.is_valid():
                    for field, errors in p_form.errors.items():
                        for error in errors:
                            messages.error(request, f'Error in {field}: {error}')
    else:
        if request.user.user_type == 'student':
            try:
                p_form = StudentProfileForm(instance=request.user.student_profile)
            except StudentProfile.DoesNotExist:
                messages.error(request, 'Please create your student profile first.')
                return redirect('create_student_profile')
        elif request.user.user_type == 'employer':
            try:
                p_form = EmployerProfileForm(instance=request.user.employer_profile)
            except EmployerProfile.DoesNotExist:
                messages.error(request, 'Please create your employer profile first.')
                return redirect('create_employer_profile')
        elif request.user.user_type == 'placement_officer':
            try:
                p_form = PlacementOfficerProfileForm(instance=request.user.placement_officer_profile)
            except PlacementOfficer.DoesNotExist:
                messages.error(request, 'Please create your placement officer profile first.')
                return redirect('create_placement_officer_profile')
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/update_profile.html', context)

@login_required
def profile(request):
    context = {}  # Initialize context dictionary
    
    try:
        if request.user.user_type == 'student':
            profile = request.user.student_profile
            profile.calculate_profile_completion()  # Calculate profile completion
            context = {
                'profile': profile,
                'profile_completion': profile.profile_completion,
            }
        elif request.user.user_type == 'employer':
            profile = request.user.employer_profile
            context = {
                'profile': profile,
            }
        elif request.user.user_type == 'placement_officer':
            profile = request.user.placement_officer_profile
            context = {
                'profile': profile,
            }
        elif request.user.user_type == 'admin':
            # For admin users, we use the User model directly
            context = {
                'profile': request.user,
            }
    except (StudentProfile.DoesNotExist, EmployerProfile.DoesNotExist, PlacementOfficer.DoesNotExist):
        messages.info(request, 'Please create your profile first.')
        if request.user.user_type == 'student':
            return redirect('create_student_profile')
        elif request.user.user_type == 'employer':
            return redirect('create_employer_profile')
        elif request.user.user_type == 'placement_officer':
            return redirect('create_placement_officer_profile')
    
    return render(request, 'users/profile.html', context)

def home(request):
    return render(request, 'users/home.html')

@login_required
def student_dashboard(request):
    # Check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can access the student dashboard.')
        return redirect('home')
    
    # Check if student profile exists
    if not hasattr(request.user, 'student_profile'):
        messages.info(request, 'Please create your student profile first.')
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    student_profile.calculate_profile_completion()
    
    # Get all statistics
    academic_performance = student_profile.get_academic_performance()
    project_stats = student_profile.get_project_stats()
    contest_stats = student_profile.get_contest_stats()
    job_stats = student_profile.get_job_stats()
    
    # Get recent activities - order by start_date if created_at doesn't exist
    try:
        recent_projects = student_profile.projects.all().order_by('-created_at')[:3]
    except:
        recent_projects = student_profile.projects.all().order_by('-start_date')[:3]
    
    recent_contests = student_profile.contests.all().order_by('-date_of_participation')[:3]
    recent_applications = student_profile.job_applications.all().order_by('-applied_date')[:3]
    
    # Get recent notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'student_profile': student_profile,
        'profile_completion': student_profile.profile_completion,
        'academic_performance': academic_performance,
        'project_stats': project_stats,
        'contest_stats': contest_stats,
        'job_stats': job_stats,
        'recent_projects': recent_projects,
        'recent_contests': recent_contests,
        'recent_applications': recent_applications,
        'notifications': notifications,
    }
    return render(request, 'users/student_dashboard.html', context)

@login_required
def employer_dashboard(request):
    if not hasattr(request.user, 'employer_profile'):
        return redirect('create_employer_profile')
    
    employer_profile = request.user.employer_profile
    
    # Get all jobs for the employer
    jobs = Job.objects.filter(employer=employer_profile)
    
    # Calculate statistics
    total_jobs = jobs.count()
    active_jobs = jobs.filter(is_active=True).count()
    total_applications = JobApplication.objects.filter(job__employer=employer_profile).count()
    hired_count = JobApplication.objects.filter(job__employer=employer_profile, status='hired').count()
    
    # Get recent applications
    recent_applications = JobApplication.objects.filter(
        job__employer=employer_profile
    ).order_by('-applied_date')[:5]
    
    # Get recent jobs
    recent_jobs = jobs.order_by('-created_at')[:5]
    
    context = {
        'employer_profile': employer_profile,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'hired_count': hired_count,
        'recent_applications': recent_applications,
        'recent_jobs': recent_jobs
    }
    return render(request, 'users/employer_dashboard.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def academic_records(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    
    if request.method == 'POST':
        form = AcademicRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = student_profile
            record.save()
            messages.success(request, 'Academic record added successfully!')
            return redirect('academic_records')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AcademicRecordForm()
    
    # Get academic records grouped by semester
    records = {}
    semester_gpas = {}
    
    for record in student_profile.academic_records.all().order_by('semester'):
        if record.semester not in records:
            records[record.semester] = []
            semester_gpas[record.semester] = AcademicRecord.calculate_semester_gpa(student_profile, record.semester)
        records[record.semester].append(record)
    
    # Calculate CGPA
    cgpa = AcademicRecord.calculate_cgpa(student_profile)
    
    # Calculate academic performance percentage
    total_marks = sum(record.marks_obtained for record in student_profile.academic_records.all())
    total_max_marks = sum(record.max_marks for record in student_profile.academic_records.all() if record.max_marks)
    academic_performance = (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
    
    context = {
        'form': form,
        'records': records,
        'semester_gpas': semester_gpas,
        'cgpa': cgpa,
        'academic_performance': round(academic_performance, 2)
    }
    return render(request, 'users/academic_records.html', context)

@login_required
def projects(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    projects = student_profile.projects.all()
    project_stats = student_profile.get_project_stats()
    
    # Handle project creation
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.student = student_profile
            project.save()
            messages.success(request, 'Project added successfully!')
            return redirect('projects')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    
    # Filter projects by type if specified
    project_type = request.GET.get('type')
    if project_type:
        projects = projects.filter(project_type=project_type)
    
    context = {
        'projects': projects,
        'project_stats': project_stats,
        'form': form
    }
    return render(request, 'users/projects.html', context)

@login_required
def add_project_file(request, project_id):
    project = get_object_or_404(Project, id=project_id, student=request.user.student_profile)
    
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.save()
            messages.success(request, 'File added successfully!')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectFileForm()
    
    return render(request, 'users/add_project_file.html', {
        'form': form,
        'project': project
    })

@login_required
def contests(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    contests = student_profile.contests.all()
    contest_stats = student_profile.get_contest_stats()
    
    # Handle contest creation
    if request.method == 'POST':
        form = ContestForm(request.POST, request.FILES)
        if form.is_valid():
            contest = form.save(commit=False)
            contest.student = student_profile
            contest.save()
            messages.success(request, 'Contest added successfully!')
            return redirect('contests')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContestForm()
    
    # Filter contests by category if specified
    category = request.GET.get('category')
    if category:
        contests = contests.filter(category=category)
    
    context = {
        'contests': contests,
        'contest_stats': contest_stats,
        'form': form
    }
    return render(request, 'users/contests.html', context)

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, student=request.user.student_profile)
    
    if request.method == 'POST':
        file_form = ProjectFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            project_file = file_form.save(commit=False)
            project_file.project = project
            project_file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('project_detail', project_id=project.id)
    else:
        file_form = ProjectFileForm()
    
    context = {
        'project': project,
        'file_form': file_form
    }
    return render(request, 'users/project_detail.html', context)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, student=request.user.student_profile)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('projects')
    return render(request, 'users/confirm_delete.html', {'object': project})

@login_required
def delete_contest(request, contest_id):
    try:
        contest = Contest.objects.get(id=contest_id)
        # Check if the contest belongs to the current user
        if contest.student.user != request.user:
            messages.error(request, "You don't have permission to delete this contest.")
            return redirect('contests')
        
        # Delete the contest
        contest.delete()
        messages.success(request, "Contest deleted successfully.")
    except Contest.DoesNotExist:
        messages.error(request, "Contest not found.")
    
    return redirect('contests')

@login_required
def job_applications(request):
    # Check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can view job applications.')
        return redirect('home')
    
    # Check if student profile exists
    if not hasattr(request.user, 'student_profile'):
        messages.info(request, 'Please create your student profile first.')
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    
    # Get all applications for the student
    applications = JobApplication.objects.filter(student=student_profile)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    # Get job statistics
    job_stats = {
        'total': applications.count(),
        'applied': applications.filter(status='applied').count(),
        'under_review': applications.filter(status='under_review').count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'rejected': applications.filter(status='rejected').count(),
        'hired': applications.filter(status='hired').count()
    }
    
    context = {
        'applications': applications,
        'job_stats': job_stats,
        'current_status': status
    }
    return render(request, 'users/job_applications.html', context)

@login_required
def generate_resume(request, template_id=None):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    
    if request.method == 'POST':
        template_id = request.POST.get('template') or template_id
        template = get_object_or_404(ResumeTemplate, id=template_id)
        
        # Get all required data
        academic_records = student_profile.academic_records.all()
        projects = student_profile.projects.all()
        contests = student_profile.contests.all()
        student_skills = student_profile.skills.all()
        
        # Calculate CGPA
        cgpa = AcademicRecord.calculate_cgpa(student_profile)
        
        # Render the template with context
        context = {
            'student_profile': student_profile,
            'academic_records': {
                'cgpa': cgpa,
                'records': academic_records
            },
            'projects': projects,
            'contests': contests,
            'student_skills': student_skills
        }
        
        # Get the template path and remove any 'templates/' prefix
        template_path = template.template_path
        if template_path.startswith('templates/'):
            template_path = template_path[10:]  # Remove 'templates/' prefix
        
        try:
            # Render the template
            rendered_content = render_to_string(template_path, context)
            
            # Create PDF using ReportLab
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            section_style = ParagraphStyle(
                'Section',
                parent=styles['Heading2'],
                fontSize=18,
                spaceAfter=20,
                textColor=HexColor('#333333')
            )
            
            # Create paragraphs with proper styling
            paragraphs = []
            
            # Add header
            paragraphs.append(Paragraph(student_profile.user.get_full_name(), title_style))
            
            # Add contact info
            contact_info = f"{student_profile.phone_number} | {student_profile.user.email}"
            if student_profile.linkedin_url:
                contact_info += f" | LinkedIn: {student_profile.linkedin_url}"
            if student_profile.github_url:
                contact_info += f" | GitHub: {student_profile.github_url}"
            paragraphs.append(Paragraph(contact_info, styles['Normal']))
            paragraphs.append(Spacer(1, 30))
            
            # Add education section
            paragraphs.append(Paragraph("Education", section_style))
            education_info = f"{student_profile.course.name}<br/>{student_profile.college.name}<br/>Expected Graduation: {student_profile.expected_graduation_year}<br/>CGPA: {cgpa}"
            paragraphs.append(Paragraph(education_info, styles['Normal']))
            paragraphs.append(Spacer(1, 20))
            
            # Add skills section
            if student_skills:
                paragraphs.append(Paragraph("Skills", section_style))
                skills_text = ", ".join([skill.skill.name for skill in student_skills])
                paragraphs.append(Paragraph(skills_text, styles['Normal']))
                paragraphs.append(Spacer(1, 20))
            
            # Add projects section
            if projects:
                paragraphs.append(Paragraph("Projects", section_style))
                for project in projects:
                    project_text = f"<b>{project.title}</b><br/>{project.role} | Team Size: {project.team_size}<br/>{project.description}<br/>Technologies: {project.tools_used}"
                    paragraphs.append(Paragraph(project_text, styles['Normal']))
                    paragraphs.append(Spacer(1, 10))
                paragraphs.append(Spacer(1, 10))
            
            # Add contests section
            if contests:
                paragraphs.append(Paragraph("Contests & Achievements", section_style))
                for contest in contests:
                    contest_text = f"<b>{contest.event_name}</b><br/>{contest.organized_by}<br/>Date: {contest.date_of_participation}<br/>Outcome: {contest.get_outcome_display()}"
                    paragraphs.append(Paragraph(contest_text, styles['Normal']))
                    paragraphs.append(Spacer(1, 10))
            
            # Build the PDF
            doc.build(paragraphs)
            
            # Get the PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            # Create a response with the PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{student_profile.user.get_full_name()}_resume.pdf"'
            response.write(pdf_content)
            
            return response
            
        except TemplateDoesNotExist:
            messages.error(request, 'Resume template not found. Please try a different template.')
            return redirect('resume_templates')
        except Exception as e:
            messages.error(request, f'Error generating resume: {str(e)}')
            return redirect('resume_templates')
    
    # If template_id is provided, show the generate form with that template
    if template_id:
        template = get_object_or_404(ResumeTemplate, id=template_id)
        templates = [template]
    else:
        templates = ResumeTemplate.objects.filter(is_active=True)
    
    context = {
        'templates': templates,
        'selected_template_id': template_id
    }
    return render(request, 'users/generate_resume.html', context)

@login_required
def download_resume(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    if not student_profile.resume_file:
        messages.error(request, 'No resume found. Please generate one first.')
        return redirect('generate_resume')
    
    response = HttpResponse(student_profile.resume_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student_profile.resume_file.name}"'
    return response

@login_required
def notifications(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    notifications = request.user.notifications.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'users/notifications.html', context)

@login_required
def notification_settings(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your notification settings have been updated!')
            return redirect('notifications')
    else:
        form = NotificationSettingsForm(instance=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'users/notification_settings.html', context)

@login_required
def college_list(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    colleges = College.objects.all()
    context = {
        'colleges': colleges
    }
    return render(request, 'users/college_list.html', context)

@login_required
def course_list(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    courses = Course.objects.all()
    context = {
        'courses': courses
    }
    return render(request, 'users/course_list.html', context)

@login_required
def placement_officers(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    officers = PlacementOfficer.objects.all()
    context = {
        'officers': officers
    }
    return render(request, 'users/placement_officers.html', context)

def send_notification(user, title, message, notification_type='system'):
    # Create notification in database
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )
    
    # Send email if user has email notifications enabled
    if user.email_notifications:
        html_message = render_to_string('users/email_notification.html', {
            'user': user,
            'title': title,
            'message': message,
            'notification_type': notification_type
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            title,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True
        )
    
    return notification

@login_required
def toggle_job_bookmark(request, job_id):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    job = get_object_or_404(Job, id=job_id)
    bookmark, created = JobBookmark.objects.get_or_create(user=request.user, job=job)
    
    if not created:
        bookmark.delete()
        messages.success(request, 'Job removed from bookmarks.')
    else:
        messages.success(request, 'Job added to bookmarks.')
    
    return redirect('job_detail', job_id=job_id)

@login_required
def bookmarked_jobs(request):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    bookmarks = JobBookmark.objects.filter(user=request.user)
    jobs = [bookmark.job for bookmark in bookmarks]
    
    context = {
        'jobs': jobs
    }
    return render(request, 'users/bookmarked_jobs.html', context)

@login_required
def delete_project_file(request, project_id, file_id):
    project = get_object_or_404(Project, id=project_id, student=request.user.student_profile)
    project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
    
    if request.method == 'POST':
        project_file.file.delete()  # Delete the actual file
        project_file.delete()  # Delete the database record
        messages.success(request, 'File deleted successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'users/confirm_delete.html', {
        'object': project_file,
        'back_url': reverse('project_detail', args=[project.id])
    })

def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_email_verified:
            # Verify the token using the model method
            if user.verify_email(token):
                user.is_verified = True  # Set is_verified to True for admin users
                user.save()
                messages.success(request, 'Your email has been verified successfully!')
            else:
                messages.error(request, 'Verification token has expired. Please request a new verification email.')
                return redirect('home')
        else:
            messages.info(request, 'Your email is already verified.')
        return redirect('login')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
        return redirect('home')

def send_verification_email(request, user):
    token = user.email_verification_token
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )
    
    subject = 'Verify your email address'
    html_message = render_to_string('users/email_verification.html', {
        'user': user,
        'verification_url': verification_url,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )

@login_required
def job_list(request):
    # Check if user is a student or employer
    if request.user.user_type == 'student':
        if not hasattr(request.user, 'student_profile'):
            return redirect('create_student_profile')
    elif request.user.user_type == 'employer':
        if not hasattr(request.user, 'employer_profile'):
            return redirect('create_employer_profile')
    
    # Get jobs based on user type
    if request.user.user_type == 'employer':
        jobs = Job.objects.filter(employer=request.user.employer_profile)
    else:
        jobs = Job.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(employer__company_name__icontains=query)
        )
    
    # Advanced search filters
    job_type = request.GET.get('type')
    location = request.GET.get('location')
    skills = request.GET.get('skills')
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if skills:
        skills_list = [skill.strip() for skill in skills.split(',')]
        for skill in skills_list:
            jobs = jobs.filter(skills_required__icontains=skill)
    
    # Add bookmark status for students
    if request.user.user_type == 'student':
        for job in jobs:
            job.is_bookmarked = JobBookmark.objects.filter(student=request.user.student_profile, job=job).exists()
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)
    
    # Create filter form
    filter_form = JobFilterForm(request.GET or None)
    
    context = {
        'jobs': jobs,
        'filter_form': filter_form,
        'query': query,
        'is_employer': request.user.user_type == 'employer'
    }
    return render(request, 'users/job_list.html', context)

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # If user is a student, check for student profile
    if request.user.user_type == 'student':
        if not hasattr(request.user, 'student_profile'):
            return redirect('create_student_profile')
        is_bookmarked = JobBookmark.objects.filter(student=request.user.student_profile, job=job).exists()
    else:
        # For employers, check if they own the job
        if request.user.user_type == 'employer' and hasattr(request.user, 'employer_profile'):
            is_owner = job.employer == request.user.employer_profile
        else:
            is_owner = False
        is_bookmarked = False
    
    # Calculate application statistics
    total_applications = job.applications.count()
    shortlisted_count = job.applications.filter(status='shortlisted').count()
    hired_count = job.applications.filter(status='hired').count()
    
    context = {
        'job': job,
        'is_bookmarked': is_bookmarked,
        'is_owner': is_owner if request.user.user_type == 'employer' else False,
        'total_applications': total_applications,
        'shortlisted_count': shortlisted_count,
        'hired_count': hired_count
    }
    return render(request, 'users/job_detail.html', context)

@login_required
def job_apply(request, job_id):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    job = get_object_or_404(Job, id=job_id)
    student_profile = request.user.student_profile
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, student=student_profile).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = student_profile
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', job_id=job_id)
    else:
        form = JobApplicationForm()
    
    context = {
        'form': form,
        'job': job
    }
    return render(request, 'users/job_apply.html', context)

@login_required
def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'users/skill_list.html', {'skills': skills})

@login_required
def add_skill(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can add skills.')
        return redirect('home')
    
    if request.method == 'POST':
        form = StudentSkillForm(request.POST)
        if form.is_valid():
            student_skill = form.save(commit=False)
            student_skill.student = request.user.studentprofile
            student_skill.save()
            messages.success(request, 'Skill added successfully!')
            return redirect('profile')
    else:
        form = StudentSkillForm()
    return render(request, 'users/skill_form.html', {'form': form})

@login_required
def resume_templates(request):
    templates = ResumeTemplate.objects.filter(is_active=True)
    return render(request, 'users/resume_templates.html', {'templates': templates})

@login_required
def job_create(request):
    if not hasattr(request.user, 'employer_profile'):
        messages.error(request, 'Only employers can create jobs.')
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.employer_profile
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'users/job_form.html', {
        'form': form,
        'title': 'Post New Job'
    })

@login_required
def employer_job_applications(request, job_id=None):
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can view applications.')
        return redirect('home')
    
    if not hasattr(request.user, 'employer_profile'):
        messages.error(request, 'Please create an employer profile first.')
        return redirect('create_employer_profile')
    
    employer_profile = request.user.employer_profile
    job = None
    if job_id:
        job = get_object_or_404(Job, id=job_id, employer=employer_profile)
        applications = job.applications.all()
    else:
        applications = JobApplication.objects.filter(job__employer=employer_profile)
    
    # Get all jobs for the employer
    jobs = Job.objects.filter(employer=employer_profile)
    
    context = {
        'applications': applications,
        'jobs': jobs,
        'selected_job': job
    }
    return render(request, 'users/employer_applications.html', context)

@login_required
def update_application_status(request, application_id):
    if not hasattr(request.user, 'employer_profile'):
        messages.error(request, 'Only employers can update application status.')
        return redirect('home')
    
    application = get_object_or_404(JobApplication, id=application_id)
    if application.job.employer != request.user.employer_profile:
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('employer_job_applications')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, 'Application status updated successfully.')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('employer_job_applications', job_id=application.job.id)

@login_required
def delete_job(request, job_id):
    if not hasattr(request.user, 'employer_profile'):
        messages.error(request, 'Only employers can delete jobs.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id, employer=request.user.employer_profile)
    job.delete()
    messages.success(request, 'Job post deleted successfully.')
    return redirect('employer_dashboard')

@login_required
def job_edit(request, job_id):
    if not hasattr(request.user, 'employer_profile'):
        messages.error(request, 'Only employers can edit jobs.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'users/job_form.html', {
        'form': form,
        'title': 'Edit Job',
        'job': job
    })

def is_placement_officer(user):
    return (user.is_authenticated and 
            user.user_type == 'placement_officer' and 
            hasattr(user, 'placement_officer_profile') and 
            user.placement_officer_profile.is_approved)

@login_required
@user_passes_test(is_placement_officer)
def placement_officer_dashboard(request):
    try:
        officer = request.user.placement_officer_profile
        context = {
            'profile_stats': officer.get_profile_completion_stats(),
            'resume_stats': officer.get_resume_stats(),
            'application_stats': officer.get_application_stats(),
        }
        return render(request, 'users/placement_officer/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing dashboard: {str(e)}')
        return redirect('home')

@login_required
@user_passes_test(is_placement_officer)
def student_list(request):
    try:
        officer = request.user.placement_officer_profile
        department = request.GET.get('department')
        semester = request.GET.get('semester')
        min_applications = request.GET.get('min_applications', 0)
        
        # Get students from the officer's college
        students = StudentProfile.objects.filter(college=officer.college).select_related('user', 'course')
        
        if department:
            students = students.filter(course_id=department)
        if semester:
            students = students.filter(semester=semester)
        if min_applications:
            students = students.annotate(
                application_count=Count('job_applications')
            ).filter(application_count__gte=int(min_applications))
        
        # Add has_resume property to each student
        for student in students:
            student.has_resume = student.job_applications.filter(resume__isnull=False).exists()
        
        context = {
            'students': students,
            'departments': Course.objects.all(),  # Get all courses since they're not college-specific
            'semesters': range(1, 9),  # Assuming 8 semesters
        }
        return render(request, 'users/placement_officer/student_list.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing student list: {str(e)}')
        return redirect('home')

@login_required
@user_passes_test(is_placement_officer)
def download_student_report(request):
    try:
        officer = request.user.placement_officer_profile
        department = request.GET.get('department')
        semester = request.GET.get('semester')
        
        students = StudentProfile.objects.filter(college=officer.college)
        if department:
            students = students.filter(course_id=department)
        if semester:
            students = students.filter(semester=semester)
            
        # Add has_resume property to each student
        for student in students:
            student.has_resume = student.job_applications.filter(resume__isnull=False).exists()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="student_report_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Department', 'Semester', 'Phone', 'Profile Completion', 'Resume Status', 'Applications'])
        
        for student in students:
            profile_completion = 'Complete' if student.profile_picture and student.bio and student.linkedin_url else 'Incomplete'
            resume_status = 'Uploaded' if student.has_resume else 'Not Uploaded'
            applications = student.job_applications.count()
            
            # Format phone number to avoid Excel formula interpretation
            phone_number = f"'{student.phone_number}" if student.phone_number else 'N/A'
            
            writer.writerow([
                student.user.get_full_name(),
                student.user.email,
                student.course.name if student.course else 'N/A',
                student.semester,
                phone_number,
                profile_completion,
                resume_status,
                applications
            ])
        
        return response
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('home')

@login_required
@user_passes_test(is_placement_officer)
def student_detail(request, student_id):
    try:
        student = get_object_or_404(StudentProfile, id=student_id, college=request.user.placement_officer_profile.college)
        applications = student.job_applications.all()
        projects = student.projects.all()
        
        # Add has_resume property
        student.has_resume = student.job_applications.filter(resume__isnull=False).exists()
        
        context = {
            'student': student,
            'applications': applications,
            'projects': projects,
        }
        return render(request, 'users/placement_officer/student_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing student details: {str(e)}')
        return redirect('home')

def custom_login(request):
    if request.user.is_authenticated:
        # If user is already logged in, redirect based on user type
        if request.user.is_staff:
            if not request.user.is_verified:
                messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
                return redirect('home')
            return redirect('admin_dashboard')
        elif request.user.user_type == 'student':
            if not hasattr(request.user, 'student_profile'):
                return redirect('create_student_profile')
            return redirect('student_dashboard')
        elif request.user.user_type == 'employer':
            if not hasattr(request.user, 'employer_profile'):
                return redirect('create_employer_profile')
            return redirect('employer_dashboard')
        elif request.user.user_type == 'placement_officer':
            if not hasattr(request.user, 'placement_officer_profile'):
                return redirect('create_placement_officer_profile')
            elif not request.user.placement_officer_profile.is_approved:
                messages.warning(request, 'Your account is pending approval. Please wait for admin approval.')
                return redirect('home')
            return redirect('placement_officer_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            
            # Redirect based on user type
            if user.is_staff:
                if not user.is_verified:
                    messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
                    return redirect('home')
                return redirect('admin_dashboard')
            elif user.user_type == 'student':
                if not hasattr(user, 'student_profile'):
                    return redirect('create_student_profile')
                return redirect('student_dashboard')
            elif user.user_type == 'employer':
                if not hasattr(user, 'employer_profile'):
                    return redirect('create_employer_profile')
                return redirect('employer_dashboard')
            elif user.user_type == 'placement_officer':
                if not hasattr(user, 'placement_officer_profile'):
                    return redirect('create_placement_officer_profile')
                elif not user.placement_officer_profile.is_approved:
                    messages.warning(request, 'Your account is pending approval. Please wait for admin approval.')
                    return redirect('home')
                return redirect('placement_officer_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def create_placement_officer_profile(request):
    # Check if user is a placement officer
    if request.user.user_type != 'placement_officer':
        messages.error(request, 'Only placement officers can create placement officer profiles.')
        return redirect('home')
    
    # Check if profile already exists
    try:
        existing_profile = PlacementOfficer.objects.get(user=request.user)
        messages.info(request, 'You already have a profile. You can update it instead.')
        return redirect('update_profile')
    except PlacementOfficer.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = PlacementOfficerProfileForm(request.POST)
        if form.is_valid():
            try:
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Your profile has been created successfully!')
                return redirect('placement_officer_dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred while creating your profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlacementOfficerProfileForm()
    
    context = {
        'form': form,
        'colleges': College.objects.filter(is_active=True),
    }
    return render(request, 'users/placement_officer/create_profile.html', context)

@staff_member_required
def admin_dashboard(request):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
        
    # Get total counts
    total_students = StudentProfile.objects.count()
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    total_employers = EmployerProfile.objects.count()
    
    # Get latest job posts
    latest_jobs = Job.objects.select_related('employer').order_by('-created_at')[:5]
    
    # Get registration trends (last 7 days)
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    student_registrations = User.objects.filter(
        user_type='student',
        date_joined__gte=week_ago
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    employer_registrations = User.objects.filter(
        user_type='employer',
        date_joined__gte=week_ago
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Get activity heatmap data (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    daily_activity = JobApplication.objects.filter(
        applied_date__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('applied_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    context = {
        'total_students': total_students,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_employers': total_employers,
        'latest_jobs': latest_jobs,
        'student_registrations': list(student_registrations),
        'employer_registrations': list(employer_registrations),
        'daily_activity': list(daily_activity),
    }
    return render(request, 'users/admin/dashboard.html', context)

@staff_member_required
def student_management(request):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
        
    students = StudentProfile.objects.select_related('user', 'college', 'course')
    
    # Search and filter
    search_query = request.GET.get('search')
    college_id = request.GET.get('college')
    course_id = request.GET.get('course')
    specialization = request.GET.get('specialization')
    location = request.GET.get('location')
    
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )
    
    if college_id:
        students = students.filter(college_id=college_id)
    if course_id:
        students = students.filter(course_id=course_id)
    if specialization:
        students = students.filter(course__specialization__icontains=specialization)
    if location:
        students = students.filter(college__location__icontains=location)
    
    context = {
        'students': students,
        'colleges': College.objects.all(),
        'courses': Course.objects.all(),
    }
    return render(request, 'users/admin/student_management.html', context)

@staff_member_required
def admin_student_detail(request, student_id):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
    
    try:
        student = get_object_or_404(StudentProfile, id=student_id)
        applications = student.job_applications.all()
        projects = student.projects.all()
        academic_records = student.academic_records.all()
        contests = student.contests.all()
        
        # Calculate statistics
        academic_performance = student.get_academic_performance()
        project_stats = student.get_project_stats()
        contest_stats = student.get_contest_stats()
        job_stats = student.get_job_stats()
        
        context = {
            'student': student,
            'applications': applications,
            'projects': projects,
            'academic_records': academic_records,
            'contests': contests,
            'academic_performance': academic_performance,
            'project_stats': project_stats,
            'contest_stats': contest_stats,
            'job_stats': job_stats,
        }
        return render(request, 'users/admin/student_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing student details: {str(e)}')
        return redirect('student_management')

@staff_member_required
def employer_management(request):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
        
    employers = EmployerProfile.objects.select_related('user')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        employers = employers.filter(
            Q(company_name__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Filter by verification status
    verification_status = request.GET.get('verification_status')
    if verification_status == 'verified':
        employers = employers.filter(is_verified=True)
    elif verification_status == 'pending':
        employers = employers.filter(is_verified=False)
    
    # Get all jobs for statistics
    jobs = Job.objects.select_related('employer').all()
    
    context = {
        'employers': employers,
        'jobs': jobs,
    }
    return render(request, 'users/admin/employer_management.html', context)

@staff_member_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "suspended"
    messages.success(request, f'User {user.get_full_name()} has been {status}.')
    
    if user.user_type == 'student':
        return redirect('student_management')
    elif user.user_type == 'employer':
        return redirect('employer_management')
    return redirect('admin_dashboard')

@staff_member_required
def master_config(request):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
        
    context = {
        'colleges': College.objects.all(),
        'courses': Course.objects.all(),
        'skills': Skill.objects.all(),
        'templates': ResumeTemplate.objects.all(),
    }
    return render(request, 'users/admin/master_config.html', context)

@staff_member_required
def communication_panel(request):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
        
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        notification_type = request.POST.get('notification_type')
        
        if recipient_type == 'all':
            recipients = User.objects.filter(is_active=True)
        elif recipient_type == 'students':
            recipients = User.objects.filter(user_type='student', is_active=True)
        elif recipient_type == 'employers':
            recipients = User.objects.filter(user_type='employer', is_active=True)
        
        # Send email
        for recipient in recipients:
            html_message = render_to_string('users/email_notification.html', {
                'user': recipient,
                'message': message,
                'notification_type': notification_type
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                html_message=html_message,
                fail_silently=True
            )
            
            # Create notification
            Notification.objects.create(
                user=recipient,
                title=subject,
                message=message,
                notification_type=notification_type
            )
        
        messages.success(request, f'Message sent to {recipients.count()} recipients.')
        return redirect('communication_panel')
    
    # Get announcements
    announcements = Announcement.objects.all()
    
    # Get recent notifications
    notifications = Notification.objects.all().order_by('-created_at')[:10]
    
    context = {
        'announcements': announcements,
        'notifications': notifications,
        'announcement_form': AnnouncementForm(),
    }
    
    return render(request, 'users/admin/communication_panel.html', context)

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_email_verified:
                # Generate new token
                user.generate_email_verification_token()
                user.save()
                # Send new verification email
                send_verification_email(request, user)
                messages.success(request, 'A new verification email has been sent to your email address.')
            else:
                messages.info(request, 'Your email is already verified.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    return render(request, 'users/resend_verification.html')

@staff_member_required
def employer_detail(request, employer_id):
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    jobs = Job.objects.filter(employer=employer)
    context = {
        'employer': employer,
        'jobs': jobs,
    }
    return render(request, 'users/admin/employer_detail.html', context)

@staff_member_required
def verify_employer(request, employer_id):
    if request.method == 'POST':
        try:
            employer = get_object_or_404(EmployerProfile, id=employer_id)
            employer.is_verified = True
            employer.save()
            
            # Send notification to the employer
            try:
                send_notification(
                    employer.user,
                    'Account Verified',
                    'Your employer account has been verified. You can now access all features.',
                    'system'
                )
            except Exception as e:
                # Log the notification error but don't fail the verification
                print(f"Failed to send notification: {str(e)}")
            
            messages.success(request, f'Employer {employer.company_name} has been verified.')
        except Exception as e:
            messages.error(request, f'Error verifying employer: {str(e)}')
    return redirect('employer_management')

@staff_member_required
def delete_employer(request, employer_id):
    if request.method == 'POST':
        try:
            employer = get_object_or_404(EmployerProfile, id=employer_id)
            company_name = employer.company_name
            employer.user.delete()  # This will also delete the employer profile due to CASCADE
            messages.success(request, f'Employer {company_name} has been deleted.')
        except Exception as e:
            messages.error(request, f'Error deleting employer: {str(e)}')
    return redirect('employer_management')

@staff_member_required
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('communication_panel')
    else:
        form = AnnouncementForm()
    return render(request, 'users/admin/create_announcement.html', {'form': form})

@staff_member_required
def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully.')
            return redirect('communication_panel')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'users/admin/edit_announcement.html', {'form': form, 'announcement': announcement})

@staff_member_required
def delete_announcement(request, announcement_id):
    if request.method == 'POST':
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
    return redirect('communication_panel')

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    if request.method == 'POST':
        form = CollegeForm(request.POST, instance=college)
        if form.is_valid():
            form.save()
            messages.success(request, 'College updated successfully.')
            return redirect('master_config')
    else:
        form = CollegeForm(instance=college)
    context = {
        'colleges': College.objects.all(),
        'courses': Course.objects.all(),
        'skills': Skill.objects.all(),
        'templates': ResumeTemplate.objects.all(),
        'college_form': form
    }
    return render(request, 'users/admin/master_config.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            # Refresh the course instance to get updated data
            course.refresh_from_db()
            form = CourseForm(instance=course)
    else:
        form = CourseForm(instance=course)
    context = {
        'colleges': College.objects.all(),
        'courses': Course.objects.all(),
        'skills': Skill.objects.all(),
        'templates': ResumeTemplate.objects.all(),
        'course_form': form
    }
    return render(request, 'users/admin/master_config.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully.')
            # Refresh the skill instance to get updated data
            skill.refresh_from_db()
            form = SkillForm(instance=skill)
    else:
        form = SkillForm(instance=skill)
    context = {
        'colleges': College.objects.all(),
        'courses': Course.objects.all(),
        'skills': Skill.objects.all(),
        'templates': ResumeTemplate.objects.all(),
        'skill_form': form
    }
    return render(request, 'users/admin/master_config.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_template(request, template_id):
    template = get_object_or_404(ResumeTemplate, id=template_id)
    if request.method == 'POST':
        form = ResumeTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resume template updated successfully.')
            # Refresh the template instance to get updated data
            template.refresh_from_db()
            form = ResumeTemplateForm(instance=template)
    else:
        form = ResumeTemplateForm(instance=template)
    context = {
        'colleges': College.objects.all(),
        'courses': Course.objects.all(),
        'skills': Skill.objects.all(),
        'templates': ResumeTemplate.objects.all(),
        'template_form': form
    }
    return render(request, 'users/admin/master_config.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_college(request):
    if request.method == 'POST':
        form = CollegeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'College added successfully.')
            return redirect('master_config')
    else:
        form = CollegeForm()
    return render(request, 'users/admin/master_config.html', {'college_form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully.')
            return redirect('master_config')
    else:
        form = CourseForm()
    return render(request, 'users/admin/master_config.html', {'course_form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill added successfully.')
            return redirect('master_config')
    else:
        form = SkillForm()
    return render(request, 'users/admin/master_config.html', {'skill_form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_template(request):
    if request.method == 'POST':
        form = ResumeTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resume template added successfully.')
            return redirect('master_config')
    else:
        form = ResumeTemplateForm()
    return render(request, 'users/admin/master_config.html', {'template_form': form})

@staff_member_required
def placement_officer_management(request):
    # Check if user is verified
    if not request.user.is_verified:
        messages.warning(request, 'Please verify your email before accessing the admin dashboard.')
        return redirect('home')
        
    officers = PlacementOfficer.objects.select_related('user', 'college').all()
    
    # Search and filter
    search_query = request.GET.get('search')
    college_id = request.GET.get('college')
    approval_status = request.GET.get('approval_status')
    
    if search_query:
        officers = officers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(designation__icontains=search_query)
        )
    
    if college_id:
        officers = officers.filter(college_id=college_id)
    if approval_status:
        officers = officers.filter(is_approved=approval_status == 'approved')
    
    context = {
        'officers': officers,
        'colleges': College.objects.all(),
    }
    return render(request, 'users/admin/placement_officer_management.html', context)

@staff_member_required
def approve_placement_officer(request, officer_id):
    if request.method == 'POST':
        try:
            officer = get_object_or_404(PlacementOfficer, id=officer_id)
            officer.is_approved = True
            officer.is_rejected = False
            officer.save()
            
            # Send notification to the placement officer
            try:
                send_notification(
                    officer.user,
                    'Account Approved',
                    'Your placement officer account has been approved. You can now access the dashboard.',
                    'system'
                )
            except Exception as e:
                # Log the notification error but don't fail the approval
                print(f"Failed to send notification: {str(e)}")
            
            messages.success(request, f'Placement officer {officer.user.get_full_name()} has been approved.')
        except Exception as e:
            messages.error(request, f'Error approving placement officer: {str(e)}')
    return redirect('placement_officer_management')

@staff_member_required
def reject_placement_officer(request, officer_id):
    if request.method == 'POST':
        try:
            officer = get_object_or_404(PlacementOfficer, id=officer_id)
            officer.is_approved = False
            officer.is_rejected = True
            officer.save()
            
            # Send notification to the placement officer
            try:
                send_notification(
                    officer.user,
                    'Account Rejected',
                    'Your placement officer account has been rejected. Please contact the administrator for more information.',
                    'system'
                )
            except Exception as e:
                # Log the notification error but don't fail the rejection
                print(f"Failed to send notification: {str(e)}")
            
            messages.success(request, f'Placement officer {officer.user.get_full_name()} has been rejected.')
        except Exception as e:
            messages.error(request, f'Error rejecting placement officer: {str(e)}')
    return redirect('placement_officer_management')
