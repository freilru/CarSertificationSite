from django.contrib import admin
from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название проекта', default='', null=True)
    description = models.TextField(verbose_name='Краткое описание', default='', null=True)

    def __str__(self):
        return self.title


class Requirement(models.Model):
    CATEGORY_CHOICES = [
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
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requirements')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория', default='', null=True)
    title = models.CharField(max_length=200, verbose_name='Название', default='', null=True)
    description = models.TextField(verbose_name='Описание', default='', null=True)
    characteristics = models.TextField(verbose_name='Характеристики', default='', null=True)

    def __str__(self):
        return self.title


class RequirementCheck(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='checks')
    summary_sert = models.TextField(verbose_name='Выжимка', blank=True, default='', null=True)
    is_passed = models.BooleanField(verbose_name='Зачитывается', default=False)
    comment = models.TextField(verbose_name='Комментарий', blank=True, default='', null=True)

    def __str__(self):
        return f'Проверка для {self.requirement.title} - {"Зачтено" if self.is_passed else "Не зачтено"}'
