from dis import dis
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions import *
from actions import declarative_changing_variables as dv
import subprocess
import re

class ActionDeclarativeActionRules(Action):
    def name(self) -> Text:
        return "action_declarative_action_rules"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        option_selected = tracker.get_slot("option")
        if(option_selected == "Flux"):
            model_path= tracker.get_slot("model")
        elif(option_selected == "Both"):
            model_path= tracker.get_slot("comparison_scenario")
        else:
            print("No deberias de estar aqui")
            exit(1)
        #This code extracts and verifies the rule of the form
        rule=tracker.get_slot("rule")
        boolean_rule=RuleVerify(rule)

        #TODO: Sacar el log de eventos desde chatbot
        if boolean_rule:
            #TODO: Forma de enviar Regla y resultado del alucinador al código
            #Este codigo cambia en los archivos del codigo los valores necesarios para que funcione
            dv.ChangeModelNameTraining(model_path)

            #mandar el modelo a alucinar (Mas o menos una hora)
            script_path = "DeclarativeProcessSimulation\dg_training.py"
            subprocess.call(["python", script_path])

            directory='actions\DeclarativeProcessSimulation\output_files'
            dv.ReturnFolderName(directory)
            dv.ChangeModelName(model_path)

            script_path = "DeclarativeProcessSimulation\dg_prediction.py"
            subprocess.call(["python", script_path])

        dispatcher.utter_message(text='Aqui va lo declarativo')
        return []
    
def RuleVerify(rule):
    patterns = ['^\w+ >> \w+$', '^\w+ >> .* >> \w+$', '^\w+$', '^\^\w+$']
    for pattern in patterns:
        if re.match(pattern, rule):
            return True    
    # If no match is found, return False
    return False