from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import os
import shutil
import yaml

class ActionConfigFileGeneration(Action):
    """
    Action to generate simod configuration file
    """

    def name(self) -> Text:
        return "action_generate_config_file"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Retrieve the value of the slot named 'log'
        log = tracker.get_slot('log')
        print(f"Retrieved log value: {log}")
        
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")

        # Define the destination directory and path
        destination_dir = os.path.join(current_directory, "Simod", "resources", "event_logs")
        destination_path = os.path.join(destination_dir, os.path.basename(log))
        print(f"Destination path: {destination_path}")

        # Ensure the destination directory exists
        os.makedirs(destination_dir, exist_ok=True)

        # Copy the log file to the destination path
        try:
            shutil.copy(os.path.abspath(log), destination_path)
            print(f"Copied log file to: {destination_path}")
        except Exception as e:
            print(f"Failed to copy log file: {e}")
            return []

        # Define the path to the complete configuration file
        config_file_path = os.path.join(current_directory, "Simod", "resources", "config", "configuration_example.yml")
        # Read the complete configuration file
        try:
            with open(config_file_path, "r") as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            print("complete_configuration.yml file not found.")
            return []

        # Update the train_log_path with the new log path
        config['common']['train_log_path'] = destination_path

        # Write the modified configuration to a new file without comments
        new_config_path = os.path.join(current_directory, "Simod", "resources", "config", "modified_configuration.yml")
        try:
            with open(new_config_path, "w") as file:
                yaml.dump(config, file, default_flow_style=False)
            print(f"Generated new configuration file at: {new_config_path}")
        except Exception as e:
            print(f"Failed to write new configuration file: {e}")
            return []

        # Save the destination path into a slot
        return [SlotSet("destination_path", new_config_path)]
    
        #return []