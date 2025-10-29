from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Article, Comment
from .forms import ArticleForm, CommentForm, FeedbackForm
from .serializers import *
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import ArticleSerializer, CommentSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):

    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Генерация JWT токенов
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Регистрация прошла успешно!',
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):

    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Вход выполнен успешно!',
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Успешный выход из системы'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Неверный токен'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_token_refresh(request):

    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': 'Refresh токен обязателен'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return Response({
            'access': access_token,
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Неверный или просроченный refresh токен'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

def jwt_required(view_func):

    def wrapped_view(request, *args, **kwargs):
        try:
            jwt_auth = JWTAuthentication()
            auth_result = jwt_auth.authenticate(request)
            
            if auth_result is not None:
                user, token = auth_result
                request.user = user
                return view_func(request, *args, **kwargs)
            else:
                return Response({
                    'error': 'Требуется аутентификация',
                    'detail': 'Добавьте заголовок Authorization: Bearer <token>'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'error': 'Неверный токен',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return wrapped_view



# эндпоинты 
@api_view(['GET'])
@permission_classes([AllowAny])
def api_articles_list(request):
    """Список всех статей"""
    articles = Article.objects.all()
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_article_detail(request, id):
    """Статья по ID"""
    try:
        article = Article.objects.get(id=id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Статья не найдена'}, 
            status=status.HTTP_404_NOT_FOUND
        )

# CRUD
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_article(request):
    """Создать статью"""
    serializer = ArticleSerializer(data=request.data)
    
    if serializer.is_valid():
        category = serializer.validated_data.get('category', 'news')
        if not Article.can_user_create_article(request.user, category):
            return Response(
                {'error': 'У вас нет прав для создания статей в этой категории!'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        article = serializer.save(user=request.user)
        return Response(
            ArticleSerializer(article).data, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_update_article(request, id):
    """Обновить статью"""
    try:
        article = Article.objects.get(id=id)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Статья не найдена'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if article.user != request.user and not request.user.is_superuser:
        return Response(
            {'error': 'Вы можете редактировать только свои статьи!'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ArticleSerializer(article, data=request.data, partial=False)
    
    if serializer.is_valid():
        if 'category' in serializer.validated_data:
            new_category = serializer.validated_data['category']
            if not Article.can_user_create_article(request.user, new_category):
                return Response(
                    {'error': 'У вас нет прав для изменения категории на эту!'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_article(request, id):
    """Удалить статью"""
    try:
        article = Article.objects.get(id=id)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Статья не найдена'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if article.user != request.user and not request.user.is_superuser:
        return Response(
            {'error': 'Вы можете удалять только свои статьи!'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    article.delete()
    return Response(
        {'message': 'Статья успешно удалена'}, 
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def api_articles_by_category(request, category):
    """Фильтр по категории"""
    valid_categories = dict(Article.CATEGORY_CHOICES).keys()
    if category not in valid_categories:
        return Response(
            {'error': 'Неверная категория'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    articles = Article.objects.filter(category=category)
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_articles_sorted_by_date(request):
    """Сортировка по дате"""
    sort_order = request.GET.get('order', 'desc') 
    
    if sort_order == 'asc':
        articles = Article.objects.all().order_by('created_date')
    else:
        articles = Article.objects.all().order_by('-created_date')
    
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_comments_list(request):
    """Список всех комментариев"""
    comments = Comment.objects.all()
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_comment_detail(request, id):
    """Комментарий по ID"""
    try:
        comment = Comment.objects.get(id=id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    except Comment.DoesNotExist:
        return Response(
            {'error': 'Комментарий не найден'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def api_create_comment(request):
    """Создать комментарий"""
    serializer = CommentSerializer(data=request.data)
    
    if serializer.is_valid():
        article_id = serializer.validated_data.get('article')
        if not Article.objects.filter(id=article_id.id).exists():
            return Response(
                {'error': 'Статья не найдена'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_update_comment(request, id):
    """Обновить комментарий"""
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return Response(
            {'error': 'Комментарий не найден'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not request.user.is_superuser:
        return Response(
            {'error': 'У вас нет прав для редактирования комментариев!'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CommentSerializer(comment, data=request.data, partial=False)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_comment(request, id):
    """Удалить комментарий"""
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return Response(
            {'error': 'Комментарий не найден'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not request.user.is_superuser:
        return Response(
            {'error': 'У вас нет прав для удаления комментариев!'},
            status=status.HTTP_403_FORBIDDEN
        )

    comment.delete()
    return Response(
        {'message': 'Комментарий успешно удален'}, 
        status=status.HTTP_204_NO_CONTENT
    )

def register(request):
    """Отображение страницы регистрации и обработка формы"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Регистрация прошла успешно! Добро пожаловать, {user.username}. За Императора!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserCreationForm()
    
    return render(request, 'my_siteApp/register.html', {'form': form})

def user_login(request):
    """Отображение страницы входа и обработка формы"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}. За Императора!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'my_siteApp/login.html', {'form': form})

def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')

# CRUD
@login_required
def create_article(request):
    """Обработка создания статьи с проверкой прав доступа к категориям"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.cleaned_data['category']
            
            if not Article.can_user_create_article(request.user, category):
                messages.error(request, 'У вас нет прав для создания статей в этой категории!')
                return redirect('articles_list')
            
            article = form.save(commit=False)
            article.user = request.user
            article.save()
            messages.success(request, 'Статья успешно создана!')
            return redirect('articles_list')
    else:
        form = ArticleForm(user=request.user)
    
    return render(request, 'my_siteApp/create_article.html', {'form': form})

@login_required
def edit_article(request, id):
    """Обработка редактирования статьи с проверкой прав"""
    article = get_object_or_404(Article, id=id)
    
    if article.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы можете редактировать только свои статьи!')
        return redirect('articles_list')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            if 'category' in form.changed_data:
                new_category = form.cleaned_data['category']
                if not Article.can_user_create_article(request.user, new_category):
                    messages.error(request, 'У вас нет прав для изменения категории на эту!')
                    return redirect('articles_list')
            
            form.save()
            messages.success(request, 'Статья успешно обновлена!')
            return redirect('news_detail', id=article.id)
    else:
        form = ArticleForm(instance=article, user=request.user)
    
    return render(request, 'my_siteApp/edit_article.html', {'form': form, 'article': article})

@login_required
def delete_article(request, id):
    """Обработка удаления статьи"""
    article = get_object_or_404(Article, id=id)
    
    if article.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы можете удалять только своих еретиков!')
        return redirect('articles_list')
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Еретик удален!')
        return redirect('articles_list')
    
    return render(request, 'my_siteApp/delete_article.html', {'article': article})

def create_article_page(request):
    """Отображение страницы создания статьи"""
    if not request.user.is_authenticated:
        messages.error(request, 'Для создания статьи необходимо авторизоваться!')
        return redirect('login')
    
    form = ArticleForm(user=request.user)
    return render(request, 'my_siteApp/create_article.html', {'form': form})

def edit_article_page(request, id):
    """Отображение страницы редактирования статьи"""
    article = get_object_or_404(Article, id=id)
    
    if not request.user.is_authenticated:
        messages.error(request, 'Для редактирования статьи необходимо авторизоваться!')
        return redirect('login')
    
    if article.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы можете редактировать только свои статьи!')
        return redirect('articles_list')
    
    form = ArticleForm(instance=article, user=request.user)
    return render(request, 'my_siteApp/edit_article.html', {'form': form, 'article': article})

def delete_article_page(request, id):
    """Отображение страницы подтверждения удаления статьи"""
    article = get_object_or_404(Article, id=id)
    
    if not request.user.is_authenticated:
        messages.error(request, 'Для удаления статьи необходимо авторизоваться!')
        return redirect('login')
    
    if article.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы можете удалять только свои статьи!')
        return redirect('articles_list')
    
    return render(request, 'my_siteApp/delete_article.html', {'article': article})

def articles_list(request, category=None):
    """Отображение списка статей"""
    articles = Article.objects.all()
    
    if category:
        valid_categories = dict(Article.CATEGORY_CHOICES).keys()
        if category not in valid_categories:
            messages.error(request, 'Неверная категория')
            return redirect('articles_list')
        articles = articles.filter(category=category)
    
    context = {
        'articles': articles,
        'current_category': category,
        'category_choices': Article.CATEGORY_CHOICES,
    }
    return render(request, 'my_siteApp/articles_list.html', context)

def news_detail(request, id):
    """Отображение детальной страницы статьи с комментариями"""
    article = get_object_or_404(Article, id=id)
    comments = article.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.save()
            messages.success(request, 'Ваш комментарий добавлен!')
            return redirect('news_detail', id=id)
    else:
        comment_form = CommentForm()
    
    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'comments_count': comments.count(),
    }
    return render(request, 'my_siteApp/news_detail.html', context)

def home(request):
    """Домашняя страница"""
    latest_articles = Article.objects.all()[:3]
    return render(request, 'my_siteApp/home.html', {'latest_articles': latest_articles})

def works(request):
    """Страница работ"""
    return render(request, 'my_siteApp/works.html')

def about(request):
    """Страница о нас"""
    return render(request, 'my_siteApp/about.html')

def feedback(request):
    """Страница обратной связи"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            print("\n" + "="*50)
            print("НОВОЕ СООБЩЕНИЕ ИЗ ФОРМЫ ОБРАТНОЙ СВЯЗИ")
            print("="*50)
            print(f"Имя: {name}")
            print(f"Email: {email}")
            print(f"Сообщение: {message}")
            print(f"Время отправки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50 + "\n")
            
            context = {'form_submitted': True, 'name': name}
            return render(request, 'my_siteApp/feedback.html', context)
    else:
        form = FeedbackForm()
    
    return render(request, 'my_siteApp/feedback.html', {'form': form})