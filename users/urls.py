from rest_framework_simplejwt.views import  TokenRefreshView
from django.urls import path
from .views import UserRegistrationView,TaskDetailView,TaskListCreateView,CustomTokenObtainPairView,TaskStatisticsView
from .import views
urlpatterns=[
    path('',views.index,name='index'),
    path('api/token/',CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserRegistrationView.as_view(), name='register_user'),
    path('api/tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('api/tasks/<int:task_id>/', TaskDetailView.as_view(), name='task-detail'),
     path('task-statistics/', TaskStatisticsView.as_view(), name='task-statistics'),
]