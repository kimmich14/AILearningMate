import random
from django.core.management.base import BaseCommand
from learning.models import Course

class Command(BaseCommand):
    help = "Updates all courses with a random duration between 8 and 16"

    def handle(self, *args, **kwargs):
        courses = Course.objects.all()
        updated_count = 0

        for course in courses:
            new_duration = random.randint(8, 16)
            course.duration = new_duration
            course.save(update_fields=["duration"])
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"Updated {course.title} → {new_duration} weeks"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Done! Updated {updated_count} courses."
        ))
