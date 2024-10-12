# Импорт необходимых модулей
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
import urllib.request
import urllib.parse

from .api import get_check
from .forms import ProjectForm, RequirementForm
from .models import Project, Requirement, RequirementCheck


# Представление для главной страницы
def index(request):
    projects = Project.objects.all()
    return render(request, 'main/index.html', {'projects': projects})


def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProjectForm()
    return render(request, 'main/create_project.html', {'form': form})


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    requirements = Requirement.objects.filter(project=project)
    checks = RequirementCheck.objects.filter(requirement__in=requirements)
    # Создаем словари для подсчета зачетов и незачетов по каждой категории
    passed_counts = {category[0]: 0 for category in Requirement.CATEGORY_CHOICES}
    failed_counts = {category[0]: 0 for category in Requirement.CATEGORY_CHOICES}

    # Подсчитываем зачеты и незачеты для каждого требования
    for check in checks:
        category = check.requirement.category
        if check.is_passed:
            passed_counts[category] += 1
        else:
            failed_counts[category] += 1

    # Преобразуем словари в списки для передачи в шаблон
    passed_list = [passed_counts[category[0]] for category in Requirement.CATEGORY_CHOICES]
    failed_list = [failed_counts[category[0]] for category in Requirement.CATEGORY_CHOICES]
    # Создаем список кортежей для категорий требований
    requirement_categories = [
        (category[0], category[1]) for category in Requirement.CATEGORY_CHOICES
    ]

    # Группируем требования по категориям
    requirements_by_category = {}
    for requirement in requirements:
        if requirement.category not in requirements_by_category:
            requirements_by_category[requirement.category] = []
        requirements_by_category[requirement.category].append(requirement)
    # Добавляем списки в контекст
    context = {
        'project': project,
        'requirements': requirements,
        'checks': checks,
        'passed_counts': passed_list,
        'failed_counts': failed_list,
        'requirement_categories': requirement_categories,
        'requirements_by_category': requirements_by_category,
    }
    return render(request, 'main/project_detail.html', context)


def create_requirement(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = RequirementForm(request.POST)
        if form.is_valid():
            requirement = form.save(commit=False)
            requirement.project = project
            requirement.save()
            check_res = get_check(requirement.category, requirement.title, requirement.description,
                                  requirement.characteristics)
            RequirementCheck.objects.create(
                requirement=requirement,
                summary_sert=check_res['summary'],
                is_passed=check_res['is_done'],
                comment=check_res['comment']
            )
            
            return redirect('project_detail', project_id=project_id)
    else:
        form = RequirementForm()
    return render(request, 'main/create_requirement.html', {'form': form, 'project': project})


def check_detail(request, project_id, requirement_id):
    requirement = get_object_or_404(Requirement, id=requirement_id, project_id=project_id)
    checks = RequirementCheck.objects.filter(requirement=requirement)
    return render(request, 'main/check_detail.html', {'requirement': requirement, 'checks': checks})


def delete_check(request, project_id, requirement_id, check_id):
    check = get_object_or_404(RequirementCheck, id=check_id, requirement_id=requirement_id)
    check.delete()
    return redirect('project_detail', project_id=project_id)


def delete_requirement(request, project_id, requirement_id):
    requirement = get_object_or_404(Requirement, id=requirement_id, project_id=project_id)
    requirement.delete()
    return redirect('project_detail', project_id=project_id)
