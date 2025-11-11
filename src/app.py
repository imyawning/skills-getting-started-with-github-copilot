"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },

    # Sports activities (2 more)
    "Soccer Team": {
        "description": "Outdoor team sport focusing on skills, fitness, and league matches",
        "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Pick-up games, drills, and friendly tournaments",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
    },

    # Artistic activities (2 more)
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, stagecraft, and preparation for school productions",
        "schedule": "Thursdays, 3:45 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },

    # Intellectual activities (2 more)
    "Debate Team": {
        "description": "Public speaking, argumentation, and competitive debate practice",
        "schedule": "Mondays, 5:00 PM - 6:30 PM",
        "max_participants": 16,
        "participants": ["eli@mergington.edu", "grace@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Hands-on science challenges, experiments, and competitions",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["lucas@mergington.edu", "zoe@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.delete("/activities/{activity_name}/participants")
def remove_participant(activity_name: str, email: str):
    """Remove/unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Normalize and find existing participant (case-insensitive)
    normalized_email = email.strip().lower()
    existing = [p for p in activity.get("participants", [])]
    matches = [p for p in existing if p.strip().lower() == normalized_email]
    if not matches:
        raise HTTPException(status_code=404, detail="Participant not found in activity")

    # Remove first matching participant
    to_remove = matches[0]
    activity["participants"].remove(to_remove)
    return {"message": f"Removed {to_remove} from {activity_name}"}

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    normalized_email = email.strip().lower()
    existing = [p.strip().lower() for p in activity.get("participants", [])]
    if normalized_email in existing:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}