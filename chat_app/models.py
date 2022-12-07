from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import uuid
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(default="default.jpeg", upload_to="profile_images")
    forget_password_token = models.CharField(max_length=100)
    location = models.CharField(max_length=300, blank=True, null=True)
    education = models.CharField(max_length=300, blank=True, null=True)
    work = models.CharField(max_length=200, blank=True, null=True)
    more_about_author = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_online = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.profile_pic:
            self.profile_pic = self.compressImage(self.profile_pic)
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class ChatSession(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1_name")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2_name")
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user1", "user2")
        verbose_name = "Chat Message"

    def __str__(self):
        return "%s_%s" % (self.user1.username, self.user2.username)

    @property
    def room_group_name(self):
        return f"chat_{self.id}"

    @staticmethod
    def chat_session_exists(user1, user2):
        return ChatSession.objects.filter(
            Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
        ).first()

    @staticmethod
    def create_if_not_exists(user1, user2):
        res = ChatSession.chat_session_exists(user1, user2)
        return False if res else ChatSession.objects.create(user1=user1, user2=user2)


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="user_messages"
    )
    user = models.ForeignKey(
        User, verbose_name="message_sender", on_delete=models.CASCADE
    )
    message_detail = models.JSONField()

    class Meta:
        ordering = ["-message_detail__timestamp"]

    def __str__(self):
        return "%s" % (self.message_detail["timestamp"])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update ChatSession TimeStampe
        ChatSession.objects.get(id=self.chat_session.id).save()

    @staticmethod
    def count_overall_unread_msg(user_id):
        total_unread_msg = 0
        user_all_friends = ChatSession.objects.filter(
            Q(user1__id=user_id) | Q(user2__id=user_id)
        )
        for ch_session in user_all_friends:
            un_read_msg_count = (
                ChatMessage.objects.filter(
                    chat_session=ch_session.id, message_detail__read=False
                )
                .exclude(user__id=user_id)
                .count()
            )
            total_unread_msg += un_read_msg_count
        return total_unread_msg

    @staticmethod
    def meassage_read_true(message_id):
        msg_inst = ChatMessage.objects.filter(id=message_id).first()
        msg_inst.message_detail["read"] = True
        msg_inst.save(
            update_fields=[
                "message_detail",
            ]
        )
        return None

    @staticmethod
    def all_msg_read(room_id, user):
        all_msg = ChatMessage.objects.filter(
            chat_session=room_id, message_detail__read=False
        ).exclude(user__username=user)
        for msg in all_msg:
            msg.message_detail["read"] = True
            msg.save(
                update_fields=[
                    "message_detail",
                ]
            )
        return None

    @staticmethod
    def sender_inactive_msg(message_id):
        return ChatMessage.objects.filter(id=message_id).update(
            message_detail__Sclr=True
        )

    @staticmethod
    def receiver_inactive_msg(message_id):
        return ChatMessage.objects.filter(id=message_id).update(
            message_detail__Rclr=True
        )
