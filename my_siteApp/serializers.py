from rest_framework import serializers
from .models import Article, Comment

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'text', 'created_date', 'category', 'user', 'author_name']
        read_only_fields = ['id', 'created_date', 'user']

class CommentSerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_date', 'author_name', 'article', 'article_title']
        read_only_fields = ['id', 'created_date']