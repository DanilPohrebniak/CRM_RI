from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms import formset_factory
from .models import  Good, Counterparty, Warehouse, Unit, Documents, Doctype, Goods_in_stock, User, Sales
from .forms import WarehouseForm, UnitForm, GoodForm, CounterpartyForm, DocumentForm, GoodsInStockForm
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')  # Redirect to your home page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('home')  # Redirect to your home page
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('home')  # Redirect to your home page

def home_view(request):
    return render(request, 'home.html')

def reference_tables(request):
    return render(request, 'reference_tables.html')

def display_table(request, model_name):
    models = {
        'warehouse': Warehouse.objects.all(),
        'unit': Unit.objects.all(),
        'good': Good.objects.all(),
        'counterparty': Counterparty.objects.all(),
    }

    if model_name not in models:
        model_name = 'warehouse'

    paginator = Paginator(models[model_name], 10)  # 10 items per page
    page = request.GET.get('page')

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'model_name': model_name,
        'items': items,
        'fields': [field.name for field in models[model_name].model._meta.fields],
        'item_fields': [{field.name: getattr(item, field.name) for field in item._meta.fields} for item in items],
    }

    return render(request, 'display_table.html', context)

def delete_item_view(request, model_name, pk):
    models = {
        'warehouse': Warehouse.objects.all(),
        'unit': Unit.objects.all(),
        'good': Good.objects.all(),
        'counterparty': Counterparty.objects.all(),
    }

    model_class = models.get(model_name)
    item = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        item.delete()
        return redirect('display_table', model_name=model_name)

def add_item_view(request, model_name):
    form_classes = {
        'warehouse': WarehouseForm,
        'unit': UnitForm,
        'good': GoodForm,
        'counterparty': CounterpartyForm,
    }

    form_class = form_classes.get(model_name)
    if form_class:
        form = form_class(request.POST or None)

        if form.is_valid():
            form.save()
            return redirect('display_table', model_name=model_name)

        template_name = 'add_item_template.html'
        return render(request, template_name, {'form': form, 'model_name': model_name})

    # Handle the case when an invalid table_name is provided
    return render(request, 'error.html', {'model_name': model_name})

def get_model_and_form(model_name):
    MODELS = {
        'warehouse': Warehouse,
        'unit': Unit,
        'good': Good,
        'counterparty': Counterparty,
    }

    FORM_CLASSES = {
        'warehouse': WarehouseForm,
        'unit': UnitForm,
        'good': GoodForm,
        'counterparty': CounterpartyForm,
    }

    model_class = MODELS.get(model_name)
    form_class = FORM_CLASSES.get(model_name)

    if not (model_class and form_class):
        return None, None

    return model_class, form_class

def edit_item_view(request, model_name, pk):
    model_class, form_class = get_model_and_form(model_name)

    if model_class is None or form_class is None:
        return HttpResponseBadRequest("Invalid model name")

    item = get_object_or_404(model_class, pk=pk)
    form = form_class(instance=item)

    if request.method == 'POST':
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('display_table', model_name=model_name)
    else:
        form = form_class(instance=item)

    return render(request, 'edit_item_template.html', {'form': form, 'model_name': model_name, 'item': item})

def display_documents(request, document_type):
    documents = Documents.objects.all()

    if document_type:
        documents = documents.filter(Doctype__name__iexact=document_type)

    paginator = Paginator(documents, 10)  # 10 items per page
    page = request.GET.get('page')

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'document_type': document_type,  # This line was missing
        'documents': items,
        'fields': [field.name for field in Documents._meta.fields],
        'document_fields': [{field.name: getattr(document, field.name) for field in document._meta.fields} for document
                            in items],
    }

    return render(request, 'display_documents.html', context)

