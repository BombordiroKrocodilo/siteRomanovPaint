from django.urls  import path
from . import views

urlpatterns = [
    path('', views.home, name= 'home'),
    path('works/', views.works, name='works'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback, name='feedback'),
    path('news/<int:id>/', views.news_detail, name='news_detail'),
]
