from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_core_sdk.forms import FormAction
from typing import Dict, Text, List
from actions.inc_demand import *

class ValidateChangeResourcesForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_change_resources_form"

    @staticmethod
    def change_resources_role_modify_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_change_resources_role_modify(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        resources = self.change_resources_role_modify_db(tracker)

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"change_resources_role_modify": value}
        else:
            dispatcher.utter_message(response="utter_wrong_change_resources_role_modify")
            for resource in resources:
                dispatcher.utter_message(resource)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"change_resources_role_modify": None}

    def validate_change_resources_new_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate change_resources_new_amount value."""

        if self.is_int(value) and int(value) > 0:
            return {"change_resources_new_amount": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_amount")
            # validation failed, set slot to None
            return {"change_resources_new_amount": None}

    def validate_change_resources_new_cost(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate change_resources_new_cost value."""

        if self.is_int(value) and int(value) > 0:
            return {"change_resources_new_cost": value}
        else:
            dispatcher.utter_message(response="utter_wrong_change_resources_new_cost")
            # validation failed, set slot to None
            return {"change_resources_new_cost": None}

class ChangeResourcesForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "change_resources_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["change_resources_role_modify", "change_resources_new_amount", "change_resources_new_cost"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []