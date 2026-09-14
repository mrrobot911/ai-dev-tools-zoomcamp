System Design Interview App — Specification
1. Project Goal

Build a minimal web application for conducting live system design interviews.

The application allows an interviewer to create an interview session, invite a candidate using a link, and collaboratively work on a system architecture diagram in real time.

The goal of the MVP is to demonstrate real-time collaborative editing and session management.

2. MVP Features
2.1 Create Interview Session

The interviewer can:

Create a new interview session.
Enter the interview problem:
Title
Task description
Receive a unique link for the candidate.

The interviewer is automatically the owner of the session.

2.2 Join Interview

The candidate can:

Open the interview link.
Enter the session without creating an account.
Access the shared interview workspace.

No authentication system is required for the MVP.

2.3 Collaborative Architecture Diagram

The main feature of the application is a shared system architecture diagram.

Both interviewer and candidate can:

Add diagram elements.
Move elements.
Delete elements.
Create connections between elements.
Edit the diagram simultaneously.

Changes are synchronized between participants in real time using WebSockets.

Both users should see approximately the same diagram state without refreshing the page.

2.4 Notes

The interviewer can create notes during the interview.

Each note has a visibility setting:

Private — visible only to the interviewer.
Shared — visible to both interviewer and candidate.

Notes should be synchronized in real time when appropriate.

The candidate can see shared notes but cannot see private notes.

2.5 Finish Interview

The interviewer can finish the interview session.

After finishing:

The session becomes read-only.
The diagram can no longer be edited.
Notes can no longer be edited.
The candidate can no longer modify the workspace.

No scorecard or feedback workflow is required.

3. Main User Flows
Interviewer Flow
Open the application.
Create an interview session.
Enter the problem title and description.
Receive a unique candidate link.
Share the link with the candidate.
Wait for the candidate to join.
Collaboratively edit the architecture diagram.
Add private/shared notes.
Finish the interview.
Candidate Flow
Open the interview link.
Join the session.
Read the problem description.
Collaboratively edit the architecture diagram.
See shared notes.
Continue until the interviewer finishes the session.
4. Interview Problem

An interview problem contains only:

Problem
├── title
└── description


Example:

Title:
Design a URL Shortener

Description:
Design a scalable URL shortening service similar to bit.ly.
Discuss the API, storage model, scaling strategy, and potential bottlenecks.


No hints, reference solutions, evaluation criteria, or question libraries are required.

5. Minimal Data Model
InterviewSession
InterviewSession
├── id
├── problem_title
├── problem_description
├── status
├── created_at
└── finished_at


status:

ACTIVE
FINISHED

Note
Note
├── id
├── session_id
├── content
├── visibility
└── created_at


visibility:

PRIVATE
SHARED

Diagram

The diagram state belongs to an interview session.

A diagram element may contain information such as:

DiagramElement
├── id
├── type
├── position
├── label
└── properties


Connections reference diagram element IDs.

The exact diagram data format can be defined during implementation.

6. Real-Time Communication

WebSockets are used for real-time synchronization.

The basic architecture is:

Interviewer Browser
        │
        │ WebSocket
        ▼
    FastAPI Server
        │
        │ WebSocket
        ▼
 Candidate Browser


The server is responsible for broadcasting changes to other participants in the same session.

Examples of real-time events:

element_created
element_updated
element_deleted
connection_created
note_created
note_updated
session_finished


The server should be the authoritative source for the current session state.

7. Technical Stack
Frontend
React
TypeScript

Responsibilities:

Interview UI
Diagram editor
Notes UI
Session state
WebSocket connection
Real-time updates
Backend
FastAPI
Python
WebSockets

Responsibilities:

Create interview sessions
Generate session links/IDs
Allow candidates to join sessions
Manage WebSocket connections
Synchronize diagram changes
Synchronize shared notes
Store session data
Finish sessions
Database
SQLite

Used for persistent storage of:

Interview sessions
Problem title and description
Notes
Diagram state
Session status
Communication
WebSockets for real-time collaboration
HTTP/REST for regular operations such as creating and loading sessions
8. MVP Architecture
┌───────────────────────┐
│   Interviewer Browser │
│   React + TypeScript  │
└───────────┬───────────┘
            │
      HTTP / WebSocket
            │
            ▼
┌───────────────────────┐
│      FastAPI Server   │
│                       │
│  Session Management   │
│  WebSocket Manager    │
│  Collaboration Logic  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│        SQLite         │
│                       │
│ Sessions              │
│ Notes                 │
│ Diagram State         │
└───────────────────────┘
            ▲
            │
      HTTP / WebSocket
            │
┌───────────┴───────────┐
│    Candidate Browser  │
│   React + TypeScript  │
└───────────────────────┘

9. MVP Scope
Included
Create interview session
Define problem title and description
Generate/share candidate link
Join session without registration
Shared interview workspace
Real-time collaborative diagram editing
Private interviewer notes
Shared notes
Real-time synchronization
Finish interview
Read-only state after completion
SQLite persistence
Explicitly Out of Scope
Authentication
User accounts
Organizations
Teams
Roles and permissions
Problem library
Scorecards
Feedback
Interview history
Replay
AI interviewer
Video/audio calls
Recording
Transcription
Solo practice mode
Hints or reference solutions
Advanced analytics
10. MVP Success Criteria

The MVP is successful if two users can:

Open the same interview session.
See the same problem.
Edit the same architecture diagram simultaneously.
See diagram changes in real time.
Create private and shared notes.
See shared notes in real time.
Finish the interview.
Have the session become read-only after finishing.

The core technical demonstration is:

Two independent browser clients connected to the same interview session can collaboratively edit a shared system design diagram in real time through WebSockets.

