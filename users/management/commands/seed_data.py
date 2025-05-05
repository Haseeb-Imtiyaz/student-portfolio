from django.core.management.base import BaseCommand
from users.models import College, Course, Skill, ResumeTemplate
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Seeds the database with initial data for colleges, courses, skills, and resume templates'

    def handle(self, *args, **kwargs):
        # Create colleges
        colleges = [
            {
                'name': 'Indian Institute of Technology Delhi',
                'location': 'New Delhi',
                'website': 'https://www.iitd.ac.in',
                'contact_email': 'contact@iitd.ac.in',
                'contact_phone': '01126591715',
            },
            {
                'name': 'National Institute of Technology Karnataka',
                'location': 'Surathkal, Karnataka',
                'website': 'https://www.nitk.ac.in',
                'contact_email': 'contact@nitk.ac.in',
                'contact_phone': '08242474000',
            },
            {
                'name': 'Birla Institute of Technology and Science',
                'location': 'Pilani, Rajasthan',
                'website': 'https://www.bits-pilani.ac.in',
                'contact_email': 'contact@bits-pilani.ac.in',
                'contact_phone': '01596242000',
            },
            {
                'name': 'Indian Institute of Science',
                'location': 'Bangalore, Karnataka',
                'website': 'https://www.iisc.ac.in',
                'contact_email': 'contact@iisc.ac.in',
                'contact_phone': '08022932300',
            },
            {
                'name': 'Indian Institute of Technology Bombay',
                'location': 'Mumbai, Maharashtra',
                'website': 'https://www.iitb.ac.in',
                'contact_email': 'contact@iitb.ac.in',
                'contact_phone': '02225722545',
            },
            {
                'name': 'Indian Institute of Technology Madras',
                'location': 'Chennai, Tamil Nadu',
                'website': 'https://www.iitm.ac.in',
                'contact_email': 'contact@iitm.ac.in',
                'contact_phone': '04422578200',
            },
            {
                'name': 'National Institute of Technology Tiruchirappalli',
                'location': 'Tiruchirappalli, Tamil Nadu',
                'website': 'https://www.nitt.edu',
                'contact_email': 'contact@nitt.edu',
                'contact_phone': '04312423000',
            },
            {
                'name': 'Delhi Technological University',
                'location': 'New Delhi',
                'website': 'https://www.dtu.ac.in',
                'contact_email': 'contact@dtu.ac.in',
                'contact_phone': '01127871000',
            },
            {
                'name': 'Vellore Institute of Technology',
                'location': 'Vellore, Tamil Nadu',
                'website': 'https://www.vit.ac.in',
                'contact_email': 'contact@vit.ac.in',
                'contact_phone': '04162202222',
            },
            {
                'name': 'Manipal Institute of Technology',
                'location': 'Manipal, Karnataka',
                'website': 'https://manipal.edu/mit.html',
                'contact_email': 'contact@manipal.edu',
                'contact_phone': '08202571711',
            }
        ]

        for college_data in colleges:
            College.objects.get_or_create(
                name=college_data['name'],
                defaults=college_data
            )

        # Create courses
        courses = [
            {
                'name': 'Bachelor of Technology in Computer Science',
                'duration': 4,
                'description': 'Undergraduate program in Computer Science and Engineering',
            },
            {
                'name': 'Bachelor of Technology in Electronics',
                'duration': 4,
                'description': 'Undergraduate program in Electronics and Communication Engineering',
            },
            {
                'name': 'Bachelor of Technology in Mechanical',
                'duration': 4,
                'description': 'Undergraduate program in Mechanical Engineering',
            },
            {
                'name': 'Master of Technology in Computer Science',
                'duration': 2,
                'description': 'Postgraduate program in Computer Science and Engineering',
            },
            {
                'name': 'Bachelor of Technology in Information Technology',
                'duration': 4,
                'description': 'Undergraduate program in Information Technology',
            },
            {
                'name': 'Bachelor of Technology in Artificial Intelligence',
                'duration': 4,
                'description': 'Undergraduate program in Artificial Intelligence',
            },
            {
                'name': 'Bachelor of Technology in Data Science',
                'duration': 4,
                'description': 'Undergraduate program in Data Science',
            },
            {
                'name': 'Master of Technology in Artificial Intelligence',
                'duration': 2,
                'description': 'Postgraduate program in Artificial Intelligence',
            },
            {
                'name': 'Master of Technology in Data Science',
                'duration': 2,
                'description': 'Postgraduate program in Data Science',
            },
            {
                'name': 'Bachelor of Technology in Civil Engineering',
                'duration': 4,
                'description': 'Undergraduate program in Civil Engineering',
            }
        ]

        for course_data in courses:
            Course.objects.get_or_create(
                name=course_data['name'],
                defaults=course_data
            )

        # Create skills
        skills = [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin',
            'TypeScript', 'PHP', 'Ruby', 'R', 'MATLAB', 'Scala', 'Perl',
            
            # Web Development
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js',
            'Django', 'Flask', 'Spring Boot', 'Laravel', 'ASP.NET', 'jQuery',
            'Bootstrap', 'Tailwind CSS', 'SASS', 'Webpack', 'GraphQL',
            
            # Mobile Development
            'React Native', 'Flutter', 'Android Development', 'iOS Development',
            'Xamarin', 'Ionic', 'Cordova',
            
            # Database
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle',
            'SQLite', 'Cassandra', 'DynamoDB', 'Firebase',
            
            # DevOps & Cloud
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'Google Cloud',
            'CI/CD', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Bitbucket',
            'Terraform', 'Ansible', 'Linux', 'Shell Scripting',
            
            # Data Science & AI
            'Machine Learning', 'Deep Learning', 'Data Science',
            'Artificial Intelligence', 'Natural Language Processing',
            'Computer Vision', 'TensorFlow', 'PyTorch', 'Keras',
            'Pandas', 'NumPy', 'SciPy', 'Scikit-learn', 'OpenCV',
            
            # Other Technologies
            'Blockchain', 'Web3', 'Solidity', 'Ethereum',
            'Microservices', 'REST API', 'GraphQL', 'WebSocket',
            'OAuth', 'JWT', 'OAuth2', 'JWT Authentication',
            
            # Soft Skills
            'Problem Solving', 'Critical Thinking', 'Teamwork',
            'Communication', 'Leadership', 'Time Management',
            'Project Management', 'Agile', 'Scrum', 'Kanban'
        ]

        for skill_name in skills:
            Skill.objects.get_or_create(name=skill_name)

        # Create resume templates
        templates = [
            {
                'name': 'Professional Classic',
                'description': 'A clean and professional template suitable for all industries',
                'template_path': 'resumes/professional_classic.html',
                'is_active': True
            }
        ]

        for template_data in templates:
            template, created = ResumeTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'template_path': template_data['template_path'],
                    'is_active': template_data['is_active']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with comprehensive data')) 