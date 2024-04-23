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
class ValidateModifyWorkingTimeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_modify_working_time_form"

    @staticmethod
    def modify_working_time_name_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_timetables = esc.extract_timetables(model_path)

        return list(df_timetables['timetableName'])

    @staticmethod
    def modify_working_time_resource_db(tracker) -> List[Text]:
        """Database of supported resource timetables."""

        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def modify_working_time_weekday_db() -> List[Text]:
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

    def validate_modify_working_time_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_name value."""

        timetables = self.modify_working_time_name_db(tracker)

        if value.lower() in [x.lower() for x in timetables]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"modify_working_time_name": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_name")
            for timetable in timetables:
                dispatcher.utter_message(timetable)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"modify_working_time_name": None}

    def validate_modify_working_time_from_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_from_time value."""

        if self.is_hour(value):
            return {"modify_working_time_from_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_from_time")
            # validation failed, set slot to None
            return {"modify_working_time_from_time": None}

    def validate_modify_working_time_to_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_to_time value."""

        if self.is_hour(value):
            return {"modify_working_time_to_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_to_time")
            # validation failed, set slot to None
            return {"modify_working_time_to_time": None}

    def validate_modify_working_time_from_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_from_weekday value."""

        weekdays = self.modify_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"modify_working_time_from_weekday": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_from_weekday")
            for weekday in weekdays:
                dispatcher.utter_message(weekday)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"modify_working_time_from_weekday": None}

    def validate_modify_working_time_to_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_to_weekday value."""

        weekdays = self.modify_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"modify_working_time_to_weekday": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_to_weekday")
            for weekday in weekdays:
                dispatcher.utter_message(weekday)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"modify_working_time_to_weekday": None}

class ModifyWorkingTimeForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "modify_working_time_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["modify_working_time_name", "modify_working_time_from_time", "modify_working_time_to_time", 
        "modify_working_time_from_weekday", "modify_working_time_to_weekday"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class AskForModifyWorkingTimeName(Action):
    def name(self) -> Text:
        return "action_ask_modify_working_time_name"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        dispatcher.utter_message(text="Which timetable do you want to modify?")

        model_path = tracker.get_slot("model")
        df_timetables = esc.extract_timetables(model_path)
        for timetable in df_timetables['timetableName']:
            dispatcher.utter_message(text=timetable)

        return []