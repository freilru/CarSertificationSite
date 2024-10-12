from django import forms
from .models import Project, Requirement

class ProjectForm(forms.ModelForm):
    theme = forms.ChoiceField(
        choices=[
            ('wheelbase', 'Колесная база'),
        ('engine', 'Двигатель'),
        ('transmission', 'Трансмиссия'),
        ('brakes', 'Тормоза'),
        ('suspension', 'Подвеска'),
        ('windows', 'Стекла'),
        ('fuel_system', 'Топливная система'),
        ('lighting', 'Световая система'),
        ('exhaust', 'Выхлопная система'),
        ('safety', 'Система безопасности'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Тема проекта'
    )

    class Meta:
        model = Project
        fields = ['theme', 'title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'title': 'Название проекта',
            'description': 'Краткое описание',
        }

class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ['category', 'title', 'description', 'characteristics']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'characteristics': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'category': 'Категория',
            'title': 'Название',
            'description': 'Описание',
            'characteristics': 'Характеристики',
        }
