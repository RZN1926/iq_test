from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма регистрации с email"""
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS классы ко всем полям
        self.fields['username'].widget.attrs.update({'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input'})
        
        # Русские названия полей
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Добавляем подсказки для пароля
        self.fields['password1'].help_text = '''
            <ul style="color: #a0aec0; font-size: 0.875rem; margin-top: 0.5rem; padding-left: 1.5rem;">
                <li>Пароль должен содержать минимум 8 символов</li>
                <li>Избегайте распространенных паролей (например: password123, qwerty)</li>
                <li>Пароль не должен состоять только из цифр</li>
            </ul>
        '''
        self.fields['password2'].help_text = None  # Убираем лишний текст
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class RegisterForm(forms.ModelForm):
    """Форма регистрации пользователя"""
    username = forms.CharField(
        max_length=150,
        label='Никнейм',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите никнейм',
            'class': 'form-input'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@mail.com',
            'class': 'form-input'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'class': 'form-input'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'class': 'form-input'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким никнеймом уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают.')
        
        if password1 and len(password1) < 6:
            raise ValidationError('Пароль должен содержать минимум 6 символов.')

        return cleaned_data


class LoginForm(forms.Form):
    """Форма входа"""
    username = forms.CharField(
        max_length=150,
        label='Никнейм',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите никнейм',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'class': 'form-input'
        })
    )


class PasswordResetRequestForm(forms.Form):
    """Форма запроса восстановления пароля"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите ваш email',
            'class': 'form-input'
        })
    )


class PasswordResetConfirmForm(forms.Form):
    """Форма подтверждения восстановления пароля"""
    code = forms.CharField(
        max_length=6,
        label='Код восстановления',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите 6-значный код',
            'class': 'form-input'
        })
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите новый пароль',
            'class': 'form-input'
        })
    )
    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'class': 'form-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают.')
        
        if password1 and len(password1) < 6:
            raise ValidationError('Пароль должен содержать минимум 6 символов.')

        return cleaned_data


# ===== ФОРМЫ ДЛЯ ПРОФИЛЯ =====

class UserUpdateForm(forms.ModelForm):
    """Форма для обновления данных пользователя"""
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
        }


class ProfileUpdateForm(forms.ModelForm):
    """Форма для обновления профиля пользователя"""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Расскажите о себе...'
            }),
        }
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({
            'class': 'form-input',
            'accept': 'image/*'
        })
        self.fields['avatar'].required = False
        self.fields['bio'].required = False
