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
    
class AskForModel(Action):
    def name(self) -> Text:
        return "action_ask_model"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="On which of these models?")

        models = {idx: x for idx, x in enumerate(glob('inputs/*.bpmn'), start=1)}
        
        for key in models.keys():
            dispatcher.utter_message(text=json.dumps({key : models[int(key)]}))
        
        return []

class ValidateChooseModelForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_choose_model_form"

    @staticmethod
    def models_db() -> List[Text]:
        """Database of supported models."""

        models = {idx: x for idx, x in enumerate(glob('inputs/*.bpmn'), start=1)}
        return models

    def validate_model(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate compared_scenarios value."""

        models = self.models_db()
        try:
            if int(value) in models.keys():
                return {"model": models[int(value)]}
            else:
                dispatcher.utter_message(text='Please enter a valid option for model')
                for key in models.keys():
                    dispatcher.utter_message(text=json.dumps({key : models[key]}))
                return {"model": None}
        except:
            return {"model": value}

class ChooseModelForm(FormAction):

    def name(self):
        return "choose_model_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        return ["model"]


    def submit(self):
        return []

