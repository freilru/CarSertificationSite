# Импорт необходимых модулей
import json
import time

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
import urllib.request
import urllib.parse
import io

from django.views.decorators.csrf import csrf_exempt

from .api import get_check, process_large_query, create_pdf
from .forms import ProjectForm, RequirementForm
from .models import Project, Requirement, RequirementCheck, StoredFile


# Представление для главной страницы
@csrf_exempt
def index(request):
    projects = Project.objects.all()
    stored_files = StoredFile.objects.all()
    return render(request, 'main/index.html', {'projects': projects, 'stored_files': stored_files})


@csrf_exempt
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProjectForm()
    return render(request, 'main/create_project.html', {'form': form})


@csrf_exempt
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


@csrf_exempt
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
            print(check_res)
            RequirementCheck.objects.create(
                requirement=requirement,
                summary_sert=check_res[0]['summary'],
                is_passed=check_res[0]['is_done'],
                comment=check_res[0]['comment']
            )

            return redirect('project_detail', project_id=project_id)
    else:
        form = RequirementForm()
    return render(request, 'main/create_requirement.html', {'form': form, 'project': project})


@csrf_exempt
def check_detail(request, project_id, requirement_id):
    requirement = get_object_or_404(Requirement, id=requirement_id, project_id=project_id)
    checks = RequirementCheck.objects.filter(requirement=requirement)
    return render(request, 'main/check_detail.html', {'requirement': requirement, 'checks': checks})


@csrf_exempt
def delete_check(request, project_id, requirement_id, check_id):
    check = get_object_or_404(RequirementCheck, id=check_id, requirement_id=requirement_id)
    check.delete()
    return redirect('project_detail', project_id=project_id)


@csrf_exempt
def delete_requirement(request, project_id, requirement_id):
    requirement = get_object_or_404(Requirement, id=requirement_id, project_id=project_id)
    requirement.delete()
    return redirect('project_detail', project_id=project_id)


@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            pdf_file = request.FILES['file']
            if pdf_file.name.endswith('.pdf'):
                import os
                from django.conf import settings

                pdf_folder = os.path.join(settings.BASE_DIR, 'pdf')
                if not os.path.exists(pdf_folder):
                    os.makedirs(pdf_folder)

                file_path = os.path.join(pdf_folder, pdf_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)

                StoredFile.objects.update_or_create(
                    title=pdf_file.name,
                    defaults={'title': pdf_file.name}
                )
                return JsonResponse({'message': 'PDF успешно сохранен'}, status=200)
            else:
                return JsonResponse({'error': 'Файл должен быть в формате PDF'}, status=400)
        else:
            return JsonResponse({'error': 'Файл не найден'}, status=400)
    return render(request, 'main/upload_pdf.html')


@csrf_exempt
def create_report(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids')
        print(file_ids)
        res = process_large_query(file_ids)
        print(res)

        # Создаем PDF-файл
        import os
        from django.conf import settings
        from .api import create_pdf

        # Создаем директорию для отчетов, если она не существует
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        # Генерируем уникальное имя файла
        pdf_filename = f'report_{request.user.id}_{int(time.time())}.pdf'
        pdf_path = os.path.join(reports_dir, pdf_filename)

        # Создаем PDF-файл
        create_pdf(res, pdf_path)

        # Формируем URL для скачивания PDF
        pdf_url = settings.MEDIA_URL + f'reports/{pdf_filename}'
        print(pdf_url)

        return render(request, 'main/create_report.html', {'reports': res, 'pdf_url': pdf_url})

    return render(request, 'main/create_report.html')
