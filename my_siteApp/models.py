from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Article(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'Новости'),
        ('works', 'Ваши работы'),
        ('review', 'Обзоры'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст статьи")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='news',
        verbose_name="Категория"
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Автор"
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_date']
    
    def can_user_create_article(user, category):
        """
        Проверяет, может ли пользователь создавать статью в указанной категории
        """
        if not user.is_authenticated:
            return False
            
        if user.is_superuser or user.is_staff:
            return True
            
        return category == 'works'
    
    def can_user_edit_article(self, user):
        """
        Проверяет, может ли пользователь редактировать/удалять статью
        """
        if not user.is_authenticated:
            return False
            
        if user.is_superuser or user.is_staff:
            return True
            
        return self.user == user

class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    author_name = models.CharField(max_length=100, verbose_name="Имя автора")
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Статья"
    )
    
    def __str__(self):
        return f"Комментарий от {self.author_name}"
    
    class Meta:
        ordering = ['created_date']