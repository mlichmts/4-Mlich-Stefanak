from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Task, Category, Group, GroupMembership

@login_required
def task_list(request):
    if request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        user_groups = request.user.student_groups.all()
        tasks = Task.objects.filter(
            Q(user=request.user) | Q(group__in=user_groups)
        ).distinct()

    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    categories = Category.objects.all()
    user_groups = request.user.student_groups.all()

    if request.method == 'POST':
        Task.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description'),
            due_date=request.POST.get('due_date'),
            priority=request.POST.get('priority'),
            status=request.POST.get('status'),
            category_id=request.POST.get('category') or None,
            group_id=request.POST.get('group') or None,
            user=request.user
        )
        return redirect('task_list')

    return render(request, 'tasks/task_form.html', {
        'categories': categories,
        'groups': user_groups,
    })


@login_required
def group_list(request):
    all_groups = Group.objects.all()
    my_groups = request.user.student_groups.all()
    return render(request, 'tasks/group_list.html', {
        'all_groups': all_groups,
        'my_groups': my_groups,
    })


@login_required
def group_join(request, group_id):
    group = Group.objects.get(id=group_id)
    GroupMembership.objects.get_or_create(
        user=request.user,
        group=group,
        defaults={'role': 'member'}
    )
    return redirect('task_list')


@login_required
def group_leave(request, group_id):
    GroupMembership.objects.filter(
        user=request.user,
        group_id=group_id
    ).delete()
    return redirect('task_list')


@login_required
def group_create(request):
    all_users = User.objects.exclude(id=request.user.id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        member_ids = request.POST.getlist('members')

        group = Group.objects.create(name=name, description=description)
        GroupMembership.objects.create(user=request.user, group=group, role='admin')

        for user_id in member_ids:
            user = User.objects.get(id=user_id)
            GroupMembership.objects.create(user=user, group=group, role='member')

        

    return render(request, 'tasks/group_create.html', {
        'all_users': all_users,
    })