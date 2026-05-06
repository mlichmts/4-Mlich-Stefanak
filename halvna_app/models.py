from django.db import models
from django.contrib.auth.models import User


# =========================
# CATEGORY
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=30, blank=True, null=True)  # napr. "#ff0000"

    def __str__(self):
        return self.name


# =========================
# GROUP
# =========================
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        User,
        through='GroupMembership',
        related_name='student_groups'
    )

    def __str__(self):
        return self.name


# =========================
# M:N TABLE (User ↔ Group)
# =========================
class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


# =========================
# TASK
# =========================
class Task(models.Model):

    PRIORITY_CHOICES = [
        ('nízka', 'Nízka'),
        ('stredná', 'Stredná'),
        ('vysoká', 'Vysoká'),
    ]

    STATUS_CHOICES = [
        ('spraviť', 'Spraviť '),
        ('in_progress', 'In progress'),
        ('hotová', 'Hotová'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='stredná'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='spraviť'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title