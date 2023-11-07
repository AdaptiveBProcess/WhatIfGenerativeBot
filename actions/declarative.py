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

class ActionDeclarativeActionRules(Action):
    def name(self) -> Text:
        return "action_declarative_action_rules"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        dispatcher.utter_message(text='Aqui va lo declarativo')
        return []