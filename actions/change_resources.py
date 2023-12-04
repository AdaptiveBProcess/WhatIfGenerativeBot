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

class AskForChangeResourceRoleModify(Action):
    def name(self) -> Text:
        return "action_ask_change_resources_role_modify"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="Which resource do you want to modify?")
        
        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)
        for resource in df_resources['resourceName']:
            dispatcher.utter_message(text=resource)
        
        return []
    
class ActionChangeResource(Action):
    def name(self) -> Text:
        return "action_change_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = tracker.get_slot("model")

        df_resources = esc.extract_resources(model_path)
        
        mod_res = tracker.get_slot("change_resources_role_modify")
        
        new_amount = tracker.get_slot("change_resources_new_amount")
        new_cost = tracker.get_slot("change_resources_new_cost")
        
        df_resources.loc[df_resources['resourceName']==mod_res, ['totalAmount']] = new_amount
        df_resources.loc[df_resources['resourceName']==mod_res, ['costPerHour']] = new_cost
        
        mod_name = mod_res.replace(' ', '_')

        resources = """    <qbp:resources>
            {} 
        </qbp:resources>"""

        resource = """<qbp:resource id="{}" name="{}" totalAmount="{}" costPerHour="{}" timetableId="{}"/>"""
        df_resources['resource'] = df_resources.apply(lambda x: resource.format(x['resourceId'], x['resourceName'], x['totalAmount'], \
                                                                                x['costPerHour'], x['timetableId']
                                                                                ), axis=1)
        new_resources = resources.format("""""".join(df_resources['resource']))

        with open(model_path) as f:
            model = f.read()

        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources_text = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e)

        new_model = model.replace(resources_text, new_resources)

        sce_name = '_mod_resource_{}'.format(mod_name)
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/resources/models')

        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
        
        csv_output_path = 'outputs/resources/output_mod_resource_{}.csv'.format(mod_name)
        esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Resource Modification')
        
        csv_org_path = 'outputs/resources/output_baseline.csv'
        esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = esc.return_message_stats_complete(csv_org_path, 'Stats for the baseline scenario')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)
        option_selected = tracker.get_slot("option")
        if(option_selected == "Both"):
            dir_path = 'inputs/resources/models/'
            files = glob.glob(dir_path + '*')
            source_path = max(files, key=os.path.getctime)
            target_path = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/simod/'
            target_path_files = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/'
            shutil.copy(source_path, target_path)
            shutil.copy(source_path, target_path_files)
            return [SlotSet("change_resources_role_modify", None),
                    SlotSet("change_resources_new_amount", None),
                    SlotSet("change_resources_new_cost", None),
                    SlotSet("comparison_scenario", new_model_path),
                    SlotSet("name_scenario", mod_name),
                    FollowupAction('action_declarative_action_rules')]
        return [SlotSet("change_resources_role_modify", None),
                SlotSet("change_resources_new_amount", None),
                SlotSet("change_resources_new_cost", None),
                SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", mod_name)]