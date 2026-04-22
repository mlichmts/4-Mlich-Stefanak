from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Task

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        Task.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description'),
            due_date=request.POST['due_date'],
            user=request.user
        )
        return redirect('task_list')

    return render(request, 'tasks/task_form.html')