from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='user.username', read_only=True)
    author_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 
            'title', 
            'text', 
            'created_date', 
            'category', 
            'user', 
            'author_name',
            'author_details'
        ]
        read_only_fields = ['id', 'created_date', 'user', 'author_name', 'author_details']

class CommentSerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_details = ArticleSerializer(source='article', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 
            'text', 
            'created_date', 
            'author_name', 
            'article', 
            'article_title',
            'article_details'
        ]
        read_only_fields = ['id', 'created_date']

# JWT 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        min_length=6,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        min_length=6,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password', 
            'password_confirm', 
            'first_name', 
            'last_name'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Неверные учетные данные')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт отключен')
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Необходимо указать имя пользователя и пароль')

class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)