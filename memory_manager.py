import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "story_memory.json")


def save_story(data):

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            stories = json.load(f)
    else:
        stories = []

    stories.append(data)

    with open(MEMORY_FILE, "w") as f:
        json.dump(stories, f, indent=4)


def get_all_stories():

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    return []