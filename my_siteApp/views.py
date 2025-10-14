from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Article, Comment
from .forms import ArticleForm, CommentForm, FeedbackForm
from datetime import datetime

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