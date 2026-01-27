"""Data-driven tutorial system.

Loads tutorial steps and messages from data/tutorial.json.
"""

import json
from pathlib import Path

# Default tutorial steps if file not found
DEFAULT_TUTORIAL = {
    "steps": [
        {"id": "welcome", "message": "Welcome to Minmatar Rebellion!", "duration": 3.0},
        {"id": "movement", "message": "Use WASD or Arrow Keys to move.", "duration": 4.0},
        {"id": "shooting", "message": "Press SPACE to fire autocannons.", "duration": 4.0},
    ]
}


def get_tutorial_path():
    """Get the path to the tutorial.json data file."""
    base_dir = Path(__file__).parent.parent
    return base_dir / "data" / "tutorial.json"


def load_tutorial_data():
    """Load tutorial data from data/tutorial.json.

    Returns:
        dict: Tutorial data with 'steps' list.
              Returns default tutorial if file doesn't exist or is invalid.
    """
    tutorial_path = get_tutorial_path()

    if not tutorial_path.exists():
        return DEFAULT_TUTORIAL.copy()

    try:
        with open(tutorial_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate that steps exist
        if "steps" not in data or not isinstance(data["steps"], list):
            return DEFAULT_TUTORIAL.copy()

        # Validate each step has required fields
        validated_steps = []
        for step in data["steps"]:
            if isinstance(step, dict) and "message" in step:
                validated_step = {
                    "id": step.get("id", f"step_{len(validated_steps)}"),
                    "message": str(step["message"]),
                    "duration": float(step.get("duration", 3.0)),
                }
                validated_steps.append(validated_step)

        if not validated_steps:
            return DEFAULT_TUTORIAL.copy()

        return {"steps": validated_steps}
    except (json.JSONDecodeError, IOError, ValueError):
        return DEFAULT_TUTORIAL.copy()


class Tutorial:
    """Data-driven tutorial system.

    Displays sequential tutorial messages loaded from data/tutorial.json.

    Attributes:
        steps (list): List of tutorial step dictionaries.
        current_step (int): Index of the current tutorial step.
        is_active (bool): Whether the tutorial is currently running.
        step_timer (float): Time remaining for the current step.
        completed (bool): Whether the tutorial has been completed.
    """

    def __init__(self):
        """Initialize the tutorial system and load tutorial data."""
        data = load_tutorial_data()
        self.steps = data["steps"]
        self.current_step = 0
        self.is_active = False
        self.step_timer = 0.0
        self.completed = False

    def start(self):
        """Start the tutorial from the beginning."""
        self.current_step = 0
        self.is_active = True
        self.completed = False
        if self.steps:
            self.step_timer = self.steps[0]["duration"]

    def stop(self):
        """Stop the tutorial."""
        self.is_active = False

    def skip(self):
        """Skip to the end of the tutorial."""
        self.current_step = len(self.steps)
        self.is_active = False
        self.completed = True

    def next_step(self):
        """Advance to the next tutorial step.

        Returns:
            bool: True if advanced to next step, False if tutorial complete.
        """
        self.current_step += 1

        if self.current_step >= len(self.steps):
            self.is_active = False
            self.completed = True
            return False

        self.step_timer = self.steps[self.current_step]["duration"]
        return True

    def previous_step(self):
        """Go back to the previous tutorial step.

        Returns:
            bool: True if went back, False if already at the beginning.
        """
        if self.current_step > 0:
            self.current_step -= 1
            self.step_timer = self.steps[self.current_step]["duration"]
            return True
        return False

    def update(self, delta_time):
        """Update the tutorial timer.

        Args:
            delta_time: Time elapsed since last update in seconds.

        Returns:
            bool: True if step changed, False otherwise.
        """
        if not self.is_active or not self.steps:
            return False

        self.step_timer -= delta_time

        if self.step_timer <= 0:
            return self.next_step()

        return False

    def get_current_message(self):
        """Get the current tutorial message.

        Returns:
            str or None: Current message text, or None if tutorial not active.
        """
        if not self.is_active or self.current_step >= len(self.steps):
            return None

        return self.steps[self.current_step]["message"]

    def get_current_step_id(self):
        """Get the current step's ID.

        Returns:
            str or None: Current step ID, or None if tutorial not active.
        """
        if not self.is_active or self.current_step >= len(self.steps):
            return None

        return self.steps[self.current_step]["id"]

    def get_progress(self):
        """Get tutorial progress information.

        Returns:
            dict: Progress info with 'current', 'total', and 'percentage'.
        """
        total = len(self.steps)
        current = min(self.current_step + 1, total)
        percentage = (current / total * 100) if total > 0 else 100

        return {"current": current, "total": total, "percentage": percentage}

    def get_display_data(self):
        """Get tutorial data for rendering.

        Returns:
            dict: Tutorial state for rendering including message and progress.
        """
        return {
            "is_active": self.is_active,
            "message": self.get_current_message(),
            "step_id": self.get_current_step_id(),
            "progress": self.get_progress(),
            "time_remaining": self.step_timer,
            "completed": self.completed,
        }

    def reload(self):
        """Reload tutorial data from file.

        Useful for development to pick up changes without restarting.
        """
        data = load_tutorial_data()
        self.steps = data["steps"]

        # Reset if current step is now out of bounds
        if self.current_step >= len(self.steps):
            self.current_step = 0
            if self.is_active and self.steps:
                self.step_timer = self.steps[0]["duration"]
