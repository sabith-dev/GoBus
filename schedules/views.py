from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Schedule
from .forms import ScheduleForm


@login_required
def schedule_list_view(request):
    schedules = Schedule.objects.filter(bus__agency=request.user)
    return render(request, 'schedules/list.html', {'schedules': schedules})


@login_required
def schedule_create_view(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule created successfully!')
            return redirect('schedules:schedule_list')
    else:
        form = ScheduleForm()
    return render(request, 'schedules/create.html', {'form': form})


@login_required
def schedule_update_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, bus__agency=request.user)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('schedules:schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'schedules/update.html', {'form': form, 'schedule': schedule})


@login_required
def schedule_delete_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, bus__agency=request.user)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('schedules:schedule_list')
    return render(request, 'schedules/delete.html', {'schedule': schedule})
