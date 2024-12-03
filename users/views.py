from django.shortcuts import render,HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
def index(request):
    return HttpResponse('<h1>Megha</h1>')
# Create your views here.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "User registered successfully. Please check your email for verification.",
            "data": response.data
        }, status=status.HTTP_201_CREATED)
    



class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, task_id, user):
        try:
            return Task.objects.get(id=task_id, user=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        task = self.get_object(task_id, request.user)
        if task:
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, task_id):
        task = self.get_object(task_id, request.user)
        if task:
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, task_id):
        task = self.get_object(task_id, request.user)
        if task:
            task.delete()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username  # Add username to the token
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from users.models import CustomUser
from django.utils import timezone
class TaskStatisticsView(APIView):
    # Ensure that only authenticated users can access this view
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the logged-in user

        # Calculate statistics for the logged-in user
        completed_tasks = Task.objects.filter(user=user, status="Completed").count()
        overdue_tasks = Task.objects.filter(user=user, due_date__lt=timezone.now(), status="Pending").count()
        total_tasks = Task.objects.filter(user=user).count()

        # Create a response dictionary with the statistics
        stats = {
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'total_tasks': total_tasks
        }

        # Return the statistics as a JSON response
        return Response(stats)
    


