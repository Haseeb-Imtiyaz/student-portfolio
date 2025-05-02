import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portfolio.settings')
django.setup()

from users.models import College, Course

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

if __name__ == '__main__':
    setup_initial_data() 