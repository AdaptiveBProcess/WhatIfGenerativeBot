# This file contains the actions for the declarative process simulation
from typing import Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions import *
from actions import declarative_changing_variables as dv
import subprocess
import shutil
import os
import glob

class ActionDeclarativeActionRules(Action):
    
    def name(self) -> Text:
        return "action_declarative_action_rules"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        option_selected = tracker.get_slot("option")
        event_log= tracker.get_slot("log")
        rule=tracker.get_slot("rule")
        if option_selected == "Flux":
            model=tracker.get_slot("model")
            dv.ChangeModelNameDeclarative(model)
        elif option_selected == "Both":
            model=tracker.get_slot("comparison_scenario")
        else:
            print("No way this gets here")
        #print(model)
        with open('DeclarativeProcessSimulation/GenerativeLSTM/rules.ini', 'w') as f:
            f.write("# Production\n")
            f.write("[RULES]\n")
            f.write(f"path =  {rule}\n")
            f.write("variation = =1\n")
        destination_path = 'DeclarativeProcessSimulation/GenerativeLSTM/input_files'
        shutil.copy(event_log, destination_path)           
        env_name='deep_generator'
        dv.ChangeModelNameTraining(event_log)
        log_name=os.path.basename(event_log)
        directory='DeclarativeProcessSimulation/GenerativeLSTM/output_files'
        dv.ReturnFolderName(directory)
        dv.ChangeModelName(log_name)    
        script_path = "DeclarativeProcessSimulation\dg_prediction.py"
        command=f'python {script_path} --config .\prediction.yml'
        subprocess.Popen(f'conda run -n {env_name} {command}', shell=True)
        dispatcher.utter_message(text='Process running in background, you will see new files on declarative\DeclarativeProcessSimulation\output_files when finishes')
        return []