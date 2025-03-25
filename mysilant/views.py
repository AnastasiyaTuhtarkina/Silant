# Стандартные библиотеки
import logging
from functools import wraps

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

# Локальные импорты
from .filters import MachineFilter, MaintenanceFilter, ClaimFilter
from .models import Machine, TechnicalMaintenance, Claim, Reference, Client, ServiceOrganization
from .forms import *


logger = logging.getLogger(__name__)
def home(request):
    search_query = request.GET.get('search', '')
    machines = Machine.objects.filter(serial_number__icontains=search_query).order_by('shipment_date')
    maintenances = TechnicalMaintenance.objects.filter().order_by('maintenance_date')
    claims = Claim.objects.filter().order_by('rejection_date')

      # Пагинация
    paginator = Paginator(machines, 10)  # 10 машин на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    logger.info("Home view accessed")

      # Проверяем, авторизован ли пользователь
    if request.user.is_authenticated:
        # Логика для зарегистрированных пользователей
        context = {
            'search_query': search_query,
            'page_obj': page_obj,
            'user_machines': machines,  # Пример: передаем все машины для зарегистрированных пользователей
            'user_maintenances': maintenances,  # Пример: передаем все запланированные ремонты для зарегистрированных пользователей
            'user_claims': claims,  # Пример: передаем все заявки на ремонты для зарегистрированных пользователей
        }
        return render(request, 'home_auth.html', context)  # Шаблон для зарегистрированных пользователей
    else:
        # Логика для незарегистрированных пользователей
        context = {
            'search_query': search_query,
            'page_obj': page_obj,
        }
        return render(request, 'home.html', context)  # Шаблон для незарегистрированных пользователей


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

@login_required
def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    return render(request, 'machine_detail.html', {'machine': machine})

def get_client_for_user(user):
    try:
        return Client.objects.get(user=user)
    except ObjectDoesNotExist:
        return None
def get_machines_for_user(user):
    """
    Возвращает queryset машин в зависимости от роли пользователя.
    
    :param user: Пользователь, для которого нужно получить машины.
    :return: QuerySet машин, доступных для данного пользователя.
    """
    # # Константы для групп
    # MANAGER_GROUP = 'Менеджер'
    # CLIENT_GROUP = 'Клиент'
    # SERVICE_GROUP = 'Сервисная организация'
    
    # user_groups = set(user.groups.values_list('name', flat=True))

    # if MANAGER_GROUP in user_groups:
    #     return Machine.objects.all()
    
    # if CLIENT_GROUP in user_groups:
    #     try:
    #         # Получаем клиента, связанного с пользователем
    #         # Предполагаем, что у модели Client есть поле user
    #         client = Client.objects.get(user=user)
    #         return Machine.objects.filter(client=client)
    #     except ObjectDoesNotExist:
    #         # Если клиент не найден, попробуем найти через recipient
    #         try:
    #             org_name = user.first_name.strip()
    #             cleaned_org_name = clean_organization_name(org_name)
    #             return Machine.objects.filter(recipient__icontains=cleaned_org_name)
    #         except Exception as e:
    #             print(f"Ошибка при получении машин для клиента {user}: {e}")
    #             return Machine.objects.none()
            
    # 1. Для менеджеров и суперпользователей - все машины
    if user.is_superuser or user.groups.filter(name='Менеджер').exists():
        print("Доступ: менеджер/админ - все машины")
        return Machine.objects.all()

    # 2. Для клиентов
    if user.groups.filter(name='Клиент').exists():
        print("Доступ: клиент - поиск машин")
        
        # Вариант 1: Через явную связь Client -> User
        if hasattr(user, 'client'):
            print(f"Найден клиент: {user.client}")
            return Machine.objects.filter(client=user.client)
        
        # Вариант 2: Через соответствие имени
        org_names = [
            user.first_name,
            user.username,
            getattr(user, 'client_name', '')  # Если есть дополнительное поле
        ]
        
        # Фильтруем непустые значения и чистим
        org_names = [clean_organization_name(name) for name in org_names if name]
        
        print(f"Поиск по именам организаций: {org_names}")
        
        # Создаём условия для поиска
        conditions = Q()
        for name in org_names:
            conditions |= Q(client__name__icontains=name) | Q(recipient__icontains=name)
        
        return Machine.objects.filter(conditions)
    
     # 3. Для сервисных организаций
    if user.groups.filter(name='Сервисная организация').exists():
        print("Доступ: сервисная организация")
        return Machine.objects.filter(service_organization__user=user)
    
    # if SERVICE_GROUP in user_groups:
    #     # Более надёжный способ определения сервисной компании
    #     try:
    #         service_company = ServiceOrganization.objects.get(user=user)
    #         return Machine.objects.filter(service_company=service_company)
    #     except ObjectDoesNotExist:
    #         return Machine.objects.none()
    
    # Для пользователей без специальных прав
    return Machine.objects.all()[:10]

def clean_organization_name(name):
    """
    Приводит название организации к единому формату для сравнения.
    """
    if not name:
        return ""
    
    # Удаляем кавычки и лишние пробелы
    name = name.replace('"', '').replace("'", "").strip()
    return ' '.join(name.split())
    
