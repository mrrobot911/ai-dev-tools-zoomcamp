# Mini Kanban Board — Product Specification

## 1. Product Description

Mini Kanban Board is a desktop web application for managing tasks on collaborative Kanban boards.

Users can register and log in using email and password. A user can create multiple boards, invite other users through single-use invitation links, and collaborate with them in real time.

Each board contains columns and cards. Users can create and manage cards and move them between columns using drag and drop. Changes made by one user are immediately delivered to other users currently viewing the same board.

### Technology Stack

* **Frontend:** React + TypeScript
* **Backend:** FastAPI + SQLAlchemy
* **Database:** SQLite
* **Real-time communication:** Long Polling over REST API
* **HTTP API:** REST

### Default Board Structure

A newly created board contains three columns:

* To Do
* In Progress
* Done

A board must always contain at least **3 columns**.

---

## 2. Users and Permissions

### Owner

The user who creates a board is its owner.

The owner can:

* edit and delete the board;
* manage board participants;
* create, rename, reorder, and delete columns;
* create, edit, move, and delete cards;
* generate single-use invitation links.

### Participant

Participants can:

* view the board;
* create cards;
* edit any card;
* move cards between columns;
* leave the board;
* search and filter cards.

Participants cannot:

* manage columns;
* manage other participants;
* delete cards created by other participants;
* delete the board.

### Card Permissions

* All participants can edit any card.
* A card can be deleted only by:

  * its creator, or
  * the board owner.

---

## 3. User Stories

### Authentication

* As a user, I want to register with an email and password so that I can create and access my boards.
* As a user, I want to log in with my credentials so that I can access my boards.
* As a user, I want to log out so that my account remains protected.

### Boards

* As a user, I want to create a board so that I can organize tasks.
* As a user, I want to see my boards on a dashboard so that I can easily access them.
* As an owner, I want to rename and delete my board.
* As an owner, I want to invite other users to my board.
* As a participant, I want to leave a board when I no longer need access.

### Columns

* As an owner, I want to create columns to organize cards.
* As an owner, I want to rename and reorder columns.
* As an owner, I want to delete empty columns.
* As an owner, I want to organize my board using at least three columns.

### Cards

* As a participant, I want to create cards with a title and optional description.
* As a participant, I want to assign a card to a board participant.
* As a participant, I want to edit cards.
* As a card creator or owner, I want to delete cards.
* As a participant, I want to move cards between columns using drag and drop.
* As a user, I want to search cards by title.
* As a user, I want to filter cards by assignee.

### Collaboration

* As a participant, I want to see changes made by other users immediately.
* As a participant, I want my changes to appear immediately without waiting for the server response.
* As a user, I want the application to recover from temporary connection loss without losing the current board state.

### Invitations

* As an owner, I want to generate a single-use invitation link.
* As an unregistered user, I want to register through an invitation link and automatically join the board.
* As an owner, I want an invitation link to become invalid after it has been used.

---

## 4. Acceptance Criteria

### Authentication

* Users can register with an email and password.
* Users can log in with valid credentials.
* Invalid credentials are rejected.
* Authenticated users can access their dashboard.
* Unauthenticated users cannot access protected boards.

### Dashboard

* After login, the user sees a list of their boards.
* The dashboard allows the user to create a new board.
* Each board can be opened from the dashboard.
* The dashboard displays basic board information, including its owner and participant count.

### Board Management

* Creating a board automatically creates `To Do`, `In Progress`, and `Done`.
* A user can create up to **10 boards**.
* A board can have up to **10 participants**.
* A board can have up to **10 columns**.
* The owner can rename a board.
* The owner can delete a board.
* Deleting a board permanently deletes its columns, cards, participants, and invitation links.
* There is no board restoration mechanism.

### Column Management

* Only the owner can create, rename, reorder, or delete columns.
* A board must always contain at least **3 columns**.
* A column can be deleted only when it contains no cards.
* A board cannot exceed **10 columns**.
* Column changes are immediately propagated to other connected users.

### Card Management

