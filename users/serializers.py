from rest_framework import serializers
from .models import CustomUser,Task
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'dob', 'mobile', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords must match.")
        
        # Validate password strength
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        return attrs

    def create(self, validated_data):
        # Remove confirm_password before creating user
        validated_data.pop('confirm_password')
        
        # Create the user and return it
        user = CustomUser.objects.create_user(**validated_data)
        return user


class TaskSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Adding the username field

    class Meta:
        model = Task
        fields = ['id', 'username', 'title', 'description', 'status', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

class TaskStatisticsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    total_tasks = serializers.IntegerField()