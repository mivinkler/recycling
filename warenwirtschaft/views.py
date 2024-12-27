from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.db.models import Q


def eingang(request):
    suppliers = Supplier.objects.all()
    devices = Device.objects.all()

    ladungstraeger_anzahl = 1

    if request.method == 'POST':
        ladungstraeger_anzahl = int(request.POST.get('ladungstraeger_anzahl', 1))

        if ladungstraeger_anzahl > 10:
            ladungstraeger_anzahl = 10

    range_10 = range(ladungstraeger_anzahl)

    return render(request, 'warenwirtschaft/eingang.html', {'ladungstraeger_anzahl': ladungstraeger_anzahl, 'range_10': range_10, 'suppliers': suppliers, 'devices': devices})

def suppliers(request):
    suppliers = Supplier.objects.all()

    paginator = Paginator(suppliers, 22)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'warenwirtschaft/suppliers.html', {'page_obj': page_obj})

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'supplier_update.html', {'form': form, 'supplier': supplier})

def supplier_deliveries(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    deliveries = Delivery.objects.filter(supplier=supplier).select_related('device')

    paginator = Paginator(deliveries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'supplier_deliveries.html',
        {'supplier': supplier, 'page_obj': page_obj}
    )

def delivery(request):
    deliveries = Delivery.objects.prefetch_related(
        Prefetch('deliveryunits_set', queryset=DeliveryUnits.objects.all())
    )

    paginator = Paginator(deliveries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'warenwirtschaft/delivery.html', {'page_obj': page_obj})



from django.db.models import Q

def delivery_units(request):
    # Base queryset
    queryset = DeliveryUnits.objects.all()

    # Filtering
    filter_mapping = {
        'id': 'id',
        'delivery': 'delivery__id',
        'delivery_date': 'delivery__delivery_date',
        'delivery_id': 'delivery_receipt__icontains',
        'delivery_type': 'delivery_type',
        'device': 'device__name__icontains',
        'weight': 'weight',
        'status': 'status',
        'note': 'note__icontains',
    }
    filters = {
        field: request.GET[param]
        for param, field in filter_mapping.items()
        if request.GET.get(param)
    }
    queryset = queryset.filter(Q(**filters)) if filters else queryset

    # Sorting
    sort_mapping = {
        'id_asc': 'id', 'id_desc': '-id',
        'delivery_asc': 'delivery__id', 'delivery_desc': '-delivery__id',
        'date_asc': 'delivery__delivery_date', 'date_desc': '-delivery__delivery_date',
        'lid_asc': 'delivery_receipt', 'lid_desc': '-delivery_receipt',
        'container_asc': 'delivery_type', 'container_desc': '-delivery_type',
        'device_asc': 'device__name', 'device_desc': '-device__name',
        'weight_asc': 'weight', 'weight_desc': '-weight',
        'status_asc': 'status', 'status_desc': '-status',
        'note_asc': 'note', 'note_desc': '-note',
    }
    sort_field = sort_mapping.get(request.GET.get('sort', 'id_asc'), 'id')
    queryset = queryset.order_by(sort_field)

    # Pagination
    paginator = Paginator(queryset, 21)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Context
    context = {
        'page_obj': page_obj,
        'delivery_types': DeliveryUnits.DELIVERY_TYPE_CHOICES,
        'statuses': DeliveryUnits.STATUS_CHOICES,
    }

    return render(request, 'warenwirtschaft/delivery_units.html', context)
