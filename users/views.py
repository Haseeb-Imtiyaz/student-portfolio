from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegistrationForm, StudentProfileForm, EmployerProfileForm, UserUpdateForm, AcademicRecordForm, ProjectForm, ProjectFileForm, ContestForm, JobForm, JobApplicationForm, SkillForm, StudentSkillForm, ResumeTemplateForm, NotificationForm, CollegeForm, CourseForm, PlacementOfficerForm, NotificationSettingsForm
from .models import StudentProfile, EmployerProfile, AcademicRecord, Project, Contest, Job, JobApplication, Skill, StudentSkill, ResumeTemplate, Notification, College, Course, PlacementOfficer, JobBookmark, ProjectFile, User
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if request.user.user_type == 'student':
            p_form = StudentProfileForm(request.POST, request.FILES, instance=request.user.student_profile)
        else:
            p_form = EmployerProfileForm(request.POST, request.FILES, instance=request.user.employer_profile)
            
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        if request.user.user_type == 'student':
            p_form = StudentProfileForm(instance=request.user.student_profile)
        else:
            p_form = EmployerProfileForm(instance=request.user.employer_profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/update_profile.html', context)

@login_required
def profile(request):
    try:
        if request.user.user_type == 'student':
            profile = request.user.student_profile
            profile.calculate_profile_completion()  # Calculate profile completion
            context = {
                'profile': profile,
                'profile_completion': profile.profile_completion,
            }
        else:
            profile = request.user.employer_profile
            context = {
                'profile': profile,
            }
    except (StudentProfile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.info(request, 'Please create your profile first.')
        return redirect('create_student_profile' if request.user.user_type == 'student' else 'create_employer_profile')
    
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
    context = {
        'employer_profile': employer_profile,
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
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    student_profile = request.user.student_profile
    applications = student_profile.job_applications.all()
    job_stats = student_profile.get_job_stats()
    
    # Filter applications by status if specified
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    context = {
        'applications': applications,
        'job_stats': job_stats,
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
        
        # Get the template content
        template_path = template.template_path
        
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
        
        item_title_style = ParagraphStyle(
            'ItemTitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=5,
            textColor=HexColor('#333333')
        )
        
        item_subtitle_style = ParagraphStyle(
            'ItemSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=5,
            textColor=HexColor('#666666'),
            fontName='Helvetica-Oblique'
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
            user.is_email_verified = True
            user.save()
            messages.success(request, 'Your email has been verified successfully!')
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
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    jobs = Job.objects.all()
    
    # Advanced search filters
    job_type = request.GET.get('type')
    location = request.GET.get('location')
    experience = request.GET.get('experience')
    salary_range = request.GET.get('salary')
    skills = request.GET.get('skills')
    company = request.GET.get('company')
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if experience:
        jobs = jobs.filter(experience_required__icontains=experience)
    if salary_range:
        jobs = jobs.filter(salary_range__icontains=salary_range)
    if skills:
        jobs = jobs.filter(skills_required__icontains=skills)
    if company:
        jobs = jobs.filter(employer__company_name__icontains=company)
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'job_types': Job.JOB_TYPE_CHOICES,
        'experience_levels': ['Entry Level', 'Mid Level', 'Senior Level', 'Expert'],
        'salary_ranges': ['0-3 LPA', '3-6 LPA', '6-10 LPA', '10-15 LPA', '15+ LPA'],
    }
    return render(request, 'users/job_list.html', context)

@login_required
def job_detail(request, job_id):
    if not hasattr(request.user, 'student_profile'):
        return redirect('create_student_profile')
    
    job = get_object_or_404(Job, id=job_id)
    is_bookmarked = JobBookmark.objects.filter(user=request.user, job=job).exists()
    
    context = {
        'job': job,
        'is_bookmarked': is_bookmarked
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
    templates = ResumeTemplate.objects.all()
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
