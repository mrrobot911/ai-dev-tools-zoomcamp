from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, name, password=None, **extra_fields):
        """Create and save a user with the given email, name, and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        """Create and save a superuser with the given email, name, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for household chores application."""
    
    username = None  # Use email instead of username
    email = models.EmailField(
        unique=True,
        verbose_name='Email address',
        help_text='Required. Unique email address for the user.'
    )
    
    name = models.CharField(
        max_length=150,
        verbose_name='Full Name',
        help_text='Required. Full name of the user.'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='Timestamp when the user was created.'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
        help_text='Timestamp when the user was last updated.'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class Household(models.Model):
    """Represents a shared household."""
    
    name = models.CharField(
        max_length=100,
        verbose_name='Household Name',
        help_text='Required. Name of the household.'
    )
    
    admin = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='admin_households',
        verbose_name='Administrator',
        help_text='Required. The user who manages this household.'
    )
    
    week_start_day = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ],
        default=0,
        verbose_name='Week Start Day',
        help_text='The day of the week when the weekly rotation starts.'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='Timestamp when the household was created.'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
        help_text='Timestamp when the household was last updated.'
    )
    
    class Meta:
        verbose_name = 'Household'
        verbose_name_plural = 'Households'
        db_table = 'households'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        """Get the number of members in this household."""
        return self.memberships.filter(is_active=True).count()
    
    @property
    def active_members(self):
        """Get all active members of this household."""
        return self.memberships.filter(is_active=True).select_related('user')
    
    def get_week_start_day_display(self):
        """Get the display name of the week start day."""
        return dict(self._meta.get_field('week_start_day').choices)[self.week_start_day]
    
    def save(self, *args, **kwargs):
        """Save the household and ensure it has an admin."""
        super().save(*args, **kwargs)
        
        # Ensure the admin has a membership with admin role
        from .models import Membership
        Membership.objects.get_or_create(
            user=self.admin,
            household=self,
            defaults={'role': 'admin', 'is_active': True}
        )


class Membership(models.Model):
    """Connects users to households."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('member', 'Member'),
    ]
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='User',
        help_text='Required. The user who is a member of this household.'
    )
    
    household = models.ForeignKey(
        'Household',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Household',
        help_text='Required. The household this user belongs to.'
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name='Role',
        help_text='The role of this user in the household.'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active',
        help_text='Whether this membership is currently active.'
    )
    
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Joined At',
        help_text='Timestamp when the user joined this household.'
    )
    
    left_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Left At',
        help_text='Timestamp when the user left this household (if applicable).'
    )
    
    class Meta:
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'
        db_table = 'memberships'
        unique_together = ('user', 'household')
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.household.name} ({self.role})"
    
    def clean(self):
        """Validate that a user can't be in the same household twice."""
        if Membership.objects.filter(
            user=self.user,
            household=self.household,
            is_active=True
        ).exists():
            raise ValidationError(
                'This user is already a member of this household.'
            )
    
    def save(self, *args, **kwargs):
        """Save the membership and handle role changes."""
        super().save(*args, **kwargs)