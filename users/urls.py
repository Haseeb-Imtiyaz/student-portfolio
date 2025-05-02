from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/student/create/', views.create_student_profile, name='create_student_profile'),
    path('profile/employer/create/', views.create_employer_profile, name='create_employer_profile'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/employer/', views.employer_dashboard, name='employer_dashboard'),
    
    # Academic Records URLs
    path('academic-records/', views.academic_records, name='academic_records'),
    
    # Project URLs
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/add-file/', views.add_project_file, name='add_project_file'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/files/<int:file_id>/delete/', views.delete_project_file, name='delete_project_file'),
    
    # Contest URLs
    path('contests/', views.contests, name='contests'),
    path('contests/<int:contest_id>/delete/', views.delete_contest, name='delete_contest'),
    
    # Job URLs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.job_apply, name='job_apply'),
    path('jobs/<int:job_id>/bookmark/', views.toggle_job_bookmark, name='toggle_job_bookmark'),
    path('jobs/bookmarked/', views.bookmarked_jobs, name='bookmarked_jobs'),
    path('jobs/applications/', views.job_applications, name='job_applications'),
    
    # Resume URLs
    path('resume/templates/', views.resume_templates, name='resume_templates'),
    path('resume/generate/<int:template_id>/', views.generate_resume, name='generate_resume'),
    path('resume/download/', views.download_resume, name='download_resume'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
    
    # Password Reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # Skill related URLs
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/add/', views.add_skill, name='add_skill'),
    
    # College and Course related URLs
    path('colleges/', views.college_list, name='college_list'),
    path('courses/', views.course_list, name='course_list'),
    
    # Placement officers
    path('placement-officers/', views.placement_officers, name='placement_officers'),
] 