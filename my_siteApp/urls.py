from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('works/', views.works, name='works'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback, name='feedback'),
    
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/<str:category>/', views.articles_list, name='articles_by_category'),
    path('news/<int:id>/', views.news_detail, name='news_detail'),
    
    path('create-article/', views.create_article, name='create_article'),
    path('edit-article/<int:id>/', views.edit_article, name='edit_article'),
    path('delete-article/<int:id>/', views.delete_article, name='delete_article'),
    
    path('create-article-page/', views.create_article_page, name='create_article_page'),
    path('edit-article-page/<int:id>/', views.edit_article_page, name='edit_article_page'),
    path('delete-article-page/<int:id>/', views.delete_article_page, name='delete_article_page'),
]