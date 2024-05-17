from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User, CodeVerify, VIA_PHONE, VIA_EMAIL, PHOTO_STEP
from users.utils import check_email_or_phone
from users.validators import check_phone_validator_serializer


class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ('id',
                  'auth_status',
                  'auth_type',
                  'email_or_phone',
                  )

        extra_kwargs = {
            'auth_status':{'required':False, 'read_only':True},
            'auth_type': {'required': False, 'read_only': True},
            'id': {'required': False, 'read_only': True},
        }

    def validate(self, data):
        info = data.get('email_or_phone', None).lower()
        data_type = check_email_or_phone(info)
        if data_type == 'email':
            data = {
                'email':info,
                'auth_type':VIA_EMAIL,
            }

            if User.objects.filter(email=info).exists():
                just = {
                    'status':False,
                    'message':'Bu email manzili avval ro\'yxatdan o\'tilgan'
                }
                raise ValidationError(just)
        elif data_type == 'phone':
            data = {
                'phone_number': info,
                'auth_type': VIA_PHONE,
            }

            if info.startswith('+998'):
                phone_1 = '+' + info[4:]
            else:
                phone_1 = '+998' + info[1:]
            if User.objects.filter(phone_number=info).exists() or User.objects.filter(phone_number=phone_1).exists():
                just = {
                    'status': False,
                    'message': 'Bu telefon raqami avval ro\'yxatdan o\'tilgan'
                }
                raise ValidationError(just)


        return data

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        if instance.email:
            data['email'] = instance.email
        else:
            data['phone_number'] = instance.phone_number

        return data



class VerifyOtpSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True, read_only=False)
    code = serializers.CharField(required=True, read_only=False)

    def validate(self, data):
        code = data.get('code', None)
        if not (len(code) == 4 and str(code).isdigit()):
            just = {
                'status':False,
                'message':'code 4 xonali va raqamlardan iborat bo\'lishi kerak'
            }
            raise ValidationError(just)

        return data


regestir, forgot_password = "regestir", "forgot_password"

class SendAgainCodeSerializer(serializers.Serializer):
    CODE_TYPE = (
        ("regestir", "regestir"),
        ("forgot_password", "forgot_password")
    )

    code_type = serializers.ChoiceField(choices=CODE_TYPE, required=True, read_only=False)
    user_id = serializers.UUIDField(required=True, read_only=False)


class UserInformationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, read_only=False)
    username = serializers.CharField(required=True, read_only=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    password = serializers.CharField(required=True, read_only=False)
    password_confirm = serializers.CharField(required=True, read_only=False)

    def validate(self, data):
        password = data.get('password', None)
        password_confirm = data.get('password_confirm', None)
        if password != password_confirm:
            just = {
                'status': False,
                'message': 'Parollar bir biriga teng emas'
            }
            raise ValidationError(just)

        validate_password(password)

        return data

    def validate_username(self, data):
        black_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '`', '|', '{', '}', '[', ']', '<', '>', ',', '/', '?', '+', '-', '*']
        if not len(data) >= 6:
            just = {
                'status': False,
                'message': 'username 6 qatordan katta bo\'lishi kerak!!!'
            }
            raise ValidationError(just)
        for char in data:
            if char in black_characters:
                just = {
                    'status': False,
                    'message': 'Siz usernamega blockdagi harflarni qatnashtirdiz!!!'
                }
                raise ValidationError(just)

        return data

    def validate_bio(self, bio):
        if len(bio) > 500:
            data = {
                'status': False,
                'message': 'bioga haddan oshiq so\'z kiritdiz'
            }
            raise ValidationError(data)

        return bio

    def validate_first_name(self, name):
        if not (len(name) >= 3 and len(name) <= 20 and str(name).isalpha()):
            just = {
                'status': False,
                'message': 'Ism 3 va 20 qator ichida faqat harflar bilan bo\'ladi'
            }
            raise ValidationError(just)

        return name

    def validate_last_name(self, name):
        if not (len(name) >= 3 and len(name) <= 20 and str(name).isalpha()):
            just = {
                'status': False,
                'message': 'Familya 3 va 20 qator ichida faqat harflar bilan bo\'ladi'
            }
            raise ValidationError(just)

        return name

    def validate_phone_number(self, phone):
        if not check_phone_validator_serializer(phone):
            data = {
                'status': False,
                'message': 'Telefon raqamni to\'g\'ri kiriting'
            }
            raise ValidationError(data)

        return phone

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        email = validated_data.get('email', None)
        if email and instance.email:
            just = {
                'status': False,
                'message': 'siz email kirita ololmaysiz!!!'
            }
            raise ValidationError(just)

        elif email:
            if User.objects.filter(email=email):
                just = {
                    'status': False,
                    'message': 'Bu email avval ro\'yxatga olingan'
                }
                raise ValidationError(just)

        instance.email = validated_data.get('email', instance.email)

        phone_number = validated_data.get('phone_number', None)
        if phone_number and instance.phone_number:
            print("instance:", instance.phone_number)
            just = {
                'status': False,
                'message': 'Siz telefon raqam kirita ololmaysiz!!!'
            }
            raise ValidationError(just)

        elif phone_number:
            if str(phone_number).startswith('+998'):
                phone_1 = phone_number
                phone_2 = '+' + phone_number[4:]
            else:
                phone_1 = phone_number
                phone_2 = '+998' + phone_number[1:]
            if User.objects.filter(phone_number=phone_1) or User.objects.filter(phone_number=phone_2):
                just = {
                    'status': False,
                    'message': 'Bu telefon raqam avval ro\'yxatdan o\'tgan'
                }
                raise ValidationError(just)

        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.password = validated_data.get('password', instance.password)
        instance.set_password(validated_data.get('password'))
        instance.auth_status = PHOTO_STEP
        instance.is_active = True
        instance.save()

        return instance


class PhotoStepSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, read_only=False)
    photo = serializers.ImageField(required=False)


class LoginSerializer(serializers.Serializer):
    user_input = serializers.CharField(required=True, read_only=False)
    password = serializers.CharField(required=True, read_only=False)

    def validate(self, data):

        return data






