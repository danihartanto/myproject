from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # Tambahkan data user ke response
        data.update({
            "user": {
                "id": self.user.id,
                "email": self.user.email,
                "name": self.user.name
            },
            "message": "Login berhasil."
        })

        return data
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name','last_login']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    
