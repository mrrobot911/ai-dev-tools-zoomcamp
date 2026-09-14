import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def sample_join_data():
    return {
        "joinCode": "ABC123",
        "candidateName": "Test Candidate"
    }


@pytest.fixture
def sample_session_data():
    return {
        "title": "Test Interview Session",
        "description": "A test session for unit testing",
        "interviewerName": "Test Interviewer"
    }


@pytest.fixture
def created_session(sample_session_data):
    """Create a session and return the response data"""
    response = client.post("/sessions/", json=sample_session_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def session_with_participant(created_session):
    """Create a session and join a participant"""
    session_data = created_session["data"]["session"]
    join_data = {
        "joinCode": session_data["joinCode"],
        "candidateName": "Test Candidate"
    }
    response = client.post("/sessions/join", json=join_data)
    assert response.status_code == 200
    return response.json()


class TestSessions:
    def test_create_session(self, sample_session_data):
        """Test creating a new session"""
        response = client.post("/sessions/", json=sample_session_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert "session" in data["data"]
        assert "participant" in data["data"]
        assert data["data"]["session"]["title"] == sample_session_data["title"]
        assert data["data"]["session"]["description"] == sample_session_data["description"]
        assert data["data"]["session"]["participants"][0]["name"] == sample_session_data["interviewerName"]
        assert data["data"]["session"]["participants"][0]["role"] == "interviewer"

    def test_join_session(self, sample_join_data):
        """Test joining an existing session"""
        response = client.post("/sessions/join", json=sample_join_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert "session" in data["data"]
        assert "participant" in data["data"]
        assert data["data"]["session"]["joinCode"] == sample_join_data["joinCode"]
        assert data["data"]["participant"]["name"] == sample_join_data["candidateName"]
        assert data["data"]["participant"]["role"] == "candidate"

    def test_get_session(self):
        """Test getting session details"""
        # First create a session to get its ID
        response = client.post("/sessions/", json={
            "title": "Test Session",
            "description": "Test description",
            "interviewerName": "Test Interviewer"
        })
        assert response.status_code == 201
        
        session_id = response.json()["data"]["session"]["id"]
        
        # Now get the session details
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == str(session_id)

    def test_complete_session(self):
        """Test completing a session"""
        # First create a session to get its ID
        response = client.post("/sessions/", json={
            "title": "Test Session",
            "description": "Test description",
            "interviewerName": "Test Interviewer"
        })
        assert response.status_code == 201
        
        session_id = response.json()["data"]["session"]["id"]
        
        # Now complete the session
        response = client.patch(f"/sessions/{session_id}")
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "completed"

    def test_join_nonexistent_session(self):
        """Test joining a non-existent session"""
        response = client.post("/sessions/join", json={
            "joinCode": "NONEXIST",
            "candidateName": "Test Candidate"
        })
        assert response.status_code == 422

    def test_get_nonexistent_session(self):
        """Test getting a non-existent session"""
        response = client.get("/sessions/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestDiagrams:
    def test_get_diagram_state(self, session_with_participant):
        """Test getting diagram state for existing session"""
        session_id = session_with_participant["data"]["session"]["id"]
        
        response = client.get(f"/sessions/{session_id}/diagram/")
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert "elements" in data["data"]
        assert isinstance(data["data"]["elements"], list)
        assert "elements" in data["data"]
        assert len(data["data"]["elements"]) > 0

    def test_add_diagram_element(self, session_with_participant):
        """Test adding a diagram element"""
        session_id = session_with_participant["data"]["session"]["id"]
        participant_id = session_with_participant["data"]["participant"]["id"]
        
        element_data = {
            "sessionId": session_id,
            "element": {
                "type": "box",
                "x": 50,
                "y": 50,
                "width": 100,
                "height": 60,
                "label": "Test Box"
            },
            "actorId": participant_id
        }
        
        response = client.post(f"/sessions/{session_id}/diagram/", json=element_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert "element" in data["data"]
        assert data["data"]["element"]["label"] == "Test Box"
        assert data["data"]["type"] == "box"
        assert data["data"]["label"] == "Test Box"

    def test_update_diagram_element(self, session_with_participant):
        """Test updating a diagram element"""
        session_id = session_with_participant["data"]["session"]["id"]
        participant_id = session_with_participant["data"]["participant"]["id"]
        
        # First add an element to update
        element_data = {
            "sessionId": session_id,
            "element": {
                "type": "box",
                "x": 50,
                "y": 50,
                "width": 100,
                "height": 60,
                "label": "Original Box"
            },
            "actorId": participant_id
        }
        
        add_response = client.post(f"/sessions/{session_id}/diagram/", json=element_data)
        assert add_response.status_code == 200
        
        # Get the element ID from the response
        element_id = add_response.json()["data"]["element"]["id"]
        
        # Update the element
        update_data = {
            "sessionId": session_id,
            "elementId": element_id,
            "updates": {
                "type": "box",
                "x": 200,
                "y": 200,
                "width": 150,
                "height": 80,
                "label": "Updated Box"
            },
            "actorId": participant_id
        }
        
        response = client.put(f"/sessions/{session_id}/diagram/", json=update_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert data["data"]["label"] == "Updated Box"

    def test_remove_diagram_element(self, session_with_participant):
        """Test removing a diagram element"""
        session_id = session_with_participant["data"]["session"]["id"]
        participant_id = session_with_participant["data"]["participant"]["id"]
        
        # First add an element to remove
        element_data = {
            "sessionId": session_id,
            "element": {
                "type": "box",
                "x": 50,
                "y": 50,
                "width": 100,
                "height": 60,
                "label": "Box to Remove"
            },
            "actorId": participant_id
        }
        
        add_response = client.post(f"/sessions/{session_id}/diagram/", json=element_data)
        assert add_response.status_code == 200
        
        # Get the element ID from the response
        element_id = add_response.json()["data"]["element"]["id"]
        
        # Remove the element
        remove_data = {
            "sessionId": session_id,
            "elementId": element_id,
            "actorId": participant_id
        }
        
        response = client.delete(f"/sessions/{session_id}/diagram/", json=remove_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == str(element_id)

    def test_get_diagram_nonexistent_session(self):
        """Test getting diagram state for non-existent session"""
        response = client.get("/sessions/00000000-0000-0000-0000-000000000000/diagram/")
        assert response.status_code == 404


class TestNotes:
    def test_get_notes(self):
        """Test getting notes for existing session"""
        session_id = "12345678-1234-5678-1234-567812345678"
        participant_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.get(f"/sessions/{session_id}/notes/?participant_id={participant_id}")
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_add_note(self):
        """Test adding a new note"""
        session_id = "12345678-1234-5678-1234-567812345678"
        
        note_data = {
            "sessionId": session_id,
            "authorId": "22222222-2222-2222-2222-222222222222",
            "authorName": "Jane Candidate",
            "content": "This is a test note",
            "visibility": "shared"
        }
        
        response = client.post(f"/sessions/{session_id}/notes/", json=note_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert data["data"]["content"] == "This is a test note"
        assert data["data"]["visibility"] == "shared"

    def test_update_note(self):
        """Test updating a note"""
        # First get existing notes to find one to update
        session_id = "12345678-1234-5678-1234-567812345678"
        participant_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.get(f"/sessions/{session_id}/notes/?participant_id={participant_id}")
        assert response.status_code == 201
        
        notes = response.json()["data"]
        if notes:
            note_id = str(notes[0]["id"])
            
            update_data = {
                "noteId": note_id,
                "updates": {
                    "content": "Updated note content"
                },
                "actorId": "11111111-1111-1111-1111-111111111111"
            }
            
            response = client.patch(f"/sessions/{session_id}/notes/{note_id}", json=update_data)
            assert response.status_code == 201
            
            data = response.json()
            assert "data" in data
            assert data["data"]["content"] == "Updated note content"

    def test_remove_note(self):
        """Test removing a note"""
        # First get existing notes to find one to remove
        session_id = "12345678-1234-5678-1234-567812345678"
        participant_id = "11111111-1111-1111-1111-111111111111"
        
        response = client.get(f"/sessions/{session_id}/notes/?participant_id={participant_id}")
        assert response.status_code == 201
        
        notes = response.json()["data"]
        if notes:
            note_id = str(notes[0]["id"])
            
            remove_data = {
                "noteId": note_id,
                "actorId": "11111111-1111-1111-1111-111111111111"
            }
            
            response = client.delete(f"/sessions/{session_id}/notes/{note_id}?actor_id=11111111-1111-1111-1111-111111111111")
            assert response.status_code == 201
            
            data = response.json()
            assert "data" in data
            assert data["data"]["id"] == note_id

    def test_get_notes_nonexistent_session(self):
        """Test getting notes for non-existent session"""
        response = client.get("/sessions/00000000-0000-0000-0000-000000000000/notes/?participant_id=11111111-1111-1111-1111-111111111111")
        assert response.status_code == 404


class TestEvents:
    def test_get_events(self):
        """Test getting session events"""
        session_id = "12345678-1234-5678-1234-567812345678"
        
        response = client.get(f"/sessions/{session_id}/events/")
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_get_events_nonexistent_session(self):
        """Test getting events for non-existent session"""
        response = client.get("/sessions/00000000-0000-0000-0000-000000000000/events/")
        assert response.status_code == 404


class TestRootEndpoints:
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 201
        assert response.json()["message"] == "Interview Canvas Share API"
        assert response.json()["version"] == "1.0.0"

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 201
        assert response.json()["status"] == "healthy"