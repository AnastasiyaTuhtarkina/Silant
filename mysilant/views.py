# Стандартные библиотеки
import logging
from functools import wraps

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics


# Локальные импорты
from .filters import MachineFilter, MaintenanceFilter, ClaimFilter
from .models import Machine, TechnicalMaintenance, Claim, Reference, Client, ServiceOrganization
from .forms import *
from .serializers import *


logger = logging.getLogger(__name__)
def home(request):
    search_query = request.GET.get('search', '')

    is_manager = request.user.groups.filter(name='Менеджер').exists()
    is_service_organization = request.user.groups.filter(name='Сервисная организация').exists()
    
    # Фильтрация машин по пользователю (если авторизован)
    if request.user.is_authenticated:
        machines = get_machines_for_user(request.user)  # Используем вашу готовую функцию
        if search_query:
            machines = machines.filter(serial_number__icontains=search_query)
        machines = machines.order_by('shipment_date')
        
        # Фильтрация ТО и рекламаций только для машин пользователя
        maintenances = TechnicalMaintenance.objects.filter(machine__in=machines).order_by('maintenance_date')
        claims = Claim.objects.filter(machine__in=machines).order_by('rejection_date')

         # Пагинация
        paginator = Paginator(machines, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'search_query': search_query,
            'page_obj': page_obj ,
            'maintenances': maintenances,  # Переименовано для соответствия шаблону
            'claims': claims,              # Переименовано для соответствия шаблону
            'user_groups': list(request.user.groups.values_list('name', flat=True)),
            'is_manager': is_manager,
            'is_service_organization': is_service_organization,
        }
        return render(request, 'home_auth.html', context)
    
    # Для неавторизованных - только поиск без фильтрации
    else:
        machines = Machine.objects.all()  # Получаем все машины
        if search_query:
            machines = machines.filter(serial_number__icontains=search_query)

        print(f"Найдено {machines.count()} машин для запроса '{search_query}'")  # Отладочное сообщение

        # Пагинация
        paginator = Paginator(machines, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)    
            
        context = {
            'machines': machines,  # Для отладки
            'search_query': search_query,
            'page_obj': page_obj
        }
        return render(request, 'home.html', context)


