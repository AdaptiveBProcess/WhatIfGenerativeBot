# Description: Rasa form action for creating a new working time in the model.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *
from datetime import datetime

class ValidateCreateWorkingTimeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_create_working_time_form"

    @staticmethod
    def create_working_time_name_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_timetables = esc.extract_timetables(model_path)

        return list(df_timetables['timetableName'])

    @staticmethod
    def create_working_time_resource_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def create_working_time_weekday_db() -> List[Text]:
        """Database of supported roles for working times."""

        return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_hour(string: Text) -> bool:
        """Check if a string have hour time format"""
        try:
            datetime.strptime(string, '%H:%M:%S')
            return True
        except:
            return False

    def validate_create_working_time_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_name value."""

        timetables = self.create_working_time_name_db(tracker)

        if value.lower() not in [x.lower() for x in timetables]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_name": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_name")
            for timetable in timetables:
                dispatcher.utter_message(timetable)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_name": None}

    def validate_create_working_time_from_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_from_time value."""

        if self.is_hour(value):
            return {"create_working_time_from_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_from_time")
            # validation failed, set slot to None
            return {"create_working_time_from_time": None}

    def validate_create_working_time_resource(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_resource value."""

        resources = self.create_working_time_resource_db(tracker)

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_resource": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_resource")
            for resource in resources:
                dispatcher.utter_message(resource)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_resource": None}

    def validate_create_working_time_to_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_to_time value."""

        if self.is_hour(value):
            return {"create_working_time_to_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_to_time")
            # validation failed, set slot to None
            return {"create_working_time_to_time": None}

    def validate_create_working_time_from_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_from_weekday value."""

        weekdays = self.create_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_from_weekday": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_from_weekday")
            for weekday in weekdays:
                dispatcher.utter_message(weekday)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_from_weekday": None}

    def validate_create_working_time_to_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_to_weekday value."""

        weekdays = self.create_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_to_weekday": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_to_weekday")
            for weekday in weekdays:
                dispatcher.utter_message(weekday)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_to_weekday": None}

class AskForCreateWorkingTimeResource(Action):
    def name(self) -> Text:
        return "action_ask_create_working_time_resource"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="To which resource do you want to apply the new timetable?")
        
        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)
        for resource in df_resources['resourceName']:
            dispatcher.utter_message(text=resource)
        
        return []