def add_document_view(request, document_type):
    GoodsInStockFormSet = formset_factory(GoodsInStockForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = DocumentForm(request.POST, document_type=document_type)
        formset = GoodsInStockFormSet(request.POST, prefix='goods_formset')

        goods_list = request.POST.getlist('good[]')
        quantity_list = request.POST.getlist('quantity[]')
        sum_list = request.POST.getlist('sum[]')

        if form.is_valid():
            document = form.save(commit=False)
            document.save()

            # Создаем списки для данных из таблицы
            goods_list = request.POST.getlist('good[]')
            quantity_list = request.POST.getlist('quantity[]')
            sum_list = request.POST.getlist('sum[]')

            # Получаем значения из объекта Document
            document = Documents.objects.get(pk=document.id)
            warehouse = document.Warehouse
            income = document.Doctype_id  == 1

            # Обрабатываем данные из списков
            for good, quantity, sum_value in zip(goods_list, quantity_list, sum_list):
                # Преобразуем значения в нужные типы данных
                quantity = float(quantity)
                sum_value = float(sum_value)

                # Получаем или создаем объект Good по имени
                good_obj, created = Good.objects.get_or_create(name=good)

                # Получаем или создаем объект Unit по имени (предполагаем, что у Good есть поле unit)
                unit_obj, created = Unit.objects.get_or_create(name=good_obj.unit.name)

                # Создаем или обновляем объект Goods_in_stock
                goods_in_stock, created = Goods_in_stock.objects.get_or_create(
                    Document=document,
                    Good=good_obj,  # Получаем объект Good по имени
                    defaults={
                        'Date': document.Date,
                        'Unit': unit_obj,
                        'Warehouse': warehouse,
                        'Income': income,
                        'Quantity': quantity,
                        'Sum': sum_value
                    }
                )

                # Если объект уже существует, обновляем его поля
                if not created:
                    goods_in_stock.Date = document.Date
                    goods_in_stock.Unit = unit_obj
                    goods_in_stock.Warehouse = warehouse
                    goods_in_stock.Income = income
                    goods_in_stock.Quantity = quantity
                    goods_in_stock.Sum = sum_value
                    goods_in_stock.save()

                if not income:
                    sale = Sales.objects.create(
                        Date=document.Date,
                        Document=document,
                        Good=good_obj,
                        Counterparty=document.Counterparty,
                        Income=False,
                        Quantity=quantity,
                        Amount=sum_value
                    )

            return redirect('display_documents', document_type=document_type)
        else:
            # Print errors to logs
            print(form.errors, formset.errors)
    else:
        form = DocumentForm(data={'Doctype': document_type},
                            initial={'Date': timezone.now().strftime('%Y-%m-%dT%H:%M')},
                            document_type=document_type)
        formset = GoodsInStockFormSet(prefix='goods_formset')

    goods = Good.objects.all()

    if 'search' in request.GET:
        search_term = request.GET['search']
        goods = goods.filter(name__icontains=search_term)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = render(request, 'items/goods_table_ajax.html', {'goods': goods}).content
        return JsonResponse({'data': data.decode('utf-8')})

    goods_range = range(len(goods))

    context = {
        'form': form,
        'formset': formset,
        'document_type': document_type,
        'goods': goods,
        'goods_range': goods_range,
    }

    return render(request, 'add_document.html', context)

def product_search(request):
    search_term = request.GET.get('search', '')
    products = Good.objects.filter(name__icontains=search_term).values_list('name', flat=True)
    return JsonResponse(list(products), safe=False)

def edit_document_view(request, document_type=None, pk=None):
    document = get_object_or_404(Documents, pk=pk)
    goods_in_stock = Goods_in_stock.objects.filter(Document=document)
    form = DocumentForm(instance=document)

    # Получаем все доступные варианты для выбора
    all_warehouses = Warehouse.objects.all()
    all_counterparties = Counterparty.objects.all()
    all_authors = User.objects.all()
    all_doctypes = Doctype.objects.all()

    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)

        if form.is_valid():
            with transaction.atomic():  # Обеспечиваем атомарность операций
                document = form.save()  # Сохраняем документ

                # Обновляем связанные записи в табличной части
                goods_list = request.POST.getlist('good[]')
                quantity_list = request.POST.getlist('quantity[]')
                sum_list = request.POST.getlist('sum[]')

                # Получаем значения из объекта Document
                warehouse = document.Warehouse
                income = document.Doctype_id == 1

                # Обрабатываем данные из списков
                for good, quantity, sum_value in zip(goods_list, quantity_list, sum_list):
                    # Преобразуем значения в нужные типы данных
                    quantity = float(quantity)
                    sum_value = float(sum_value)

                    # Получаем или создаем объект Good по имени
                    good_obj, created = Good.objects.get_or_create(name=good)

                    # Получаем или создаем объект Unit по имени (предполагаем, что у Good есть поле unit)
                    unit_obj, created = Unit.objects.get_or_create(name=good_obj.unit.name)

                    # Создаем или обновляем объект Goods_in_stock
                    goods_in_stock, created = Goods_in_stock.objects.get_or_create(
                        Document=document,
                        Good=good_obj,  # Получаем объект Good по имени
                        defaults={
                            'Date': document.Date,
                            'Unit': unit_obj,
                            'Warehouse': warehouse,
                            'Income': income,
                            'Quantity': quantity,
                            'Sum': sum_value
                        }
                    )

                    # Если объект уже существует, обновляем его поля
                    if not created:
                        goods_in_stock.Date = document.Date
                        goods_in_stock.Unit = unit_obj
                        goods_in_stock.Warehouse = warehouse
                        goods_in_stock.Income = income
                        goods_in_stock.Quantity = quantity
                        goods_in_stock.Sum = sum_value
                        goods_in_stock.save()

                    if not income:
                        sale = Sales.objects.create(
                            Date=document.Date,
                            Document=document,
                            Good=good_obj,
                            Counterparty=document.Counterparty,
                            Income=False,
                            Quantity=quantity,
                            Amount=sum_value
                        )

            return redirect('display_documents', document_type=document_type)

    context = {
        'form': form,
        'document_type': document_type,
        'document': document,
        'all_warehouses': all_warehouses,
        'all_counterparties': all_counterparties,
        'all_authors': all_authors,
        'goods_in_stock': goods_in_stock,
        'all_doctypes': all_doctypes,
    }

    return render(request, 'edit_document.html', context)