* A card requires a title.
* A card may contain an optional description.
* A card may have an optional assignee.
* The assignee can be selected from a dropdown containing the current board participants.
* The assignee must be a participant of the board.
* Cards store creation and update timestamps.
* Participants can create cards.
* All participants can edit cards.
* Only the card creator or board owner can delete a card.
* A column can contain up to **100 cards**.
* Cards can be moved between columns using drag and drop.
* Drag and drop does not change the order of cards within a column.
* Cards within a column are displayed in creation order.
* Card creation, editing, deletion, and movement are synchronized in real time.

### Search and Filtering

* Users can search cards by title.
* Users can filter cards by assignee.
* Search and filtering apply to the current board.

### Invitations

* The owner can generate an invitation link.
* Each invitation link can be used only once.
* After successful use, the invitation link becomes invalid.
* An unregistered user opening a valid invitation link is directed to registration.
* After successful registration, the user is automatically added to the board.
* A board cannot exceed **10 participants**.
* The owner can remove participants.
* A removed participant can no longer access the board.
* A participant can leave the board if at least one other participant remains.
* The owner cannot transfer ownership.
* If the owner deletes their account, their boards and all related data are permanently deleted.

### Real-Time Collaboration

The application uses Long Polling over REST API for near real-time updates.
REST API endpoints are used for normal CRUD operations.
The backend exposes a dedicated updates endpoint for each board:
GET /api/boards/{board_id}/updates?since={timestamp}
The updates endpoint returns all board, column, card, and participant changes
that occurred after the given timestamp.
If no changes are available, the endpoint holds the request open for up to
30 seconds before returning an empty response (long polling).
After the response is received (or timeout), the client immediately issues
a new request.
Changes become visible to other users within the next polling cycle.
If two users edit the same entity concurrently, the last successfully saved
change wins. No conflict resolution UI is required for the MVP.

### Connection Loss

* The UI applies supported user actions optimistically.
* Temporary connection loss is visible to the user.
* After connectivity is restored, the client synchronizes with the current server state.
* The system does not require a persistent offline operation queue.

### Access Control

* Users cannot access boards they are not participants of.
* Attempting to access a board without permission returns **403 / Access Denied**.
* The user can return to the dashboard after receiving an access-denied response.

---

## 5. Non-Goals

The following features are explicitly outside the MVP scope:

* Mobile-responsive interface.
* Email notifications.
* Push notifications.
* In-app notifications.
* Activity/history/audit log.
* Manual card ordering within a column.
* Changing card order through drag and drop.
* Offline-first functionality.
* Persistent offline operation queue.
* Complex conflict resolution.
* Ownership transfer.
* Board trash/recovery.
* Multiple permission levels beyond owner and participant.
* Recurring tasks.
* Due dates.
* Labels/tags.
* File attachments.
* Comments.
* Checklists/subtasks.
* Card dependencies.
* Advanced search.
* Analytics and reporting.
* Multiple databases or database replication.
* WebSocket or Server-Sent Events (SSE).

---

## 6. MVP Limits

| Resource                  | Limit |
| ------------------------- | ----: |
| Boards per user           |    10 |
| Participants per board    |    10 |
| Columns per board         |    10 |
| Minimum columns per board |     3 |
| Cards per column          |   100 |

---

## 7. Testing Requirements

The application must include automated tests covering the behavior defined in this specification.

### Backend

* Unit and API tests using pytest.
* Tests for authentication and authorization.
* Tests for board, column, participant, and card CRUD operations.
* Tests for permission rules.
* Tests for invitation links.
* Tests for validation and MVP limits.

### Frontend

* Component and behavior tests using Vitest.
* Tests for board, column, and card interactions.
* Tests for card search and assignee filtering.
* Tests for permission-dependent UI behavior.
* Tests for optimistic updates.

### Real-Time

* Integration tests for the updates endpoint.
* Tests verifying that board changes are returned when polled with a past timestamp.
* Tests verifying that the endpoint holds the request when no changes are available.
* Tests verifying that concurrent updates are visible on subsequent polls.
* Tests verifying that the client polling loop handles network failures.

Tests should cover all acceptance criteria and the API/long polling contract defined by the implementation.

