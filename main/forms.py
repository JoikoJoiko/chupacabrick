from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'paper-input',
            'placeholder': 'Введите логин'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'paper-input',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'paper-input',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'paper-input',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'paper-input',
            'placeholder': 'Введите пароль'
        })
    )


from django.forms import modelformset_factory
from .models import Medicine, MedicineTime


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'title',
            'comment',
            'start_date',
            'end_date',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'paper-input',
                'placeholder': 'Например: Витамин C'
            }),
            'comment': forms.TextInput(attrs={
                'class': 'paper-input',
                'placeholder': 'Например: после еды'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'paper-input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'paper-input',
                'type': 'date'
            }),
            'monday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
            'tuesday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
            'wednesday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
            'thursday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
            'friday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
            'saturday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
            'sunday': forms.CheckboxInput(attrs={'class': 'paper-checkbox'}),
        }
        labels = {
            'title': 'Название лекарства',
            'comment': 'Комментарий',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'monday': 'Пн',
            'tuesday': 'Вт',
            'wednesday': 'Ср',
            'thursday': 'Чт',
            'friday': 'Пт',
            'saturday': 'Сб',
            'sunday': 'Вс',
        }


class MedicineTimeForm(forms.ModelForm):
    class Meta:
        model = MedicineTime
        fields = ['time']
        widgets = {
            'time': forms.TimeInput(attrs={
                'class': 'paper-input',
                'type': 'time'
            })
        }
        labels = {
            'time': 'Время приёма'
        }


MedicineTimeFormSet = modelformset_factory(
    MedicineTime,
    form=MedicineTimeForm,
    extra=3,
    can_delete=True
)

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'avatar']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'paper-input',
                'placeholder': 'Как тебя называть?'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'paper-file'
            }),
        }
        labels = {
            'display_name': 'Имя на сайте',
            'avatar': 'Аватар',
        }
