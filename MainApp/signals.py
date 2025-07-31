from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.db.models import F

snippet_view = Signal()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Пользователь {instance} создан")


@receiver(snippet_view)
def snippet_views_count(sender, snippet, **kwargs):
    snippet.views_count = F('views_count') + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()