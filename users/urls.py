from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/student/create/', views.create_student_profile, name='create_student_profile'),
    path('profile/employer/create/', views.create_employer_profile, name='create_employer_profile'),
    path('profile/placement-officer/create/', views.create_placement_officer_profile, name='create_placement_officer_profile'),
    
    # Dashboard URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/student-management/', views.student_management, name='student_management'),
    path('admin/student/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin/employer-management/', views.employer_management, name='employer_management'),
    path('admin/master-config/', views.master_config, name='master_config'),
    path('admin/master-config/college/add/', views.add_college, name='add_college'),
    path('admin/master-config/college/<int:college_id>/edit/', views.edit_college, name='edit_college'),
    path('admin/master-config/course/add/', views.add_course, name='add_course'),
    path('admin/master-config/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('admin/master-config/skill/add/', views.add_skill, name='add_skill'),
    path('admin/master-config/skill/<int:skill_id>/edit/', views.edit_skill, name='edit_skill'),
    path('admin/master-config/template/add/', views.add_template, name='add_template'),
    path('admin/master-config/template/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('admin/communication/', views.communication_panel, name='communication_panel'),
    path('admin/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/employer/<int:employer_id>/', views.employer_detail, name='employer_detail'),
    path('admin/verify-employer/<int:employer_id>/', views.verify_employer, name='admin_verify_employer'),
    path('admin/delete-employer/<int:employer_id>/', views.delete_employer, name='admin_delete_employer'),
    path('admin/create-announcement/', views.create_announcement, name='admin_create_announcement'),
    path('admin/edit-announcement/<int:announcement_id>/', views.edit_announcement, name='admin_edit_announcement'),
    path('admin/delete-announcement/<int:announcement_id>/', views.delete_announcement, name='admin_delete_announcement'),
    
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
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.job_apply, name='job_apply'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('jobs/<int:job_id>/bookmark/', views.toggle_job_bookmark, name='toggle_job_bookmark'),
    path('jobs/bookmarked/', views.bookmarked_jobs, name='bookmarked_jobs'),
    
    # Job Application URLs
    path('applications/', views.job_applications, name='job_applications'),
    path('applications/<int:job_id>/', views.employer_job_applications, name='employer_job_applications'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    
    # Resume URLs
    path('resume/templates/', views.resume_templates, name='resume_templates'),
    path('resume/generate/', views.generate_resume, name='generate_resume'),
    path('resume/generate/<int:template_id>/', views.generate_resume, name='generate_resume_with_template'),
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
    
    # Placement Officer URLs
    path('placement-officer/dashboard/', views.placement_officer_dashboard, name='placement_officer_dashboard'),
    path('placement-officer/students/', views.student_list, name='student_list'),
    path('placement-officer/students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('placement-officer/download-report/', views.download_student_report, name='download_student_report'),
    
    # Placement Officer Management URLs
    path('admin/placement-officers/', views.placement_officer_management, name='placement_officer_management'),
    path('admin/placement-officers/<int:officer_id>/approve/', views.approve_placement_officer, name='approve_placement_officer'),
    path('admin/placement-officers/<int:officer_id>/reject/', views.reject_placement_officer, name='reject_placement_officer'),
] 