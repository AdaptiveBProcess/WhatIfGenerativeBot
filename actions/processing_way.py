from dis import dis
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_core_sdk.forms import FormAction
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *


import numpy as np
import pandas as pd
import re
from glob import glob
import string
import random
import uuid
from datetime import datetime
import time
import json
import os

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