from dis import dis
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions import *
from actions import declarative_changing_variables as dv
import subprocess
import re
import shutil
import pyuac
import os
import glob

class ActionDeclarativeActionRules(Action):
    def name(self) -> Text:
        return "action_train_model"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        print("Training model")
        env_name='deep_generator'
        script_path = "declarative\DeclarativeProcessSimulation\dg_training.py"
        command=f'python {script_path}'
        subprocess.Popen(f'conda run -n {env_name} {command}', shell=True)
        dispatcher.utter_message(text='Process running in background, you will see new files on declarative\DeclarativeProcessSimulation\output_files when finishes')