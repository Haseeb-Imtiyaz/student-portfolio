from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('employer', 'Employer'),
        ('placement_officer', 'Placement Officer'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_token_created_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Instant'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest')
        ],
        default='instant'
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def generate_email_verification_token(self):
        import secrets
        import datetime
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_token_created_at = datetime.datetime.now()
        self.save()
        return self.email_verification_token

    def verify_email(self, token):
        if (self.email_verification_token == token and 
            self.email_verification_token_created_at and 
            (datetime.datetime.now() - self.email_verification_token_created_at).days < 1):
            self.is_email_verified = True
            self.email_verification_token = None
            self.email_verification_token_created_at = None
            self.save()
            return True
        return False

class College(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200)
    duration = models.IntegerField()  # in years
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Personal Details
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    
    # College Information
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    specialization = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField()
    semester = models.IntegerField(null=True, blank=True)
    expected_graduation_year = models.IntegerField(null=True, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Profile Completion
    profile_completion = models.IntegerField(default=0)
    
    # Resume related fields
    resume_template = models.ForeignKey('ResumeTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_version = models.IntegerField(default=1)
    resume_last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.college.name}"
    
    def calculate_profile_completion(self):
        total_fields = 15  # Total number of required fields
        completed_fields = 0
        
        # Check each required field
        if self.profile_picture: completed_fields += 1
        if self.date_of_birth: completed_fields += 1
        if self.gender: completed_fields += 1
        if self.address: completed_fields += 1
        if self.city: completed_fields += 1
        if self.state: completed_fields += 1
        if self.pin_code: completed_fields += 1
        if self.college: completed_fields += 1
        if self.course: completed_fields += 1
        if self.specialization: completed_fields += 1
        if self.year_of_study: completed_fields += 1
        if self.semester: completed_fields += 1
        if self.phone_number: completed_fields += 1
        if self.linkedin_url: completed_fields += 1
        if self.github_url: completed_fields += 1
        
        self.profile_completion = int((completed_fields / total_fields) * 100)
        self.save()
        return self.profile_completion
    
    def get_academic_performance(self):
        academic_records = self.academic_records.all()
        if not academic_records:
            return 0
            
        total_marks = sum(record.marks_obtained for record in academic_records)
        total_max_marks = sum(record.max_marks for record in academic_records)
        return (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
    
    def get_project_stats(self):
        projects = self.projects.all()
        total = projects.count()
        completed = projects.filter(end_date__lte=timezone.now()).count()
        ongoing = projects.filter(start_date__lte=timezone.now(), end_date__gt=timezone.now()).count()
        upcoming = projects.filter(start_date__gt=timezone.now()).count()
        
        return {
            'total': total,
            'completed': completed,
            'ongoing': ongoing,
            'upcoming': upcoming,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
    
    def get_contest_stats(self):
        contests = self.contests.all()
        total = contests.count()
        technical = contests.filter(category='technical').count()
        non_technical = contests.filter(category='non-technical').count()
        wins = contests.filter(outcome='winner').count()
        runner_ups = contests.filter(outcome='runner_up').count()
        
        return {
            'total': total,
            'technical': technical,
            'non_technical': non_technical,
            'wins': wins,
            'runner_ups': runner_ups,
            'success_rate': ((wins + runner_ups) / total * 100) if total > 0 else 0
        }
    
    def get_job_stats(self):
        applications = self.job_applications.all()
        total = applications.count()
        applied = applications.filter(status='applied').count()
        under_review = applications.filter(status='under_review').count()
        shortlisted = applications.filter(status='shortlisted').count()
        rejected = applications.filter(status='rejected').count()
        hired = applications.filter(status='hired').count()
        
        return {
            'total': total,
            'applied': applied,
            'under_review': under_review,
            'shortlisted': shortlisted,
            'rejected': rejected,
            'hired': hired,
            'success_rate': (hired / total * 100) if total > 0 else 0
        }

class AcademicRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='academic_records')
    semester = models.IntegerField()
    subject_name = models.CharField(max_length=200)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    institution = models.CharField(max_length=200)
    year_of_completion = models.IntegerField()
    report_card = models.FileField(upload_to='report_cards/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - Sem {self.semester} - {self.subject_name}"
    
    @classmethod
    def calculate_semester_gpa(cls, student_profile, semester):
        """Calculate GPA for a specific semester"""
        records = cls.objects.filter(student=student_profile, semester=semester)
        if not records:
            return 0.0
            
        total_marks = sum(record.marks_obtained for record in records)
        total_max_marks = sum(record.max_marks for record in records if record.max_marks)
        
        if total_max_marks == 0:
            return 0.0
            
        # Convert to GPA (assuming 10-point scale)
        gpa = (total_marks / total_max_marks) * 10
        return round(gpa, 2)
    
    @classmethod
    def calculate_cgpa(cls, student_profile):
        """Calculate Cumulative GPA across all semesters"""
        records = cls.objects.filter(student=student_profile)
        if not records:
            return 0.0
            
        # Get unique semesters
        semesters = set(record.semester for record in records)
        if not semesters:
            return 0.0
            
        # Calculate average of all semester GPAs
        total_gpa = sum(cls.calculate_semester_gpa(student_profile, semester) for semester in semesters)
        cgpa = total_gpa / len(semesters)
        return round(cgpa, 2)

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('academic', 'Academic'),
        ('personal', 'Personal'),
        ('professional', 'Professional'),
        ('research', 'Research'),
        ('other', 'Other')
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='personal')
    technologies = models.CharField(max_length=500)
    role = models.CharField(max_length=200, help_text="Your role in the project", default='Developer')
    tools_used = models.CharField(max_length=500, help_text="Tools and technologies used in the project", default='Not specified')
    team_size = models.IntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"

    class Meta:
        ordering = ['-created_at']

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/')
    file_type = models.CharField(max_length=20, choices=[
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('other', 'Other')
    ])
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.file.name} - {self.project.title}"

    def filename(self):
        return os.path.basename(self.file.name)

class Contest(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='contests')
    event_name = models.CharField(max_length=200)
    organized_by = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=[
        ('technical', 'Technical'),
        ('non-technical', 'Non-Technical')
    ])
    description = models.TextField()
    date_of_participation = models.DateField()
    outcome = models.CharField(max_length=50, choices=[
        ('participation', 'Participation'),
        ('winner', 'Winner'),
        ('runner_up', 'Runner-Up')
    ])
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)
    video_link = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.event_name} - {self.student.user.get_full_name()}"

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.company_name} - {self.user.email}"

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('internship', 'Internship'),
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract')
    ]
    
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    experience_required = models.CharField(max_length=100, default='0-1 years')
    salary_range = models.CharField(max_length=100, default='Not Specified')
    description = models.TextField()
    skills_required = models.CharField(max_length=500)
    eligibility = models.TextField()
    openings = models.IntegerField(default=1)
    last_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.employer.company_name}"

    class Meta:
        ordering = ['-created_at']

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired')
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='job_applications')
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    availability_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    interview_date = models.DateTimeField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} applied for {self.job.title}"

    class Meta:
        ordering = ['-applied_date']

class JobBookmark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='bookmarked_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} bookmarked {self.job.title}"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('programming', 'Programming'),
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('database', 'Database'),
        ('cloud', 'Cloud'),
        ('devops', 'DevOps'),
        ('design', 'Design'),
        ('other', 'Other')
    ])

    def __str__(self):
        return self.name

class StudentSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ])

    class Meta:
        unique_together = ('student', 'skill')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.skill.name}"

class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    template_path = models.CharField(max_length=255, default='resumes/professional_classic.html')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('job_alert', 'Job Alert'),
            ('application_update', 'Application Update'),
            ('profile_reminder', 'Profile Reminder'),
            ('system', 'System Notification')
        ]
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class PlacementOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='placement_officer')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='placement_officers')
    designation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.college.name}"
