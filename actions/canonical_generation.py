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
class ActionGenerateCanonical(Action):
    """
    Action to generate canonical
    """

    def name(self) -> Text:
        return "action_generate_canonical"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        config_route = tracker.get_slot('destination_path')
        print(f"Retrieved log value: {config_route}")

        os.chdir("Simod")
        
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")

        # Get the relative path from the current directory to the config route
        relative_config_route = os.path.relpath(config_route, current_directory)
        print(f"Relative config route: {relative_config_route}")
                
        # Replace backslashes with slashes
        config_route = config_route.replace("\\", "/")
        print(f"Config route with slashes: {config_route}")
        
        
        command = f"conda run -n Simod simod --configuration {relative_config_route}"
        subprocess.Popen(command, shell=True)
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for the background process to complete
        
        # Change directory to Simod/outputs
        os.chdir("outputs")
        
        # Identify the newest file in the Simod/outputs directory
        files = [f for f in os.listdir() if os.path.isfile(f)]
        newest_file = max(files, key=os.path.getctime)
        print(f"Newest file identified: {newest_file}")
        
        destination_folder = os.path.join(current_directory, "inputs")
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        shutil.copy(newest_file, destination_folder)
        print(f"Output file copied to {destination_folder}")
        
        os.chdir("../..")
        print("Canonical is being generated in background, when finished, please use 'action_get_canonical' to get the canonical to the path")
        return []