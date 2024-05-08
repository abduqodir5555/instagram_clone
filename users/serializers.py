from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User, CodeVerify, VIA_PHONE, VIA_EMAIL
from users.utils import check_email_or_phone


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



