import uuid
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from core.settings import EMAIL_EXPIRE_TIME, PHONE_EXPIRE_TIME
from common.models import BaseModel
from users.validators import check_phone_validator, check_code_validator

VIA_PHONE, VIA_EMAIL = 'VIA_PHONE', 'VIA_EMAIL'
USER, ADMIN, SUPERADMIN = 'USER', 'ADMIN', 'SUPERADMIN'
NEW, CODE_VERIFIED, PHOTO_STEP, DONE = 'NEW', 'CODE_VERIFIED', 'PHOTO_STEP', 'DONE'
REGESTIR, RESET_PASSWORD = 'REGESTIR', 'RESET_PASSWORD'


class User(BaseModel, AbstractUser):
    AUTH_TYPE = (
        ('VIA_PHONE', 'VIA_PHONE'),
        ('VIA_EMAIL', 'VIA_EMAIL')
    )
    AUTH_ROLE = (
        ('USER', 'USER'),
        ('ADMIN', 'ADMIN'),
        ('SUPERADMIN', 'SUPERADMIN')
    )
    AUTH_STATUS = (
        ('NEW', 'NEW'),
        ('CODE_VERIFIED', 'CODE_VERIFIED'),
        ('PHOTO_STEP', 'PHOTO_STEP'),
        ('DONE', 'DONE'),
    )

    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    email = models.EmailField(max_length=100, unique=True, blank=True)
    phone_number = models.CharField(max_length=100, validators=[check_phone_validator],
                                    unique=True, blank=True)
    photo = models.ImageField(upload_to="users/", null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg', 'png'))])
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPE, null=True, blank=True)
    auth_role = models.CharField(max_length=20, choices=AUTH_ROLE, default=USER)
    auth_status = models.CharField(max_length=20, choices=AUTH_STATUS, default=NEW)

    def check_email(self):
        if self.email:
            self.email = self.email.lower()

    def check_username(self):
        if not self.username:
            while True:
                username = "instagram-"+str(uuid.uuid4()).split('-')[-1]
                if not User.objects.filter(username=username).exists():
                    break
            self.username = username

    def check_pass(self):
        if not self.password:
            password = "instagram-"+str(uuid.uuid4()).split('-')[-1]
            self.password = password

    def check_hash_pass(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.check_hash_pass()

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)


class CodeVerify(BaseModel):
    VERIFY_TYPE = (
        ('REGESTIR', 'REGESTIR'),
        ('RESET_PASSWORD', 'RESET_PASSWORD')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verify_codes')

    code = models.CharField(max_length=4, validators=[check_code_validator])
    verify_type = models.CharField(max_length=20, choices=VERIFY_TYPE)
    expire_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expire_time:
            auth_type = self.user.auth_type
            if auth_type == VIA_PHONE:
                self.expire_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE_TIME)
            elif auth_type == VIA_EMAIL:
                self.expire_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE_TIME)

        super(CodeVerify, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'code_verify'
        verbose_name_plural = 'code verifies'
