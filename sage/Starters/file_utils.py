from pathlib import Path
import json

def mark_files_unsummarized(data):
    """Recursively mark all files as unsummarized"""
    for key, value in data.items():
        if value == "file":
            data[key] = "unsummarized"
        elif isinstance(value, dict):
            mark_files_unsummarized(value)

def update_interface_with_summaries(data, summaries, current_path: Path = Path(".")):
    """Recursively update interface data with file summaries"""
    for key, value in data.items():
        if value == "file":
            # Create the full file path as it would appear in the flattened summaries
            file_key = str(current_path / key).replace("\\", "/")
            
            if file_key in summaries:
                # Ensure request is empty if it was filled
                summary_data = summaries[file_key].copy()
                if summary_data.get("request") == "provide":
                    summary_data["request"] = ""
                data[key] = summary_data
            else:
                # If not found in summaries, check without current path (for root files)
                if key in summaries:
                    summary_data = summaries[key].copy()
                    if summary_data.get("request") == "provide":
                        summary_data["request"] = ""
                    data[key] = summary_data
                else:
                    data[key] = "unsummarized"
        elif isinstance(value, dict):
            update_interface_with_summaries(value, summaries, current_path / key)