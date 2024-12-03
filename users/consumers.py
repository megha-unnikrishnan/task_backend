# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from django.contrib.auth.models import AnonymousUser
# from .models import Task


# class TaskConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         print(f"Attempting connection: User - {self.scope['user']}")
#         # Ensure the user is authenticated
#         if self.scope['user'] == AnonymousUser():
#             print("Connection rejected: Anonymous user.")
#             await self.close()
#         else:
#             self.user = self.scope['user']
#             self.group_name = f"user_{self.user.id}_tasks"
#             print(f"User {self.user} connected, joining group {self.group_name}")

#             # Join task group
#             if not self.channel_layer:
#                 print("Channel layer is not configured.")
#                 await self.close()
#                 return

#             await self.channel_layer.group_add(
#                 self.group_name,
#                 self.channel_name
#             )
#             await self.accept()

#     async def disconnect(self, close_code):
#         print(f"Disconnecting user {self.user} from group {self.group_name}")
#         if self.channel_layer:
#             await self.channel_layer.group_discard(
#                 self.group_name,
#                 self.channel_name
#             )

#     async def receive(self, text_data):
#         print(f"Received message: {text_data}")
#         try:
#             data = json.loads(text_data)
#         except json.JSONDecodeError:
#             print("Invalid JSON received.")
#             await self.send(json.dumps({'error': 'Invalid JSON'}))
#             return

#         action = data.get('action')
#         if action == 'create':
#             print("Create task action received.")
#             await self.create_task(data)
#         elif action == 'update':
#             print("Update task action received.")
#             await self.update_task(data)
#         elif action == 'delete':
#             print("Delete task action received.")
#             await self.delete_task(data)
#         else:
#             print(f"Invalid action received: {action}")
#             await self.send(json.dumps({'error': 'Invalid action'}))

#     @sync_to_async
#     def create_task(self, data):
#         print(f"Creating task for user {self.user}: {data}")
#         task = Task.objects.create(
#             user=self.user,
#             title=data['title'],
#             description=data.get('description', ''),
#             status=data.get('status', 'Pending'),
#             due_date=data.get('due_date', None)
#         )
#         print(f"Task created: {task}")
#         # Broadcast the new task
#         return task

#     @sync_to_async
#     def update_task(self, data):
#         print(f"Updating task for user {self.user}: {data}")
#         task_id = data.get('id')
#         try:
#             task = Task.objects.get(id=task_id, user=self.user)
#             task.title = data.get('title', task.title)
#             task.description = data.get('description', task.description)
#             task.status = data.get('status', task.status)
#             task.due_date = data.get('due_date', task.due_date)
#             task.save()
#             print(f"Task updated: {task}")
#             return task
#         except Task.DoesNotExist:
#             print(f"Task with ID {task_id} does not exist for user {self.user}")
#             return None

#     @sync_to_async
#     def delete_task(self, data):
#         print(f"Deleting task for user {self.user}: {data}")
#         task_id = data.get('id')
#         try:
#             task = Task.objects.get(id=task_id, user=self.user)
#             task.delete()
#             print(f"Task deleted: {task_id}")
#             return {'id': task_id}
#         except Task.DoesNotExist:
#             print(f"Task with ID {task_id} does not exist for user {self.user}")
#             return None

#     async def broadcast_task(self, action, task):
#         print(f"Broadcasting task {action} for user {self.user}")
#         message = {
#             'action': action,
#             'task': {
#                 'id': task.id,
#                 'title': task.title,
#                 'description': task.description,
#                 'status': task.status,
#                 'due_date': str(task.due_date) if task.due_date else None,
#                 'created_at': str(task.created_at),
#                 'updated_at': str(task.updated_at),
#             } if isinstance(task, Task) else task
#         }
#         await self.channel_layer.group_send(
#             self.group_name,
#             {
#                 'type': 'task_event',
#                 'message': message
#             }
#         )

#     async def task_event(self, event):
#         print(f"Sending task event to user {self.user}: {event['message']}")
#         await self.send(text_data=json.dumps(event['message']))



# tasks/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Task
from channels.db import database_sync_to_async

# Set up logging
logger = logging.getLogger(__name__)

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "tasks_room"  # Use a unique room for tasks
        self.room_group_name = f"task_updates_{self.room_name}"

        # Log when a connection attempt is made
        logger.info(f"Attempting to connect to room {self.room_group_name}")

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Connection established to room {self.room_group_name}")

    async def disconnect(self, close_code):
        # Log when a user disconnects
        logger.info(f"User {self.channel_name} disconnected from room {self.room_group_name}")

        # Leave the room group when the WebSocket disconnects
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        task_title = text_data_json.get('title', 'No title provided')
        
        # Log the received task update message
        logger.info(f"Received task update message: {task_title}")

        # Broadcast message to WebSocket group (this can be used for task creation or updates)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'task_update',
                'message': task_title
            }
        )

    # Receive message from the room group
    async def task_update(self, event):
        message = event['message']

        # Log the outgoing message being sent to the WebSocket
        logger.info(f"Sending task update message: {message}")

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
