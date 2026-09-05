# Household Chores Project Backlog

## 1. Set up empty project with passing test
Goal: Create a minimal Django project structure with one passing test
Description: Initialize a Django project with basic configuration and write a simple test that passes to verify the setup is working correctly

## 2. Create User model and registration endpoint
Goal: Implement user authentication with email/password registration
Description: Create the User model with email, password, and name fields, and build a registration API endpoint that allows users to create accounts

## 3. Create Household model and admin management
Goal: Implement household creation and administration
Description: Create the Household model with name, admin user, week start day, and build endpoints for household creation and admin management functionality

## 4. Create Membership model and household joining
Goal: Implement user-household relationships and invitation system
Description: Create the Membership model connecting users to households, and build endpoints for household invitation and joining via invitation links

## 5. Create Chore model and basic CRUD
Goal: Implement chore creation and management
Description: Create the Chore model with title, description, household, frequency, difficulty, and current assigned member fields, and build basic CRUD endpoints

## 6. Implement chore assignment and weekly rotation
Goal: Create system for assigning chores to household members
Description: Build logic to assign chores to household members using a weekly rotation system with configurable start day

## 7. Create ChoreCompletion model and completion tracking
Goal: Implement chore completion functionality
Description: Create the ChoreCompletion model and build endpoints for marking chores as completed with proper history tracking

## 8. Create ChoreRefusal model and refusal system
Goal: Implement chore refusal and reassignment
Description: Create the ChoreRefusal model and build endpoints for refusing chores with reasons, including automatic reassignment to next member

## 9. Create user dashboard endpoint
Goal: Build main dashboard showing user's current chores
Description: Create a dashboard endpoint that displays the logged-in user's current assigned chores, pending tasks, and household progress

## 10. Create household progress endpoint
Goal: Implement household-wide progress tracking
Description: Build an endpoint showing household-wide chore completion statistics and progress for the current week

## 11. Create chore history endpoint
Goal: Implement historical chore tracking
Description: Create an endpoint showing the history of completed and refused chores with proper filtering and pagination

## 12. Create member statistics endpoint
Goal: Implement individual member statistics
Description: Build an endpoint showing individual member statistics including number of completed chores, refused chores, and total difficulty completed

## 13. Add basic frontend UI for registration
Goal: Create user registration interface
Description: Build a simple HTML form for user registration with proper validation and error handling

## 14. Add basic frontend UI for household creation
Goal: Create household creation interface
Description: Build a simple HTML form for creating new households with admin setup

## 15. Add basic frontend UI for chore management
Goal: Create chore creation and management interface
Description: Build HTML forms for creating, viewing, and managing household chores with proper role-based access

## 16. Add basic frontend dashboard
Goal: Create main dashboard interface
Description: Build a dashboard view showing user's current chores, household progress, and basic navigation

## 17. Implement chore completion UI
Goal: Create interface for marking chores as done
Description: Build UI components for viewing assigned chores and marking them as completed with one-click functionality

## 18. Implement chore refusal UI
Goal: Create interface for refusing chores
Description: Build UI components for refusing assigned chores with reason input and confirmation

## 19. Add basic authentication middleware
Goal: Protect endpoints requiring authentication
Description: Implement middleware to protect endpoints that require logged-in users and handle authentication errors gracefully

## 20. Add role-based access control
Goal: Implement admin vs member permissions
Description: Build permission system to distinguish between household admins and regular members for different operations

## 21. Add basic error handling and validation
Goal: Implement comprehensive error handling
Description: Add proper validation, error messages, and exception handling across all endpoints and forms

## 22. Add basic unit tests for models
Goal: Test model functionality and relationships
Description: Write comprehensive unit tests for all models (User, Household, Membership, Chore, ChoreCompletion, ChoreRefusal)

## 23. Add integration tests for API endpoints
Goal: Test API functionality and workflows
Description: Write integration tests for all API endpoints and common user workflows (registration, household creation, chore management)

## 24. Add frontend integration tests
Goal: Test frontend functionality
Description: Write tests for frontend components and user interactions with forms and dashboard

## 25. Set up basic deployment configuration
Goal: Prepare project for deployment
Description: Configure deployment settings, requirements, and basic production considerations