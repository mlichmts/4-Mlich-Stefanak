from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegisterForm

def register(request):
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Účet bol vytvorený. Vitaj, {user.username}!')
            return redirect('task_list')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})