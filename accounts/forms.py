from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, EmployerProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'user_type', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['college_name', 'course', 'specialization', 'year_of_study', 
                 'profile_picture', 'linkedin_url', 'github_url', 'portfolio_url', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_website', 'company_description', 
                 'company_logo', 'industry', 'company_size', 'location']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number'] 