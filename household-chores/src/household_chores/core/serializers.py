from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Household, Membership

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text='Confirm your password'
    )
    
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True}
        }
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        """Create user with validated data."""
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HouseholdSerializer(serializers.ModelSerializer):
    """Serializer for Household model."""
    
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    week_start_day_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Household
        fields = [
            'id', 'name', 'admin', 'admin_name', 'week_start_day',
            'week_start_day_display', 'created_at', 'updated_at', 'member_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HouseholdCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating households."""
    
    class Meta:
        model = Household
        fields = ['name', 'week_start_day']
    
    def create(self, validated_data):
        """Create household with admin set to current user."""
        validated_data['admin'] = self.context['request'].user
        return Household.objects.create(**validated_data)


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model."""
    
    user_name = serializers.CharField(source='user.name', read_only=True)
    household_name = serializers.CharField(source='household.name', read_only=True)
    joined_at_display = serializers.DateTimeField(source='joined_at', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_name', 'household', 'household_name',
            'role', 'is_active', 'joined_at', 'joined_at_display', 'left_at'
        ]
        read_only_fields = ['id', 'user', 'joined_at', 'left_at']


class MembershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating memberships."""
    
    class Meta:
        model = Membership
        fields = ['role']
    
    def create(self, validated_data):
        """Create membership with user and household from context."""
        validated_data['user'] = self.context['request'].user
        return Membership.objects.create(**validated_data)