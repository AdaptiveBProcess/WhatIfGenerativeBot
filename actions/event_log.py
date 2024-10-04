# Description: This file contains the code for the action that asks the user to choose a log file from the list of available logs.
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
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
    
class AskForLog(Action):
    def name(self) -> Text:
        return "action_ask_log"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="Select a log")

        logs = {idx: x for idx, x in enumerate(glob('inputs/*.xes'), start=1)}
        
        for key in logs.keys():
            dispatcher.utter_message(text=json.dumps({key : logs[int(key)]}))
        
        return []

class ValidateChooseLogForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_choose_log_form"

    @staticmethod
    def logs_db() -> List[Text]:

        logs = {idx: x for idx, x in enumerate(glob('inputs/*.xes'), start=1)}
        return logs

    def validate_log(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate log value"""

        logs = self.logs_db()
        try:
            if int(slot_value) in logs.keys():
                dispatcher.utter_message(text='Loaded model selected: ' + logs[int(slot_value)])
                return {"log": logs[int(slot_value)]}
            else:
                dispatcher.utter_message(text='Please enter a valid option for log')
                for key in logs.keys():
                    dispatcher.utter_message(text=json.dumps({key : logs[key]}))
                return {"log": None}
        except:
            return {"log": slot_value}