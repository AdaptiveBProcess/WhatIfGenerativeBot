from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_core_sdk.forms import FormAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *




class AskForProcessingOption(Action):
    def name(self) -> Text:
        return "action_ask_processing_option"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="How do you want to process this model?")

        options = {
            1: "Parameter",
            2: "Flux",
            3: "Both"
        }
        
        for key, value in options.items():
            dispatcher.utter_message(text=f"{key}. {value}")
        
        return []

class ValidateProcessingOptionForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_processing_option_form"

    @staticmethod
    def options_db() -> Dict[int, Text]:
        """Database of supported options."""

        return {
            1: "Parameter",
            2: "Flux",
            3: "Both"
        }

    def validate_option(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate option value."""

        options = self.options_db()
        try:
            if int(value) in options.keys():
                print(value)
                return {"option": options[int(value)]}
            else:
                dispatcher.utter_message(text='Please, type a valid option for this menu')
                for key, value in options.items():
                    dispatcher.utter_message(text=f"{key}. {value}")
                return {"option": None}
        except:
            return {"option": value}

class ProcessingOptionForm(FormAction):

    def name(self):
        return "processing_option_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        return ["option"]

    def submit(self):
        return []
