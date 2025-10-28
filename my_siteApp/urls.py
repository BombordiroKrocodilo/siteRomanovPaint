from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenVerifyView

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
    
    # API
    path('api/articles/', views.api_articles_list, name='api_articles_list'),
    path('api/articles/<int:id>/', views.api_article_detail, name='api_article_detail'),
    path('api/articles/category/<str:category>/', views.api_articles_by_category, name='api_articles_by_category'),
    path('api/articles/sort/date/', views.api_articles_sorted_by_date, name='api_articles_sorted_by_date'),
    
    path('api/comment/', views.api_comments_list, name='api_comments_list'),
    path('api/comment/<int:id>/', views.api_comment_detail, name='api_comment_detail'),
    path('api/comment/create/', views.api_create_comment, name='api_create_comment'),
    path('api/comment/<int:id>/update/', views.api_update_comment, name='api_update_comment'),
    path('api/comment/<int:id>/delete/', views.api_delete_comment, name='api_delete_comment'),
    
    # JWT
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    path('api/auth/token/refresh/', views.api_token_refresh, name='api_token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='api_token_verify'),
    path('api/auth/profile/', views.api_user_profile, name='api_user_profile'),
    
    path('api/articles/create/', views.api_create_article, name='api_create_article'),
    path('api/articles/<int:id>/update/', views.api_update_article, name='api_update_article'),
    path('api/articles/<int:id>/delete/', views.api_delete_article, name='api_delete_article'),
]

#curl -X POST http://localhost:8000/api/auth/register/ ^
#-H "Content-Type: application/json" ^
#-d "{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"testpass123\", \"password_confirm\": \"testpass123\"}"
