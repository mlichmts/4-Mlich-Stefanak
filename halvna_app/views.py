from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Task, Category, Group, GroupMembership
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User


from django.utils import timezone
import datetime
@login_required
def group_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    memberships = GroupMembership.objects.filter(group=group)

    # 1. KONTROLA: Zistíme, kto je zakladateľom/vlastníkom skupiny
    # Hľadáme záznam, kde je rola nastavená na 'admin' (alebo 'owner'/'creator' podľa tvojho uváženia)
    owner_membership = memberships.filter(role='admin').first()
    group_owner = owner_membership.user if owner_membership else None

    # OCHRANA: Ak sa niekto pokúša upraviť skupinu, ktorú nevytvoril
    # (Dovolíme to iba vlastníkovi skupiny alebo superuserovi/adminovi systému)
    if group_owner and request.user != group_owner and not request.user.is_superuser:
        raise PermissionDenied("Môžeš upravovať iba skupiny, ktoré si sám vytvoril.")

    if request.method == 'POST':
        group.name = request.POST.get('name')
        group.description = request.POST.get('description')
        group.save()

        # OCHRANA: Zmaž všetkých členov, ale EXCLUDE (vynechaj) pôvodného zakladateľa skupiny!
        # Týmto zabezpečíš, že zakladateľ zostane v skupine navždy, aj keby ho niekto vynechal vo formulári
        if group_owner:
            GroupMembership.objects.filter(group=group).exclude(user=group_owner).delete()
        else:
            # Záložný plán, ak by skupina nemala admina (napr. staré dáta) - vymaže všetkých okrem odosielateľa
            GroupMembership.objects.filter(group=group).exclude(user=request.user).delete()

        # Pridaj nových členov z formulára
        usernames = request.POST.getlist('member_usernames')
        not_found = []
        for username in usernames:
            username = username.strip()
            if not username:
                continue
            try:
                user = User.objects.get(username=username)
                
                # Pridávame nového člena iba vtedy, ak to nie je samotný vlastník skupiny
                # (keďže toho sme hore nevymazali a nechceme duplicitné záznamy)
                if user != group_owner:    
                    GroupMembership.objects.get_or_create(
                        user=user, 
                        group=group, 
                        defaults={'role': 'member'}
                    )
            except User.DoesNotExist:
                not_found.append(username)

        if not_found:
            # Po chybe musíme znova vytiahnuť aktuálne memberships pre šablónu
            return render(request, 'tasks/group_edit.html', {
                'group': group,
                'memberships': GroupMembership.objects.filter(group=group),
                'error': f'Nenájdení: {", ".join(not_found)}'
            })

        return redirect('task_list')

    return render(request, 'tasks/group_edit.html', {
                'group': group,
                'memberships': memberships,
    })

@login_required
def task_list(request):
    if request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        user_groups = request.user.student_groups.all()
        tasks = Task.objects.filter(
            Q(user=request.user) | Q(group__in=user_groups)
        ).distinct()

    # Filtrovanie
    status   = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    due      = request.GET.get('due')
    sort     = request.GET.get('sort', '')
    
    if sort == 'due_asc':
        tasks = tasks.order_by('due_date')
    elif sort == 'due_desc':
        tasks = tasks.order_by('-due_date')
        
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if category:
        tasks = tasks.filter(category_id=category)
    if due == 'today':
        tasks = tasks.filter(due_date=timezone.now().date())
    elif due == 'week':
        today = timezone.now().date()
        tasks = tasks.filter(due_date__range=[today, today + datetime.timedelta(days=7)])
    elif due == 'overdue':
        tasks = tasks.filter(due_date__lt=timezone.now().date()).exclude(status='hotová')

    categories = Category.objects.all()

    # --- ÚPRAVA PRE SKUPINY ---
    if request.user.is_superuser:
        # Superuser (Hlavný admin stránky) uvidí a môže upravovať úplne všetky skupiny
        user_groups_to_edit = Group.objects.all()
    else:
        # Bežný používateľ uvidí IBA tie skupiny, kde je v prepojovacej tabuľke označený ako 'admin'
        user_groups_to_edit = Group.objects.filter(
            groupmembership__user=request.user,
            groupmembership__role='admin'
        )
    # ---------------------------

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'categories': categories,
        'current_status': status or '',
        'current_priority': priority or '',
        'current_category': category or '',
        'current_due': due or '',
        'current_sort': sort,
        # Sem dosadíme náš nový očistený zoznam skupín
        'user_groups': user_groups_to_edit, 
    })


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
def task_edit(request, task_id):
    task = Task.objects.get(id=task_id)
    categories = Category.objects.all()
    user_groups = request.user.student_groups.all()

    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST.get('description')
        
        due_date = request.POST.get('due_date')
        if due_date:  # ak je vyplnený, zmeň ho, inak ponechaj pôvodný
            task.due_date = due_date
            
        task.priority = request.POST.get('priority')
        task.status = request.POST.get('status')
        task.category_id = request.POST.get('category') or None
        task.group_id = request.POST.get('group') or None
        task.save()
        return redirect('task_list')

    return render(request, 'tasks/task_edit.html', {
        'task': task,
        'categories': categories,
        'groups': user_groups,
    })


@login_required
def task_delete(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect('task_list')


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

        return redirect('task_list')

    return render(request, 'tasks/group_create.html', {
        'all_users': all_users,
    })