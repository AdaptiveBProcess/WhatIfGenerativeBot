# Import required modules at the beginning of the file
from typing import List, Text, Dict, Any
from glob import glob
from rasa_sdk import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.events import EventType
from rasa_sdk import Action
import json

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
        """Database of supported models"""
        models = {idx: x for idx, x in enumerate(glob('inputs/*.bpmn'), start=1)}
        return models

    def validate_model(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate model value."""
        models = self.models_db()
        if int(slot_value) in models.keys():
             dispatcher.utter_message(text='Loaded model selected: ' + models[int(slot_value)])
             return {"model": models[int(slot_value)]}
        else:
             dispatcher.utter_message(text='Please enter a valid option for model')
             for key in models.keys():
                 dispatcher.utter_message(text=json.dumps({key : models[key]}))
             return {"model": None}