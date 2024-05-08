from random import randint

from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

from core.settings import EMAIL_HOST


def check_email_or_phone(data):
    email_data = data
    if '@' in email_data and email_data.count('@')==1:
        if len(email_data.split('@')[0]) > 30:
            raise ValidationError({"status": False, "message": "email or phone number is not valid"})
        email_data = email_data.split('@')[-1]
        if '.' in email_data and email_data.count('.')==1:
            if len(email_data.split('.')[0])>10 or len(email_data.split('.')[1])>5:
                raise ValidationError({"status":False, "message":"email or phone number is not valid"})
            else:
                return "email"
        else:
            raise ValidationError({"status": False, "message": "email or phone number is not valid"})

    obj = data
    if obj[0] == '+':
        if obj[1:].isdigit():
            if obj.startswith('+998') and len(obj)==13:
                return "phone"
            elif obj.startswith('+') and len(obj)==10:
                return "phone"
            else:
                raise ValidationError({"status": False, "message": "email or phone number is not valid"})
        else:
            raise ValidationError({"status": False, "message": "email or phone number is not valid"})
    else:
        raise ValidationError({"status": False, "message": "email or phone number is not valid"})


def create_otp_code():
    code = ''.join(str(randint(0, 9)) for _ in range(4))
    return code


def send_code_email(code, email):
    message = f"Your otp code is {code}"
    send_mail(subject="Registration OTP code", message=message, from_email=EMAIL_HOST, recipient_list = [email],
              fail_silently=True)
