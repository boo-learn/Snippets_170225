from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.db.models import F
from MainApp.models import Comment, Notification, UserProfile, Snippet, Subscription

snippet_view = Signal()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(snippet_view)
def snippet_views_count(sender, snippet, **kwargs):
    snippet.views_count = F('views_count') + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.snippet.user and instance.author != instance.snippet.user:
        Notification.objects.create(
            recipient=instance.snippet.user,
            notification_type='comment',
            title=f'Новый комментарий к сниппету "{instance.snippet.name}"',
            message=f'Пользователь {instance.author.username} оставил комментарий: {instance.text}'
        )


@receiver(post_save, sender=Snippet)
def edit_snippet_notification(sender, instance, created, **kwargs):
    if not created:
        subs = Subscription.objects.filter(snippet=instance)
        for sub in subs:
            user = sub.user
            Notification.objects.create(
                recipient=user,
                notification_type='snippet_update',
                title=f'Изменен сниппет "{instance.name}"',
                message=f'Автор отредактировал сниппет "{instance.name}"'
            )