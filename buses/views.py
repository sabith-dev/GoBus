from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Bus, BusType, Seat
from .forms import BusForm, BusTypeForm


@login_required
def bus_list_view(request):
    buses = Bus.objects.filter(agency=request.user)
    return render(request, 'buses/list.html', {'buses': buses})


@login_required
def bus_create_view(request):
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save(commit=False)
            bus.agency = request.user
            bus.save()
            messages.success(request, 'Bus created successfully!')
            return redirect('buses:bus_list')
    else:
        form = BusForm()
    return render(request, 'buses/create.html', {'form': form})


@login_required
def bus_detail_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id, agency=request.user)
    seats = bus.seats.all()
    return render(request, 'buses/detail.html', {'bus': bus, 'seats': seats})


@login_required
def bus_update_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id, agency=request.user)
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('buses:bus_detail', bus_id=bus.id)
    else:
        form = BusForm(instance=bus)
    return render(request, 'buses/update.html', {'form': form, 'bus': bus})


@login_required
def bus_delete_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id, agency=request.user)
    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Bus deleted successfully!')
        return redirect('buses:bus_list')
    return render(request, 'buses/delete.html', {'bus': bus})