def role_required(*roles):
    """
    Декоратор для проверки ролей пользователя.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name__in=roles).exists():
                raise PermissionDenied("У вас нет прав для доступа к этой странице.")
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def clean_organization_name(name):
    """
    Приводит название организации к единому формату для сравнения.
    """
    if not name:
        return ""
    
    # Удаляем кавычки и лишние пробелы
    name = name.replace('"', '').replace("'", "").strip()
    return ' '.join(name.split())

def get_machines_for_user(user):
    """Возвращает queryset машин в зависимости от роли пользователя."""
    if user.is_superuser or user.groups.filter(name='Менеджер').exists():
        print("Superuser/Manager - all machines")
        return Machine.objects.all()

    if user.groups.filter(name='Клиент').exists():
        try:
            client = Client.objects.get(user=user)
            print(f"Found client: {client.name}")
            return Machine.objects.filter(client=client)
        except Client.DoesNotExist:
            print(f"Client not found for user {user.username}")
            org_name = user.first_name or user.username
            cleaned_name = clean_organization_name(org_name)
            print(f"Searching by org name: '{cleaned_name}'")
            machines = Machine.objects.filter(
                Q(client__name__icontains=cleaned_name) | 
                Q(recipient__icontains=cleaned_name))
            print(f"Found {machines.count()} machines by org name")
            return machines

    if user.groups.filter(name='Сервисная организация').exists():
        try:
            service_org = ServiceOrganization.objects.get(user=user)
            print(f"Found service org: {service_org.name}")
            return Machine.objects.filter(service_company=service_org)
        except ServiceOrganization.DoesNotExist:
            print(f"Service org not found for user {user.username}")
            return Machine.objects.none()

    print("Regular user - returning first 10 machines")
    return Machine.objects.all()  
    
@login_required
def machine_list(request):
    user = request.user
    logger.info(f"Обработка запроса для пользователя: {user.username}")

    # Получаем queryset с учётом прав
    machines = get_machines_for_user(user).select_related(
        'model',
        'client',
        'service_organization',
        'engine_model',
        'transmission_model',
        'axle_model',
        'steering_axle_model'
    ).order_by('-shipment_date')

    print(f"Найдено машин: {machines.count()}")  # Логирование

    # Применяем фильтр
    machine_filter = MachineFilter(request.GET, queryset=machines)
    filtered_machines = machine_filter.qs

    # Пагинация
    paginator = Paginator(filtered_machines, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(1)

        # Получаем все справочные данные
    references = Reference.objects.all()  # Получаем все записи из справочника

    context = {
        'machines': page_obj,
        'filter': machine_filter,
        'user_groups': list(user.groups.values_list('name', flat=True)),
        'references': references,  # Передаем справочные данные в контекст
    }

    return render(request, 'home_auth.html', context)


@login_required
def machine_detail(request, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)
    
    # Оптимизированные запросы с select_related
    maintenances = TechnicalMaintenance.objects.filter(machine_id=machine_id)\
        .select_related('service_type', 'service_organization')
    
    claims = Claim.objects.filter(machine_id=machine_id)\
        .select_related('failure_node', 'recovery_method', 'service_company')
    

    print(f"Количество технического обслуживания: {maintenances.count()}")
    print(f"Количество рекламаций: {claims.count()}")
    # Отладочный вывод
    print(f"Maintenances for machine {machine_id}:")
    for m in maintenances:
        print(f"- {m.service_type} on {m.maintenance_date}")
    
    print(f"\nClaims for machine {machine_id}:")
    for c in claims:
        print(f"- {c.failure_node} on {c.rejection_date}")
    
    return render(request, 'machine_detail.html', {
        'machine': machine,
        'maintenances': maintenances,
        'claims': claims,
    })

@login_required
def add_machine(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Перенаправление на главную страницу или список машин
    else:
        form = MachineForm()
    
    # Получаем все значения для справочников
    references = Reference.objects.all()
    clients = Client.objects.all()
    service_companies = ServiceOrganization.objects.all()

    return render(request, 'add_machine.html', {
        'form': form,
        'references': references,
        'clients': clients,
        'service_companies': service_companies,
    })

@csrf_exempt
@require_POST
def add_reference(request):
    entity_name = request.POST.get('entity')
    reference_name = request.POST.get('name')
    
    if not entity_name or not reference_name:
        return JsonResponse({'error': 'Не указана сущность или название'}, status=400)
    
    try:
        entity = Entity.objects.get(name=entity_name)
        reference = Reference.objects.create(
            entity=entity,
            name=reference_name,
            description=f"Автоматически создано из формы"
        )
        return JsonResponse({
            'id': reference.id,
            'name': reference.name,
            'text': reference.name  # Для Select2
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def add_maintenance(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('home') + '#tab2')
    else:
        form = MaintenanceForm()

    return render(request, 'add_maintenance.html', {
        'form': form,
    })   

@login_required
def add_claim(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            form.save()
             # Перенаправляем на главную с параметром активной вкладки
            return redirect(reverse('home') + '#tab3')
    else:
        form = ClaimForm()

    return render(request, 'add_claim.html', {
        'form': form,
    })   

@role_required('Менеджер')
def edit_reference(request):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Справочник успешно обновлен!')
                return redirect('machine_list')
            except Exception as e:
                logger.error(f"Ошибка при сохранении справочника: {e}")
                messages.error(request, 'Произошла ошибка при сохранении справочника.')
    else:
        form = ReferenceForm()

    return render(request, 'edit_reference.html', {'form': form})

def reference_view(request):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reference_list')  # Перенаправление на список справочников или другой адрес
    else:
        form = ReferenceForm()

    references = Reference.objects.all()  # Получаем все справочники для отображения

    return render(request, 'reference_form.html', {'form': form, 'references': references})


def auth_view(request):
    if request.method == 'POST':
        form = CustomAuthForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Переход на главную страницу
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomAuthForm()
    
    return render(request, 'auth.html', {'form': form})

def reg_view(request):
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            organization = form.cleaned_data['organization']
            status = form.cleaned_data['status']
            
            # Отправка электронной почты
            send_mail(
                'Новая заявка на авторизацию',
                f'Наименование организации: {organization}\nСтатус: {status}',
                'your_email@example.com',  # Отправитель
                ['admin@example.com'],  # Получатель
                fail_silently=False,
            )
            messages.success(request, 'Заявка успешно отправлена!')  # Успешное сообщение
            return redirect('success')  # Переход на страницу успеха
    else:
        form = RegForm()
    
    return render(request, 'reg.html', {'form': form})

def success_view(request):
    return render(request, 'success.html')  # Создайте шаблон success.html

def claim_list(request):
    claims = Claim.objects.all()
    return render(request, 'claim_list.html', {'claims': claims})


def custom_logout(request):
    logout(request)
    return redirect('home')


class MachineList(generics.ListAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

class MaintenanceList(generics.ListAPIView):
    queryset = TechnicalMaintenance.objects.all()
    serializer_class = MaintenanceSerializer

class ClaimList(generics.ListAPIView):
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

def api_page(request):
    return render(request, 'api_page.html')  # Укажите имя вашего шаблона
