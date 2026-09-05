from django.contrib import admin
from django.utils import timezone
from .models import User, Household, Membership


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for User model."""
    
    list_display = ('email', 'name', 'created_at', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password', 'password_confirm'),
        }),
    )


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    """Admin configuration for Household model."""
    
    list_display = ('name', 'admin', 'week_start_day_display', 'member_count', 'created_at')
    list_filter = ('week_start_day', 'created_at')
    search_fields = ('name', 'admin__email', 'admin__name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('name', 'admin', 'week_start_day')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'
    
    def week_start_day_display(self, obj):
        return obj.get_week_start_day_display()
    week_start_day_display.short_description = 'Week Start Day'


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Admin configuration for Membership model."""
    
    list_display = ('user', 'household', 'role', 'is_active', 'joined_at', 'left_at')
    list_filter = ('role', 'is_active', 'joined_at', 'left_at')
    search_fields = ('user__email', 'user__name', 'household__name')
    ordering = ('-joined_at',)
    
    fieldsets = (
        (None, {'fields': ('user', 'household', 'role')}),
        ('Status', {'fields': ('is_active', 'joined_at', 'left_at')}),
    )
    
    readonly_fields = ('joined_at', 'left_at')
    
    actions = ['activate_memberships', 'deactivate_memberships']
    
    def activate_memberships(self, request, queryset):
        """Activate selected memberships."""
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f'{updated} memberships activated.')
    activate_memberships.short_description = 'Activate selected memberships'
    
    def deactivate_memberships(self, request, queryset):
        """Deactivate selected memberships."""
        updated = queryset.filter(is_active=True).update(is_active=True, left_at=timezone.now())
        self.message_user(request, f'{updated} memberships deactivated.')
    deactivate_memberships.short_description = 'Deactivate selected memberships'
