from dis import dis
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, List
from actions.inc_demand import *

class ActionSelectProcess(Action):
    """
    Action for menu, select
    """

    def name(self) -> Text:
        return "action_select_process"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
        option_selected = tracker.get_slot("option")
        print(option_selected)
        inc_percentage = float(next(tracker.get_latest_entity_values("inc_percentage")))
        if(option_selected == "Parameter"):
            return [FollowupAction('action_increase_demand')]
        elif(option_selected == "Flux"):
            dispatcher.utter_message(text='After loading the model, please write flow to continue')              
            return [FollowupAction('action_declarative_action_rules')]          
        elif(option_selected == "Both"):
            return [FollowupAction('action_increase_demand')]
        return []