def delete_document_view(request, document_type=None, pk=None):
    document = get_object_or_404(Documents, pk=pk)

    if request.method == 'POST':
        document.delete()
        return redirect('display_documents', document_type=document_type)

    context = {
        'document_type': document_type,
        'document': document,
    }

    return render(request, 'delete_document.html', context)

def inventory_view(request):
    if request.method == 'POST' and 'good_id' in request.POST:
        good_id = request.POST['good_id']
        goods_info = Goods_in_stock.objects.filter(Good_id=good_id).order_by('-Date')

        additional_info = []

        for info in goods_info:
            additional_info.append({
                'quantity': info.Quantity,
                'income': 'Income' if info.Income else 'Expense',
                'doc': info.Document_id,  # Используем только идентификатор документа
                'date': info.Date
            })

        return JsonResponse(additional_info, safe=False)
    else:
        goods = Good.objects.all()
        goods_balance = []

        for good in goods:
            total_income = \
                Goods_in_stock.objects.filter(Good=good, Income=True).aggregate(total_income=Sum('Quantity'))[
                    'total_income'] or 0
            total_expense = \
                Goods_in_stock.objects.filter(Good=good, Income=False).aggregate(total_expense=Sum('Quantity'))[
                    'total_expense'] or 0
            balance = total_income - total_expense

            goods_balance.append({
                'good': good,
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance
            })

        context = {
            'goods_balance': goods_balance,
        }

        return render(request, 'inventory.html', context)