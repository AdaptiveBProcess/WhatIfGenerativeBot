from . import bimp_essential as esc
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions import *
from rasa_sdk.events import FollowupAction
import os
class ActionGenerateCanonical(Action):
    """
    Action to generate canonical
    """

    def name(self) -> Text:
        return "action_generate_canonical"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
        model_path = tracker.get_slot("log")
        os.chdir("../Simod")
        #command = "conda run -n Simod simod --configuration resources/config/configuration_example.yml"
        command = ""
        os.system(command)
        return []