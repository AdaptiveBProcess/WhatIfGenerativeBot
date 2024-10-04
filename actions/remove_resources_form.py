# Description: Rasa form action for removing resources from the model.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *


class ValidateRemoveResourceskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_remove_resources_form"

    @staticmethod
    def remove_resources_role_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)

        return list(df_resources['resourceName'])

    def validate_remove_resources_role(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate remove_resources_role value."""

        resources = self.remove_resources_role_db(tracker)

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"remove_resources_role": value}
        else:
            dispatcher.utter_message(response="utter_wrong_remove_resources_role")
            for resource in resources:
                dispatcher.utter_message(resource)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"remove_resources_role": None}

    def validate_remove_resources_transfer_role(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate remove_resources_transfer_role value."""

        resources = self.remove_resources_role_db(tracker)

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"remove_resources_transfer_role": value}
        else:
            dispatcher.utter_message(response="utter_wrong_remove_resources_transfer_role")
            for resource in resources:
                dispatcher.utter_message(resource)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"remove_resources_transfer_role": None}

class AskForRemoveResourceRole(Action):
    def name(self) -> Text:
        return "action_ask_remove_resources_role"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="Which resource do you want to remove?")
        
        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)
        for resource in df_resources['resourceName']:
            dispatcher.utter_message(text=resource)
        
        return []

class AskForRemoveResourceTransferRole(Action):
    def name(self) -> Text:
        return "action_ask_remove_resources_transfer_role"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="To which resource do you want to reallocate the removed resource tasks?")
        
        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)
        for resource in df_resources['resourceName']:
            if resource != tracker.get_slot("remove_resources_role"):
                dispatcher.utter_message(text=resource)        
        return []