import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portfolio.settings')
django.setup()

from users.models import College, Course, User, StudentProfile, EmployerProfile
from django.utils import timezone

def setup_initial_data():
    # Create Colleges
    colleges = [
        {
            'name': 'Mangalore Institute of Technology and Engineering',
            'location': 'Moodabidri, Karnataka',
            'website': 'https://mite.ac.in',
            'contact_email': 'info@mite.ac.in',
            'contact_phone': '08258-262695',
        },
        {
            'name': 'National Institute of Technology Karnataka',
            'location': 'Surathkal, Karnataka',
            'website': 'https://www.nitk.ac.in',
            'contact_email': 'info@nitk.ac.in',
            'contact_phone': '0824-2474000',
        },
    ]

    for college_data in colleges:
        college, created = College.objects.get_or_create(
            name=college_data['name'],
            defaults=college_data
        )
        print(f'{"Created" if created else "Already exists"}: {college.name}')

    # Create Courses
    courses = [
        {
            'name': 'Computer Science and Engineering',
            'duration': 4,
            'description': 'B.E. in Computer Science and Engineering',
        },
        {
            'name': 'Information Science and Engineering',
            'duration': 4,
            'description': 'B.E. in Information Science and Engineering',
        },
        {
            'name': 'Electronics and Communication Engineering',
            'duration': 4,
            'description': 'B.E. in Electronics and Communication Engineering',
        },
        {
            'name': 'Mechanical Engineering',
            'duration': 4,
            'description': 'B.E. in Mechanical Engineering',
        },
        {
            'name': 'Civil Engineering',
            'duration': 4,
            'description': 'B.E. in Civil Engineering',
        },
    ]

    for course_data in courses:
        course, created = Course.objects.get_or_create(
            name=course_data['name'],
            defaults=course_data
        )
        print(f'{"Created" if created else "Already exists"}: {course.name}')

def create_dummy_users():
    # Get a college and course for students
    college = College.objects.first()
    course = Course.objects.first()
    
    # Realistic student data
    students = [
        {'username': 'alice', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice.johnson@example.com'},
        {'username': 'bob', 'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob.smith@example.com'},
        {'username': 'charlie', 'first_name': 'Charlie', 'last_name': 'Lee', 'email': 'charlie.lee@example.com'},
        {'username': 'diana', 'first_name': 'Diana', 'last_name': 'Patel', 'email': 'diana.patel@example.com'},
        {'username': 'ethan', 'first_name': 'Ethan', 'last_name': 'Brown', 'email': 'ethan.brown@example.com'},
    ]
    for s in students:
        user, created = User.objects.get_or_create(
            username=s['username'],
            defaults={
                'email': s['email'],
                'user_type': 'student',
                'is_verified': True,
                'is_email_verified': True,
                'first_name': s['first_name'],
                'last_name': s['last_name'],
                'date_joined': timezone.now(),
            }
        )
        if created:
            user.set_password('password@123')
            user.save()
            StudentProfile.objects.create(
                user=user,
                college=college,
                course=course,
                year_of_study=2,
                semester=3,
                expected_graduation_year=2026,
            )
            print(f'Created student: {s["first_name"]} {s["last_name"]}')
        else:
            print(f'Student already exists: {s["first_name"]} {s["last_name"]}')

    # Realistic employer data
    employers = [
        {'username': 'techcorp', 'company_name': 'TechCorp', 'email': 'hr@techcorp.com'},
        {'username': 'healthplus', 'company_name': 'HealthPlus', 'email': 'jobs@healthplus.com'},
        {'username': 'finwise', 'company_name': 'FinWise', 'email': 'careers@finwise.com'},
        {'username': 'eduspark', 'company_name': 'EduSpark', 'email': 'hr@eduspark.com'},
        {'username': 'greenworks', 'company_name': 'GreenWorks', 'email': 'jobs@greenworks.com'},
    ]
    for e in employers:
        user, created = User.objects.get_or_create(
            username=e['username'],
            defaults={
                'email': e['email'],
                'user_type': 'employer',
                'is_verified': True,
                'is_email_verified': True,
                'date_joined': timezone.now(),
            }
        )
        if created:
            user.set_password('password@123')
            user.save()
            EmployerProfile.objects.create(
                user=user,
                company_name=e['company_name'],
                company_website=f'https://{e["company_name"].lower()}.com',
                company_description=f'{e["company_name"]} is a leading company in its field.',
                industry='IT',
                company_size='50-100',
                location='City',
            )
            print(f'Created employer: {e["company_name"]}')
        else:
            print(f'Employer already exists: {e["company_name"]}')

if __name__ == '__main__':
    setup_initial_data()
    create_dummy_users() 