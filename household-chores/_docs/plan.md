# Shared Household Chores Tool — Project Plan

## 1. Project Overview

This project is a web application for managing shared household chores.  
The tool helps people living in the same household create chores, assign them fairly, track completion, and see household progress.

The first version will be built as a small Django application focused on a practical MVP.

## 2. Target Users

The application is designed for shared households with flexible member types, such as:

- Roommates
- Families
- Couples
- Any group of people sharing domestic responsibilities

Each household has an administrator who can manage members and chores.

## 3. MVP Scope

The MVP focuses on four core capabilities:

1. Household and member management
2. Chore creation and weekly rotation
3. Task completion and refusal
4. Dashboard and completion history

The goal is to build a simple but usable chore management system, not a fully automated fairness engine.

## 4. Core Features

### Feature 1: Household and Member Management

Users can register with email and password.  
A registered user can create a household and become its administrator.

The administrator can invite other members to the household using an invitation link.  
Household members can view shared chores and their own assigned tasks.

### Feature 2: Chore Creation and Weekly Rotation

Admins or permitted members can create chores.

Each chore has:

- Title
- Description
- Frequency
- Difficulty level
- Assigned household
- Current responsible member

Chores are assigned to members using a weekly rotation.  
The default rotation happens every Monday, but the household can configure the start day of the week.

### Feature 3: Completion and Refusal Tracking

A member can mark an assigned chore as completed with one button.

When a chore is completed, the system stores:

- Who completed it
- When it was completed
- Which chore was completed

A member can also refuse a chore and provide a reason.  
When a chore is refused, it is reassigned to the next member in the rotation and the refusal is stored in the history.

### Feature 4: Dashboard and History

After logging in, the user sees a dashboard.

The dashboard shows:

- The user's current chores
- Household progress for the current week
- Pending chores
- Completed chores

The app also stores a history of completed chores and basic statistics per member, such as:

- Number of completed chores
- Number of refused chores
- Total difficulty completed

## 5. Out of Scope for Version 1

The following features are intentionally excluded from the first version:

- Push notifications
- Email notifications
- Mobile application
- Advanced fairness algorithms
- Complex calendar and recurrence rules
- Time zone handling
- Photo or comment proof for completed chores
- Payments, fines, or penalties
- Native mobile app
- Google or Apple login

These can be considered for future versions after the MVP works.

## 6. Main User Flows

### Flow 1: Create a Household

1. User registers with email and password.
2. User creates a new household.
3. User becomes the household administrator.
4. User can invite other members.

### Flow 2: Invite Members

1. Admin opens the household settings page.
2. Admin generates or copies an invitation link.
3. Another user opens the link.
4. The invited user joins the household.

### Flow 3: Create a Chore

1. Admin or permitted member opens the chore creation page.
2. They enter the chore title, description, frequency, and difficulty.
3. The chore is saved and added to the household.
4. The system assigns it to a member according to the rotation.

### Flow 4: Complete a Chore

1. Member opens the dashboard.
2. Member sees their assigned chores.
3. Member clicks “Done” on a chore.
4. The chore is marked as completed.
5. The completion is saved in the history.

### Flow 5: Refuse a Chore

1. Member opens the dashboard.
2. Member clicks “Refuse” on an assigned chore.
3. Member enters a reason.
4. The refusal is saved in the history.
5. The chore is reassigned to the next member in the rotation.

## 7. Basic Data Model

### User

Represents a registered user.

Fields:

- Email
- Password
- Name

### Household

Represents a shared household.

Fields:

- Name
- Admin user
- Week start day
- Created date

### Membership

Connects users to households.

Fields:

- User
- Household
- Role: admin or member
- Is active

### Chore

Represents a recurring household chore.

Fields:

- Title
- Description
- Household
- Frequency
- Difficulty level
- Current assigned member
- Is active

### ChoreCompletion

Stores completed chores.

Fields:

- Chore
- Completed by
- Completed at
- Difficulty at time of completion

### ChoreRefusal

Stores refused chores.

Fields:

- Chore
- Refused by
- Reason
- Refused at

## 8. Acceptance Criteria

### Household and Member Management

- A user can register with email and password.
- A registered user can create a household.
- The creator of a household becomes its admin.
- An admin can invite another user with an invitation link.
- An invited user can join the household.

### Chore Creation and Rotation

- An admin or permitted member can create a chore.
- A chore has a title, description, frequency, and difficulty level.
- A chore belongs to one household.
- A chore can be assigned to a household member.
- The system can rotate chore assignments weekly.

### Completion and Refusal

- A member can mark an assigned chore as completed.
- Completed chores are stored in the history.
- A member can refuse a chore with a reason.
- Refused chores are reassigned to another member.
- Refusals are stored in the history.

### Dashboard and History

- After login, a user can see their assigned chores.
- The dashboard shows current household progress.
- The app shows completed chores.
- The app shows basic member statistics.

