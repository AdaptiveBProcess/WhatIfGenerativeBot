from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_core_sdk.forms import FormAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *
import re

class AskForRule(Action):
    def name(self) -> Text:
        return "action_ask_for_rules"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(text="Please write your rule:")
        
        return []

class ValidateRuleForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_rule_form"

    def validate_rule(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate rule_form value."""
        #return value
        #print(f"El valor es {value}")
        # Check if the rule matches the format: A >> B
        if re.match(r'^.+ >> .+$', value):
            return {"rule": value}
        # Check if the rule matches the format: A >> * >> B
        elif re.match(r'^.+ >> \* >> .+$', value):
            return {"rule": value}
        # Check if the rule matches the format: A
        elif re.match(r'^.+$', value):
            return {"rule": value}
        # Check if the rule matches the format: ^A
        elif re.match(r'^\^\w+$', value):
            return {"rule": value}
        else:
            dispatcher.utter_message("Wrong format, please verify rule")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"rule": None}

class RuleForm(FormAction):
    def name(self):
        return "rule_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["rule"]

    def submit(self):
        return []
