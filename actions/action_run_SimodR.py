from . import bimp_essential as esc
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions import *
from rasa_sdk.events import FollowupAction
import os
import subprocess
import shutil
class ActionRunSimodR(Action):
    """
    Action to Run SimodR
    """

    def name(self) -> Text:
        return "action_run_SimodR"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        config_route = tracker.get_slot('destination_path')
        print(f"Retrieved log value: {config_route}")

        os.chdir("SimodR")
        
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")

        # Get the relative path from the current directory to the config route
        relative_config_route = os.path.relpath(config_route, current_directory)
        print(f"Relative config route: {relative_config_route}")
        
        
        command = f"conda run -n SimodR python main_simodr.py"
        subprocess.Popen(command, shell=True)
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for the background process to complete
        return []