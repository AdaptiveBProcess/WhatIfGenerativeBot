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

class ActionDecreaseDemand(Action):
    """
    Action for decrease demand
    """

    def name(self) -> Text:
        return "action_decrease_demand"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        model_path = tracker.get_slot("model")
        dec_percentage = float(next(tracker.get_latest_entity_values("inc_percentage")))
        
        output_message,org_message, new_model_path, sce_name= decrease_demand(dec_percentage,model_path)
        
        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(output_message)
        
        return [SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name)]
    
def decrease_demand(dec_percentage,model_path):

    bimp_path = 'bimp\qbp-simulator-engine_with_csv_statistics.jar'
    percentage = dec_percentage/100 if np.abs(dec_percentage) > 1 else dec_percentage
    p = int(np.abs(percentage)*100)
    sce_name = 'Decreased demand in {} percent'.format(p)
    new_model_path = esc.modify_bimp_model_instances(model_path, percentage)
    csv_output_path = 'outputs/demand/output_dec_demand_{}.csv'.format(sce_name)
    esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
    output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Decrease demand')
    csv_org_path = 'outputs/demand/output_baseline.csv'
    esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
    org_message = esc.return_message_stats_complete(csv_org_path, 'Stats for the Baseline scenario')

    return output_message, org_message, model_path, sce_name    