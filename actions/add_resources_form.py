# Description: Rasa form for adding resources to the model.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *


class ValidateAddResourcesForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_add_resources_form"

    @staticmethod
    def add_resource_time_table_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_timetables = esc.extract_timetables(model_path)

        return list(df_timetables['timetableName'])

    @staticmethod
    def add_resource_new_role_db(tracker) -> List[Text]:
        """Database of supported roles for new role."""

        model_path = tracker.get_slot("model")
        df_tasks = esc.extract_tasks(model_path)

        return list(df_tasks['taskName'])

    @staticmethod
    def add_resource_name_db(tracker) -> List[Text]:
        """Database of supported roles for new role."""

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

    def validate_add_resource_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        resources = self.add_resource_name_db(tracker)

        if value.lower() not in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"add_resource_name": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_name")
            for resource in resources:
                dispatcher.utter_message(resource)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"add_resource_name": None}

    def validate_add_resource_time_table(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_time_table value."""

        timetables = self.add_resource_time_table_db(tracker)

        if value.lower() in [x.lower() for x in timetables]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"add_resource_time_table": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_time_table")
            for timetable in timetables:
                dispatcher.utter_message(timetable)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"add_resource_time_table": None}

    def validate_add_resource_new_role(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_new_role value."""

        tasks = self.add_resource_new_role_db(tracker)
        
        if value.lower() in [x.lower() for x in tasks]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"add_resource_new_role": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_new_role")
            for task in tasks:
                dispatcher.utter_message(task)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"add_resource_new_role": None}

    def validate_add_resource_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_amount value."""

        if self.is_int(value) and int(value) > 0:
            return {"add_resource_amount": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_amount")
            # validation failed, set slot to None
            return {"add_resource_amount": None}

    def validate_add_resource_cost(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_cost value."""

        if self.is_int(value) and int(value) > 0:
            return {"add_resource_cost": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_cost")
            # validation failed, set slot to None
            return {"add_resource_cost": None}

class AskForAddResourceTimeTable(Action):
    def name(self) -> Text:
        return "action_ask_add_resource_time_table"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="Which of these timetables?")
        
        model_path = tracker.get_slot("model")
        df_timetables = esc.extract_timetables(model_path)
        for timetable in df_timetables['timetableName']:
            dispatcher.utter_message(text=timetable)
        
        return []
class AskForAddResourceNewRole(Action):
    def name(self) -> Text:
        return "action_ask_add_resource_new_role"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="To which task do you want to assign the new resource?")
        
        model_path = tracker.get_slot("model")
        df_tasks = esc.extract_tasks(model_path)
        for task in df_tasks['taskName']:
            dispatcher.utter_message(text=task)
        
        return []