from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Task, Category

@login_required
def task_list(request):
    if request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(user=request.user)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks})


@login_required
def task_create(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        Task.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description'),
            due_date=request.POST.get('due_date'),
            priority=request.POST.get('priority'),
            status=request.POST.get('status'),
            category_id=request.POST.get('category'),
            user=request.user
        )
        return redirect('task_list')

    return render(request, 'tasks/task_form.html', {
        'categories': categories
    })