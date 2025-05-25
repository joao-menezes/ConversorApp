import os
import json

class HistoryService:
    def __init__(self, history_file="history.json"):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def add_record(self, action_type, filename, path):
        record = {
            "type": action_type,
            "filename": filename,
            "path": path,
            "status": "Completed"
        }
        self.history.append(record)
        self.save_history()

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []
        self.save_history()
