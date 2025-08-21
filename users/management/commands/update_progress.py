# learningapp/management/commands/update_progress.py

import random
from django.core.management.base import BaseCommand
from learning.models import Enrollment

class Command(BaseCommand):
    help = "Update all enrollments with random progress percentage"

    def handle(self, *args, **kwargs):
        enrollments = Enrollment.objects.all()
        total = enrollments.count()
        self.stdout.write(f"Found {total} enrollments...")

        for enrollment in enrollments:
            progress = round(random.uniform(0, 100), 2)  # random percentage, 2 decimal places
            enrollment.progress = progress
            enrollment.save(update_fields=["progress"])
            self.stdout.write(f"Updated enrollment {enrollment.id} -> {progress}%")

        self.stdout.write(self.style.SUCCESS("✅ All enrollments updated with random progress."))
