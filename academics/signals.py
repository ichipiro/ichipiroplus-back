from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Schedule, Term


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    if sender.name == "academics":
        Term.objects.update_or_create(number=1)
        Term.objects.update_or_create(number=2)
        Term.objects.update_or_create(number=3)
        Term.objects.update_or_create(number=4)

        for i in range(1, 8):
            for j in range(1, 6):
                Schedule.objects.update_or_create(
                    day=i,
                    time=j,
                )
