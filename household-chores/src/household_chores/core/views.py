from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Household, Membership
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    HouseholdSerializer, MembershipSerializer,
    HouseholdCreateSerializer, MembershipCreateSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user."""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response(
                {
                    'message': 'User registered successfully',
                    'user': user_data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login endpoint."""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        user_data = UserSerializer(user).data
        return Response(
            {
                'message': 'Login successful',
                'user': user_data
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'Invalid email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get the current user's profile."""
    user_data = UserSerializer(request.user).data
    return Response(
        {
            'user': user_data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_household(request):
    """Create a new household."""
    serializer = HouseholdCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        household = serializer.save()
        household_serializer = HouseholdSerializer(household)
        return Response(
            {
                'message': 'Household created successfully',
                'household': household_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_households(request):
    """Get all households for the current user."""
    # Get households where user is admin
    admin_households = Household.objects.filter(admin=request.user)
    
    # Get households where user is a member
    member_households = Household.objects.filter(
        memberships__user=request.user,
        memberships__is_active=True
    ).exclude(admin=request.user)
    
    # Combine and deduplicate
    all_households = list(admin_households) + list(member_households)
    unique_households = list(set(all_households))
    
    serializer = HouseholdSerializer(unique_households, many=True)
    return Response(
        {
            'households': serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_household_detail(request, household_id):
    """Get details of a specific household."""
    household = get_object_or_404(Household, id=household_id)
    
    # Check if user is admin or member
    is_admin = household.admin == request.user
    is_member = Membership.objects.filter(
        household=household,
        user=request.user,
        is_active=True
    ).exists()
    
    if not (is_admin or is_member):
        return Response(
            {'error': 'You are not a member of this household'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = HouseholdSerializer(household)
    return Response(
        {
            'household': serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_household(request, household_id):
    """Update household details (admin only)."""
    household = get_object_or_404(Household, id=household_id)
    
    if household.admin != request.user:
        return Response(
            {'error': 'Only the household admin can update this household'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = HouseholdSerializer(household, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'Household updated successfully',
                'household': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_household(request, household_id):
    """Join a household as a member."""
    household = get_object_or_404(Household, id=household_id)
    
    # Check if user is already a member
    if Membership.objects.filter(
        household=household,
        user=request.user,
        is_active=True
    ).exists():
        return Response(
            {'error': 'You are already a member of this household'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create membership
    membership = Membership.objects.create(
        user=request.user,
        household=household,
        role='member'
    )
    
    serializer = MembershipSerializer(membership)
    return Response(
        {
            'message': 'Successfully joined the household',
            'membership': serializer.data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def leave_household(request, household_id):
    """Leave a household."""
    household = get_object_or_404(Household, id=household_id)
    
    # Get user's membership
    membership = Membership.objects.filter(
        household=household,
        user=request.user,
        is_active=True
    ).first()
    
    if not membership:
        return Response(
            {'error': 'You are not a member of this household'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Don't allow admin to leave unless they transfer admin role first
    if membership.role == 'admin' and household.admin == request.user:
        # Check if there are other admins
        other_admins = Membership.objects.filter(
            household=household,
            role='admin',
            is_active=True
        ).exclude(user=request.user)
        
        if not other_admins:
            return Response(
                {'error': 'You cannot leave as you are the only admin. Transfer admin role first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Deactivate membership
    membership.is_active = False
    membership.left_at = timezone.now()
    membership.save()
    
    return Response(
        {'message': 'Successfully left the household'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_household_members(request, household_id):
    """Get all members of a household."""
    household = get_object_or_404(Household, id=household_id)
    
    # Check if user is admin or member
    is_admin = household.admin == request.user
    is_member = Membership.objects.filter(
        household=household,
        user=request.user,
        is_active=True
    ).exists()
    
    if not (is_admin or is_member):
        return Response(
            {'error': 'You are not a member of this household'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    memberships = Membership.objects.filter(
        household=household,
        is_active=True
    ).select_related('user')
    
    serializer = MembershipSerializer(memberships, many=True)
    return Response(
        {
            'memberships': serializer.data
        },
        status=status.HTTP_200_OK
    )