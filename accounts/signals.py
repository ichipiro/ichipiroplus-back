from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Faculty, Department


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    if sender.name == "accounts":
        Faculty.objects.update_or_create(name="情報科学部")
        Faculty.objects.update_or_create(name="国際学部")
        Faculty.objects.update_or_create(name="芸術学部")

        Department.objects.update_or_create(
            name="未配属", faculty=Faculty.objects.get(name="情報科学部")
        )
        Department.objects.update_or_create(
            name="情報工学科", faculty=Faculty.objects.get(name="情報科学部")
        )
        Department.objects.update_or_create(
            name="知能工学科", faculty=Faculty.objects.get(name="情報科学部")
        )
        Department.objects.update_or_create(
            name="システム工学科", faculty=Faculty.objects.get(name="情報科学部")
        )
        Department.objects.update_or_create(
            name="医用情報科学科", faculty=Faculty.objects.get(name="情報科学部")
        )
        Department.objects.update_or_create(
            name="情報科学研究科", faculty=Faculty.objects.get(name="情報科学部")
        )
        Department.objects.update_or_create(
            name="国際学科", faculty=Faculty.objects.get(name="国際学部")
        )
        Department.objects.update_or_create(
            name="国際学研究科", faculty=Faculty.objects.get(name="国際学部")
        )
        Department.objects.update_or_create(
            name="美術学科", faculty=Faculty.objects.get(name="芸術学部")
        )
        Department.objects.update_or_create(
            name="デザイン工芸学科", faculty=Faculty.objects.get(name="芸術学部")
        )
        Department.objects.update_or_create(
            name="芸術学研究科", faculty=Faculty.objects.get(name="芸術学部")
        )
