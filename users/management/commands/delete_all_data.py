from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import (
    User, StudentProfile, EmployerProfile, Job, JobApplication,
    JobBookmark, Project, AcademicRecord, Skill, StudentSkill,
    College, Course, ResumeTemplate, Notification
)

class Command(BaseCommand):
    help = 'Deletes all data from the database'

    def handle(self, *args, **options):
        # Delete all data in reverse order of dependencies
        Notification.objects.all().delete()
        JobBookmark.objects.all().delete()
        JobApplication.objects.all().delete()
        Job.objects.all().delete()
        StudentSkill.objects.all().delete()
        Project.objects.all().delete()
        AcademicRecord.objects.all().delete()
        StudentProfile.objects.all().delete()
        EmployerProfile.objects.all().delete()
        User.objects.all().delete()
        Skill.objects.all().delete()
        College.objects.all().delete()
        Course.objects.all().delete()
        ResumeTemplate.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all data')) 