import random
from django.shortcuts import render, redirect
from .models import Question, TestResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Avg, Max
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm


def home(request):
    return render(request, "main/home.html")


@login_required
def iq_test_view(request):
    """Показывает по одному вопросу за раз"""
    questions = Question.objects.all().order_by('id')
    total = len(questions)

    # Текущий индекс вопроса (по умолчанию 0)
    current_index = request.session.get('current_index', 0)

    # Если это POST — сохраняем ответ
    if request.method == 'POST':
        selected = request.POST.get('answer')
        question_id = request.POST.get('question_id')

        if 'answers' not in request.session:
            request.session['answers'] = {}

        answers = request.session['answers']
        answers[str(question_id)] = selected
        request.session['answers'] = answers

        # Переходим к следующему вопросу
        current_index += 1
        request.session['current_index'] = current_index

        # Если вопросов больше нет — считаем результат
        if current_index >= total:
            return redirect('test_result')

    # Если всё закончилось
    if current_index >= total:
        return redirect('test_result')

    question = questions[current_index]
    progress = f"{current_index + 1} / {total}"

    return render(request, "main/iq_test_single.html", {
        "question": question,
        "progress": progress,
    })


@login_required
def test_result(request):
    """Показывает результат IQ теста"""
    answers = request.session.get('answers', {})
    questions = Question.objects.all()
    score = 0
    total = len(questions)  # Всего 23 вопроса

    for q in questions:
        if str(q.id) in answers and int(answers[str(q.id)]) == q.correct_option:
            score += 1

    # Сохраняем результат
    TestResult.objects.create(user=request.user, score=score)

    # Вычисляем IQ с использованием Deviation IQ
    # Предполагаемые начальные значения (нужны данные для точности)
    mean_score = 11.5  # Средний балл (50% из 23), обновить позже
    std_dev = 4.0      # Стандартное отклонение (примерное), обновить позже

    # Z-оценка: (ваш балл - средний балл) / стандартное отклонение
    z_score = (score - mean_score) / std_dev if std_dev != 0 else 0
    # IQ = (Z * 15) + 100
    iq = (z_score * 15) + 100
    # Ограничиваем диапазон 70–130
    iq = max(70, min(130, round(iq)))

    # Чистим сессию
    request.session.pop('answers', None)
    request.session.pop('current_index', None)

    return render(request, "main/result.html", {
        "iq": iq,
        "score": score,
        "total": total,
    })


@login_required
def profile(request):
    """Просмотр и редактирование профиля"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Получаем статистику тестов
    results = TestResult.objects.filter(user=request.user).order_by('-date')
    best_score = results.aggregate(Max('score'))['score__max'] or 0
    avg_score = results.aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'results': results,
        'best_score': best_score,
        'avg_score': round(avg_score, 2),
    }
    
    return render(request, 'main/profile.html', context)


@login_required
def delete_profile(request):
    """Удаление профиля пользователя"""
    if request.method == 'POST':
        user = request.user
        username = user.username
        
        # Выходим из системы перед удалением
        logout(request)
        
        # Удаляем пользователя (профиль удалится автоматически благодаря CASCADE)
        user.delete()
        
        messages.success(request, f'Профиль {username} успешно удален. До свидания!')
        return redirect('home')
    
    return render(request, 'main/delete_profile_confirm.html')


def leaderboard(request):
    users = User.objects.annotate(
        best_score=Max('testresult__score'),
        avg_score=Avg('testresult__score')
    ).order_by('-best_score')[:10]
    return render(request, "main/leaderboard.html", {"users": users})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Аутентифицируем пользователя с явным указанием бэкенда
            user = authenticate(
                request, 
                username=username, 
                password=password,
                backend='django.contrib.auth.backends.ModelBackend'
            )
            
            # Входим в систему с явным указанием бэкенда
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Добро пожаловать, {username}! Регистрация успешна.')
                return redirect('home')
            else:
                messages.error(request, 'Ошибка входа после регистрации. Попробуйте войти вручную.')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})
