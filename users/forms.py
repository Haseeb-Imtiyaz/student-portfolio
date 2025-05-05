from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import User, StudentProfile, EmployerProfile, AcademicRecord, Project, ProjectFile, Contest, Job, JobApplication, Skill, StudentSkill, ResumeTemplate, Notification, College, Course, PlacementOfficer

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'profile_picture', 'date_of_birth', 'gender', 'address', 'city', 
            'state', 'pin_code', 'college', 'course', 'specialization',
            'year_of_study', 'semester', 'expected_graduation_year', 'phone_number',
            'linkedin_url', 'github_url', 'portfolio_url', 'bio'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional except college, course, and year_of_study
        for field in self.fields:
            if field not in ['college', 'course', 'year_of_study']:
                self.fields[field].required = False

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_website', 'company_description', 
                 'company_logo', 'industry', 'company_size', 'location']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

class AcademicRecordForm(forms.ModelForm):
    class Meta:
        model = AcademicRecord
        fields = [
            'semester', 'subject_name', 'marks_obtained', 'max_marks',
            'institution', 'year_of_completion', 'report_card'
        ]
        widgets = {
            'year_of_completion': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'project_type', 'technologies',
            'role', 'tools_used', 'team_size', 'start_date',
            'end_date', 'project_url', 'github_url'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'technologies': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, React'}),
            'role': forms.TextInput(attrs={'placeholder': 'e.g., Frontend Developer, Project Lead'}),
            'tools_used': forms.TextInput(attrs={'placeholder': 'e.g., VS Code, Git, Docker'}),
            'project_url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
            'github_url': forms.URLInput(attrs={'placeholder': 'https://github.com/username/repo'}),
        }
        labels = {
            'title': 'Project Title',
            'description': 'Project Description',
            'project_type': 'Project Type',
            'technologies': 'Technologies Used',
            'role': 'Your Role',
            'tools_used': 'Tools Used',
            'team_size': 'Team Size',
            'start_date': 'Start Date',
            'end_date': 'End Date (Optional)',
            'project_url': 'Project URL (Optional)',
            'github_url': 'GitHub Repository URL (Optional)',
        }
        help_texts = {
            'technologies': 'Enter comma-separated list of technologies used in the project',
            'description': 'Provide a detailed description of your project',
            'role': 'Describe your role and responsibilities in the project',
            'tools_used': 'List the tools and software used in the project',
            'end_date': 'Leave blank if the project is ongoing',
        }

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'file_type', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Brief description of the file'})
        }

class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = [
            'event_name', 'organized_by', 'category', 'description',
            'date_of_participation', 'outcome', 'certificate', 'video_link'
        ]
        widgets = {
            'date_of_participation': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'job_type', 'location', 'duration',
            'stipend_ctc', 'description', 'skills_required',
            'eligibility_course', 'eligibility_branch', 'eligibility_year',
            'openings', 'last_date'
        ]
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'duration': forms.TextInput(attrs={'placeholder': 'e.g., 3 months'}),
            'stipend_ctc': forms.TextInput(attrs={'placeholder': 'e.g., 30k/month or 6 LPA'}),
            'eligibility_course': forms.TextInput(attrs={'placeholder': 'e.g., B.Tech, M.Tech'}),
            'eligibility_branch': forms.TextInput(attrs={'placeholder': 'e.g., CSE, ECE'}),
            'eligibility_year': forms.TextInput(attrs={'placeholder': 'e.g., 3rd year, 4th year'}),
        }
        labels = {
            'title': 'Job Title',
            'job_type': 'Employment Type',
            'location': 'Job Location',
            'duration': 'Duration (For Internship)',
            'stipend_ctc': 'Stipend/CTC',
            'description': 'Job Description',
            'skills_required': 'Required Skills',
            'eligibility_course': 'Eligible Course',
            'eligibility_branch': 'Eligible Branch',
            'eligibility_year': 'Eligible Year',
            'openings': 'Number of Openings',
            'last_date': 'Application Deadline'
        }
        help_texts = {
            'skills_required': 'Select multiple skills required for this position',
            'duration': 'Required only for internship positions',
            'stipend_ctc': 'For internships: Monthly stipend, For full-time: Annual CTC',
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'portfolio_url', 'linkedin_url', 'github_url', 'availability_date']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us why you are the best fit for this position...'}),
            'portfolio_url': forms.URLInput(attrs={'placeholder': 'Your portfolio website URL'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'Your LinkedIn profile URL'}),
            'github_url': forms.URLInput(attrs={'placeholder': 'Your GitHub profile URL'}),
            'availability_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'resume': 'Resume/CV',
            'cover_letter': 'Cover Letter',
            'portfolio_url': 'Portfolio URL',
            'linkedin_url': 'LinkedIn Profile',
            'github_url': 'GitHub Profile',
            'availability_date': 'Available From',
        }
        help_texts = {
            'resume': 'Upload your latest resume in PDF or DOC format',
            'cover_letter': 'Write a compelling cover letter explaining your interest in the position',
            'portfolio_url': 'Share your portfolio website if available',
            'linkedin_url': 'Share your LinkedIn profile for additional information',
            'github_url': 'Share your GitHub profile if you have one',
            'availability_date': 'When can you start working?',
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category']

class StudentSkillForm(forms.ModelForm):
    class Meta:
        model = StudentSkill
        fields = ['skill', 'proficiency']

class ResumeTemplateForm(forms.ModelForm):
    class Meta:
        model = ResumeTemplate
        fields = ['name', 'description', 'template_path', 'is_active']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type']

class CollegeForm(forms.ModelForm):
    class Meta:
        model = College
        fields = [
            'name', 'location', 'website', 'contact_email',
            'contact_phone'
        ]

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'duration', 'description']

class PlacementOfficerForm(forms.ModelForm):
    class Meta:
        model = PlacementOfficer
        fields = ['college', 'designation', 'phone_number']

class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email_notifications',
            'push_notifications',
            'notification_frequency'
        ]
        widgets = {
            'notification_frequency': forms.Select(choices=[
                ('immediate', 'Immediate'),
                ('daily', 'Daily Digest'),
                ('weekly', 'Weekly Digest')
            ])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
            if isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs['class'] = 'form-check-input'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'

class JobFilterForm(forms.Form):
    type = forms.ChoiceField(
        choices=Job.JOB_TYPE_CHOICES,
        required=False,
        label='Job Type'
    )
    location = forms.CharField(
        required=False,
        label='Location'
    )
    experience = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('Entry Level', 'Entry Level'),
            ('Mid Level', 'Mid Level'),
            ('Senior Level', 'Senior Level'),
            ('Expert', 'Expert')
        ],
        required=False,
        label='Experience Level'
    )
    salary = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('0-3 LPA', '0-3 LPA'),
            ('3-6 LPA', '3-6 LPA'),
            ('6-10 LPA', '6-10 LPA'),
            ('10-15 LPA', '10-15 LPA'),
            ('15+ LPA', '15+ LPA')
        ],
        required=False,
        label='Salary Range'
    )
    skills = forms.CharField(
        required=False,
        label='Skills'
    ) 