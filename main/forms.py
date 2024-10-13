from django import forms
from .models import Project, Requirement

class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['title', 'description']
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
