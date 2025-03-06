import json
import os
from pathlib import Path
from typing import List
from testing.test_data_models.qa_data import QAData

def load_qa_data_from_json(json_filename: str) -> List[QAData]:
    """Load test data from a JSON file and convert it into a list of QAData objects."""
    # Get the absolute path of the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the JSON file
    json_path = os.path.join(script_dir, json_filename)
    
    # Check if the file exists before attempting to open it
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File '{json_path}' not found. Ensure it exists in the correct directory.")
    
    with open(json_path, "r", encoding="utf-8") as file:
        qa_json_list = json.load(file)
    
    qa_objects = []
    for index, qa_json in enumerate(qa_json_list):
        qa_objects.append(QAData(
            question=qa_json["question"],
            answer=qa_json["answer"],
            classification=qa_json["study_program"],
            label=f"TEST-{index}",
            language=qa_json["language"]
        ))

    return qa_objects