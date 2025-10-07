from django.http import HttpResponse
from django.shortcuts import render
from .forms import FeedbackForm
from datetime import datetime

def home(request):
    return render(request, 'my_siteApp/home.html')

def works(request):
    return render (request, 'my_siteApp/works.html')

def about(request):
    return render (request, 'my_siteApp/about.html')

def feedback(request):
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
            
            context = {
                'form_submitted': True,
                'name': name,
                'email': email,
                'message': message,
            }
            return render(request, 'my_siteApp/feedback.html', context)
    else:
        form = FeedbackForm()
    
    return render(request, 'my_siteApp/feedback.html', {'form': form})

def news_detail(request, id):
    context = {
        'news_id': id,
        'title': f"Статья {id}",
        'content': f"Это содержимое статьи {id}.",
    }
    
    return render(request, 'my_siteApp/news_detail.html', context)