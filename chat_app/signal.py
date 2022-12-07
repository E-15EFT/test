from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from .models import ChatSession, ChatMessage
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


@receiver(post_save, sender=ChatSession)
def sender_receiver_no_same(sender, instance, created, **kwargs):
    if created:
        if instance.user1 == instance.user2:
            raise ValidationError("Sender and Receiver are not same!!", code="Invalid")


@receiver(post_save, sender=ChatMessage)
def user_must_sender_or_receiver(sender, instance, created, **kwargs):
    if created:
        if (
            instance.user != instance.chat_session.user1
            and instance.user != instance.chat_session.user2
        ):
            raise ValidationError("Invalid sender!!", code="Invalid")