@login_required
def machine_list(request):
    user = request.user
    print(f"Обработка запроса для пользователя: {user.username}")  # Логирование

    # Получаем queryset с учётом прав
    machines = get_machines_for_user(user).select_related(
        'model',
        'client',
        'service_organization'
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

    context = {
        'machines': page_obj,
        'filter': machine_filter,
        'user_groups': list(user.groups.values_list('name', flat=True))
    }

    return render(request, 'home_auth.html', context)

    # Получаем queryset в зависимости от прав пользователя
    # machines = get_machines_for_user(user).select_related('client', 'service_organization')

    # # Применяем фильтр и сортировку
    # machine_filter = MachineFilter(request.GET, queryset=machines)
    # machines = machine_filter.qs.order_by('-shipment_date')

    #   # Пагинация
    # paginator = Paginator(machines, 10)  # 10 машин на страницу
    # page_number = request.GET.get('page')

    # try:
    #     page_obj = paginator.get_page(page_number)
    # except EmptyPage:
    #     page_obj = paginator.get_page(paginator.num_pages)  # Redirect to last page if out of

    # # Передаем данные в шаблон
    # return render(request, 'home_auth.html', {'machines': page_obj, 'filter': machine_filter})


def machine_search(request):
    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        try:
            machine = Machine.objects.get(serial_number=serial_number)
            return render(request, 'machine_detail.html', {'machine': machine})
        except Machine.DoesNotExist:
            return render(request, 'machine_search.html', {'error': 'Машина с таким заводским номером не найдена'})
    return render(request, 'machine_search.html')

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

@method_decorator(role_required('Менеджер'), name='dispatch')
class MachineUpdateView(UpdateView):
    model = Machine
    fields = ['serial_number', 'model', 'engine_model', 'shipment_date']
    template_name = 'machine_edit.html'
    # success_url = reverse('machine_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Менеджер').exists():
            raise PermissionDenied("У вас нет прав для редактирования этой машины.")
        return super().dispatch(request, *args, **kwargs)

@login_required
def maintenance_list_view(request):
    user = request.user

    # Получаем queryset в зависимости от прав пользователя
    maintenances = get_machines_for_user(user).select_related('client', 'service_organization')

    # Применяем фильтр и сортировку
    maintenance_filter = MaintenanceFilter(request.GET, queryset=TechnicalMaintenance.objects.all())
    maintenances = maintenance_filter.qs.order_by('-maintenance_date')

      # Пагинация
    paginator = Paginator(maintenances, 10) 
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)  # Redirect to last page if out of

    # Передаем данные в шаблон
    return render(request, 'maintenance_list.html', {'maintenances': page_obj, 'filter': maintenance_filter})



# Добавление представлений для ТО и рекламаций
@login_required
def maintenance_view(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    print(f":User  {request.user}, Machine: {machine}")

    if not (request.user.groups.filter(name='Клиент').exists() and machine.client == request.user) and \
       not (request.user.groups.filter(name='Сервисная организация').exists() and machine.service_organization == request.user):
        raise PermissionDenied("У вас нет прав для доступа к этому ТО.")

    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.machine = machine
            maintenance.save()
            return redirect('machine_detail', pk=machine.pk)
    else:
        form = MaintenanceForm()

    return render(request, 'maintenance_form.html', {'form': form, 'machine': machine})

@login_required
def claim_view(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if not (request.user.groups.filter(name='Клиент').exists() and machine.client == request.user) and \
       not (request.user.groups.filter(name='Сервисная организация').exists() and machine.service_organization == request.user):
        raise PermissionDenied("У вас нет прав для доступа к этой рекламации.")

    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.machine = machine
            complaint.save()
            return redirect('machine_detail', pk=machine.pk)
    else:
        form = ClaimForm()

    return render(request, 'claim_form.html', {'form': form, 'machine': machine})

class TechnicalMaintenanceUpdateView(UpdateView):
    model = TechnicalMaintenance
    fields = ['machine', 'service_type', 'maintenance_date', 'operating_hours']
    template_name = 'technical_maintenance_edit.html'
    # success_url = '/technical_maintenances/'

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является менеджером или сервисной организацией
        if not (request.user.groups.filter(name='Менеджер').exists() or
                request.user.groups.filter(name='Сервисная организация').exists()):
            raise PermissionDenied("У вас нет прав для редактирования этого ТО.")
        return super().dispatch(request, *args, **kwargs)
    
class ClaimUpdateView(UpdateView):
    model = Claim
    fields = ['machine', 'rejection_date', 'operating_hours', 'failure_node', 'recovery_method']
    template_name = 'claim_edit.html'
    # success_url = '/claims/'

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является менеджером или сервисной организацией
        if not (request.user.groups.filter(name='Менеджер').exists() or
                request.user.groups.filter(name='Сервисная организация').exists()):
            raise PermissionDenied("У вас нет прав для редактирования этой рекламации.")
        return super().dispatch(request, *args, **kwargs)
    
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