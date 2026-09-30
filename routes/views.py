from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Route, RouteStop
from .forms import RouteForm, RouteStopForm


@login_required
def route_list_view(request):
    routes = Route.objects.filter(agency=request.user)
    return render(request, 'routes/list.html', {'routes': routes})


@login_required
def route_create_view(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.agency = request.user
            route.save()
            messages.success(request, 'Route created successfully!')
            return redirect('routes:route_list')
    else:
        form = RouteForm()
    return render(request, 'routes/create.html', {'form': form})


@login_required
def route_update_view(request, route_id):
    route = get_object_or_404(Route, id=route_id, agency=request.user)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('routes:route_list')
    else:
        form = RouteForm(instance=route)
    return render(request, 'routes/update.html', {'form': form, 'route': route})


@login_required
def route_delete_view(request, route_id):
    route = get_object_or_404(Route, id=route_id, agency=request.user)
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
        return redirect('routes:route_list')
    return render(request, 'routes/delete.html', {'route': route})
