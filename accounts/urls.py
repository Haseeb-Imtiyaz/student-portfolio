from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/student/create/', views.create_student_profile, name='create_student_profile'),
    path('profile/employer/create/', views.create_employer_profile, name='create_employer_profile'),
] 