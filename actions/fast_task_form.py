# Description: This file contains the code for the action that asks the user to choose a log file from the list of available logs.
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *

class ValidateFastTaskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_fast_task_form"

    @staticmethod
    def fast_task_name_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_tasks, task_dist = esc.extract_task_add_info(model_path)

        return list(df_tasks['name'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_fast_task_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        tasks = self.fast_task_name_db(tracker)

        if value.lower() in [x.lower() for x in tasks]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"fast_task_name": value}
        else:
            dispatcher.utter_message(response="utter_wrong_fast_task_name")
            for task in tasks:
                dispatcher.utter_message(task)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"fast_task_name": None}

    def validate_fast_task_percentage(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate fast_task_percentage value."""

        if self.is_int(value) and int(value) > 0 and int(value) < 100:
            return {"fast_task_percentage": value}
        else:
            dispatcher.utter_message(response="utter_wrong_fast_task_percentage")
            # validation failed, set slot to None
            return {"fast_task_percentage": None}

class AskForFastTaskName(Action):
    def name(self) -> Text:
        return "action_ask_fast_task_name"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="Which task do you want to become faster?")
        
        model_path = tracker.get_slot("model")
        df_tasks = esc.extract_tasks(model_path)
        for task in df_tasks['taskName']:
            dispatcher.utter_message(text=task)
        
        return []
