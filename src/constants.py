import os

DEBUG = True

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRASH_DIR = os.path.join(ROOT_DIR, ".trash")
COMMAND_HISTORY_PATH = os.path.join(ROOT_DIR, ".history")
UNDO_HISTORY_PATH = os.path.join(ROOT_DIR, ".undo_history")
