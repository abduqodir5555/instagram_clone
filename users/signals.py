from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User, CodeVerify, REGESTIR
from users.utils import create_otp_code, send_code_email


@receiver(post_save, sender=User)
def create_verify_code(sender, instance, created, **kwargs):
    if created:
        code = create_otp_code()
        if instance.email:
            send_code_email(code, instance.email)
        CodeVerify.objects.create(
            user = instance,
            code = code,
            verify_type = REGESTIR
        )
