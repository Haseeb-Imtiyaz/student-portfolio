from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import (
    User, StudentProfile, EmployerProfile, Job, JobApplication,
    JobBookmark, Project, AcademicRecord, Skill, StudentSkill,
    College, Course, ResumeTemplate, Notification
)
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Creates dummy data for testing'

    def handle(self, *args, **options):
        # Create skills
        skills = [
            'Python', 'Django', 'JavaScript', 'React', 'Node.js',
            'Java', 'Spring Boot', 'SQL', 'MongoDB', 'AWS',
            'Docker', 'Kubernetes', 'Machine Learning', 'Data Science',
            'UI/UX Design', 'DevOps', 'Git', 'CI/CD', 'REST API',
            'GraphQL', 'TypeScript', 'Angular', 'Vue.js', 'Flutter',
            'Swift', 'Kotlin', 'TensorFlow', 'PyTorch', 'Big Data',
            'Cloud Computing', 'Cybersecurity', 'Blockchain'
        ]
        
        skill_objects = []
        for skill_name in skills:
            skill = Skill.objects.create(
                name=skill_name,
                category=random.choice(['programming', 'web', 'mobile', 'database', 'cloud', 'devops', 'design', 'other'])
            )
            skill_objects.append(skill)

        # Create colleges with manually curated list
        colleges = [
            {
                'name': 'Mangalore Institute of Technology and Engineering',
                'location': 'Mangalore',
                'website': 'https://www.mite.ac.in',
                'contact_email': 'info@mite.ac.in',
                'contact_phone': '+91-824-2274111'
            },
            {
                'name': 'National Institute of Technology Karnataka',
                'location': 'Surathkal',
                'website': 'https://www.nitk.ac.in',
                'contact_email': 'info@nitk.ac.in',
                'contact_phone': '+91-824-2474000'
            },
            {
                'name': 'Manipal Institute of Technology',
                'location': 'Manipal',
                'website': 'https://manipal.edu/mit.html',
                'contact_email': 'info@manipal.edu',
                'contact_phone': '+91-820-2922400'
            },
            {
                'name': 'St. Joseph Engineering College',
                'location': 'Mangalore',
                'website': 'https://www.sjec.ac.in',
                'contact_email': 'info@sjec.ac.in',
                'contact_phone': '+91-824-2263755'
            },
            {
                'name': 'Sahyadri College of Engineering and Management',
                'location': 'Mangalore',
                'website': 'https://www.sahyadri.edu.in',
                'contact_email': 'info@sahyadri.edu.in',
                'contact_phone': '+91-824-2277222'
            },
            {
                'name': 'Canara Engineering College',
                'location': 'Mangalore',
                'website': 'https://www.canaraengineering.in',
                'contact_email': 'info@canaraengineering.in',
                'contact_phone': '+91-824-2274111'
            },
            {
                'name': 'Srinivas Institute of Technology',
                'location': 'Mangalore',
                'website': 'https://www.srinivasgroup.com',
                'contact_email': 'info@srinivasgroup.com',
                'contact_phone': '+91-824-2274111'
            },
            {
                'name': 'Alva\'s Institute of Engineering and Technology',
                'location': 'Moodbidri',
                'website': 'https://www.alvas.org',
                'contact_email': 'info@alvas.org',
                'contact_phone': '+91-8258-237241'
            },
            {
                'name': 'P.A. College of Engineering',
                'location': 'Mangalore',
                'website': 'https://www.pace.edu.in',
                'contact_email': 'info@pace.edu.in',
                'contact_phone': '+91-824-2263755'
            },
            {
                'name': 'Yenepoya Institute of Technology',
                'location': 'Moodbidri',
                'website': 'https://www.yenepoya.edu.in',
                'contact_email': 'info@yenepoya.edu.in',
                'contact_phone': '+91-8258-237241'
            }
        ]
        
        college_objects = []
        for college_data in colleges:
            college = College.objects.create(
                name=college_data['name'],
                location=college_data['location'],
                website=college_data['website'],
                contact_email=college_data['contact_email'],
                contact_phone=college_data['contact_phone']
            )
            college_objects.append(college)

        # Create courses
        courses = [
            {'name': 'Computer Science and Engineering', 'duration': 4},
            {'name': 'Electronics and Communication Engineering', 'duration': 4},
            {'name': 'Mechanical Engineering', 'duration': 4},
            {'name': 'Electrical Engineering', 'duration': 4},
            {'name': 'Civil Engineering', 'duration': 4},
            {'name': 'Information Technology', 'duration': 4},
            {'name': 'Artificial Intelligence', 'duration': 4},
            {'name': 'Data Science', 'duration': 4},
            {'name': 'Business Administration', 'duration': 3},
            {'name': 'Computer Applications', 'duration': 3}
        ]
        
        course_objects = []
        for course_data in courses:
            course = Course.objects.create(
                name=course_data['name'],
                duration=course_data['duration'],
                description=f"Bachelor's degree in {course_data['name']}"
            )
            course_objects.append(course)

        # Create employers and jobs
        companies = [
            {'name': 'Google', 'industry': 'Technology'},
            {'name': 'Microsoft', 'industry': 'Technology'},
            {'name': 'Amazon', 'industry': 'E-commerce'},
            {'name': 'Flipkart', 'industry': 'E-commerce'},
            {'name': 'Infosys', 'industry': 'IT Services'},
            {'name': 'TCS', 'industry': 'IT Services'},
            {'name': 'Wipro', 'industry': 'IT Services'},
            {'name': 'HCL', 'industry': 'IT Services'},
            {'name': 'Zomato', 'industry': 'Food Delivery'},
            {'name': 'Swiggy', 'industry': 'Food Delivery'}
        ]

        job_titles = [
            'Software Engineer', 'Frontend Developer', 'Backend Developer',
            'Full Stack Developer', 'Data Scientist', 'Machine Learning Engineer',
            'DevOps Engineer', 'Cloud Engineer', 'Product Manager',
            'UI/UX Designer', 'Mobile App Developer', 'Quality Assurance Engineer',
            'Business Analyst', 'Technical Writer', 'System Administrator'
        ]

        for company_data in companies:
            # Create employer user
            employer_user = User.objects.create_user(
                username=f"{company_data['name'].lower()}",
                email=f"hr@{company_data['name'].lower()}.com",
                password='password123',
                user_type='employer',
                first_name=company_data['name'],
                last_name='HR'
            )

            # Create employer profile
            employer_profile = EmployerProfile.objects.create(
                user=employer_user,
                company_name=company_data['name'],
                company_website=f"https://www.{company_data['name'].lower()}.com",
                company_description=f"Leading {company_data['industry']} company",
                industry=company_data['industry'],
                company_size=random.choice(['1-50', '51-200', '201-500', '501-1000', '1000+']),
                location=random.choice(['Bangalore', 'Hyderabad', 'Pune', 'Mumbai', 'Delhi', 'Chennai'])
            )

            # Create jobs for each employer
            for _ in range(random.randint(3, 7)):
                job = Job.objects.create(
                    employer=employer_profile,
                    title=random.choice(job_titles),
                    job_type=random.choice(['internship', 'full_time', 'contract']),
                    location=random.choice(['remote', 'on_site', 'hybrid']),
                    duration='6 months' if random.choice([True, False]) else None,
                    stipend_ctc=random.choice(['30k/month', '40k/month', '50k/month', '6 LPA', '8 LPA', '10 LPA', '12 LPA']),
                    description=f"Looking for a {random.choice(job_titles)} to join our team.",
                    eligibility_course=random.choice(['Any', 'B.Tech', 'M.Tech', 'BCA', 'MCA']),
                    eligibility_branch=random.choice(['Any', 'CSE', 'ECE', 'IT', 'EEE']),
                    eligibility_year=random.choice(['Any', '3rd year', '4th year', 'Final year']),
                    openings=random.randint(1, 5),
                    last_date=timezone.now() + timedelta(days=random.randint(10, 30))
                )
                
                # Add random skills to job
                job.skills_required.add(*random.sample(skill_objects, random.randint(3, 7)))

        # Create students
        student_data = [
            {'first': 'Aarav', 'last': 'Sharma'},
            {'first': 'Aditi', 'last': 'Patel'},
            {'first': 'Akshay', 'last': 'Singh'},
            {'first': 'Ananya', 'last': 'Kumar'},
            {'first': 'Arjun', 'last': 'Gupta'},
            {'first': 'Diya', 'last': 'Verma'},
            {'first': 'Ishaan', 'last': 'Malhotra'},
            {'first': 'Kavya', 'last': 'Choudhary'},
            {'first': 'Rahul', 'last': 'Agarwal'},
            {'first': 'Sanya', 'last': 'Reddy'}
        ]

        for student in student_data:
            first_name = student['first']
            last_name = student['last']
            username = f"{first_name.lower()}{last_name.lower()}123"
            
            # Create student user
            student_user = User.objects.create_user(
                username=username,
                email=f"{username}@gmail.com",
                password='password123',
                user_type='student',
                first_name=first_name,
                last_name=last_name
            )

            # Create student profile
            student_profile = StudentProfile.objects.create(
                user=student_user,
                college=random.choice(college_objects),
                course=random.choice(course_objects),
                specialization=random.choice(['AI/ML', 'Cloud Computing', 'Cyber Security', 'Data Science', 'Web Development']),
                year_of_study=random.randint(1, 4),
                semester=random.randint(1, 8),
                expected_graduation_year=datetime.now().year + random.randint(0, 3),
                phone_number=f"+91-{random.randint(1000000000, 9999999999)}",
                linkedin_url=f"https://linkedin.com/in/{username}",
                github_url=f"https://github.com/{username}",
                portfolio_url=f"https://{username}.com",
                bio=f"Passionate {random.choice(course_objects).name} student"
            )

            # Add random skills to student
            for skill in random.sample(skill_objects, random.randint(5, 10)):
                StudentSkill.objects.create(
                    student=student_profile,
                    skill=skill,
                    proficiency=random.choice(['beginner', 'intermediate', 'advanced', 'expert'])
                )

            # Create academic records
            for semester in range(1, student_profile.semester + 1):
                AcademicRecord.objects.create(
                    student=student_profile,
                    semester=semester,
                    subject_name=f"Subject {semester}",
                    marks_obtained=random.uniform(60, 95),
                    max_marks=100,
                    institution=student_profile.college.name,
                    year_of_completion=datetime.now().year - (student_profile.semester - semester)
                )

            # Create projects
            for _ in range(random.randint(2, 5)):
                Project.objects.create(
                    student=student_profile,
                    title=f"Project {random.randint(1, 100)}",
                    description=f"Description for project {random.randint(1, 100)}",
                    project_type=random.choice(['academic', 'personal', 'professional', 'research']),
                    technologies=random.choice(['Python, Django, React', 'Java, Spring Boot', 'JavaScript, Node.js', 'Python, Machine Learning']),
                    role=random.choice(['Developer', 'Team Lead', 'Project Manager', 'Designer']),
                    tools_used=random.choice(['VS Code, Git, Docker', 'IntelliJ, Maven, Jenkins', 'PyCharm, Jupyter, TensorFlow']),
                    team_size=random.randint(1, 5),
                    start_date=timezone.now() - timedelta(days=random.randint(30, 365)),
                    end_date=timezone.now() - timedelta(days=random.randint(1, 29)) if random.choice([True, False]) else None,
                    project_url=f"https://github.com/{username}/project{random.randint(1, 100)}",
                    github_url=f"https://github.com/{username}/project{random.randint(1, 100)}"
                )

            # Create job applications
            jobs = Job.objects.all()
            for job in random.sample(list(jobs), random.randint(1, 5)):
                JobApplication.objects.create(
                    job=job,
                    student=student_profile,
                    status=random.choice(['applied', 'under_review', 'shortlisted', 'rejected', 'hired']),
                    cover_letter=f"Cover letter for {job.title} at {job.employer.company_name}",
                    portfolio_url=student_profile.portfolio_url,
                    linkedin_url=student_profile.linkedin_url,
                    github_url=student_profile.github_url,
                    availability_date=timezone.now() + timedelta(days=random.randint(30, 90))
                )

                # Create job bookmarks
                if random.choice([True, False]):
                    JobBookmark.objects.create(
                        student=student_profile,
                        job=job
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created dummy data')) 