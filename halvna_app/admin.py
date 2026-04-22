from django.contrib import admin
from .models import Task, Group, Category, GroupMembership

admin.site.register(Task)
admin.site.register(Group)
admin.site.register(Category)
admin.site.register(GroupMembership)