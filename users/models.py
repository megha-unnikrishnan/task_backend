from django.contrib.auth.models import AbstractUser
from django.db import models
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    dob = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    def __str__(self):
        return self.username





class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(
        'CustomUser',  # Refers to the CustomUser model
        on_delete=models.CASCADE,  # Deletes tasks if the associated user is deleted
        related_name='tasks' ,null=True # Allows reverse lookup from the user object
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True,auto_now=True)

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure the notify_task_update is properly awaited in an async context
        if self.pk:  # If the task is already saved
            self.notify_task_update()

    @database_sync_to_async
    def notify_task_update(self):
        # Avoid using async_to_sync here since it's inside an async function
        # Directly call the async group_send function
        channel_layer = get_channel_layer()
        group_name = "task_updates_tasks_room"
        # Send task update message to the WebSocket group
        channel_layer.group_send(
            group_name,
            {
                "type": "task_update",
                "message": f"Task {self.title} has been updated"
            }
        )