from dis import dis
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *
import glob
import os
import shutil
import numpy as np
import uuid
import pandas as pd
class ActionAddResource(Action):
    def name(self) -> Text:
        return "action_add_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = tracker.get_slot("model")
        df_resources = esc.extract_resources(model_path)
        df_timetables = esc.extract_timetables(model_path)        
        resourceId = 'qbp_{}'.format(uuid.uuid4())
        resourceName = tracker.get_slot("add_resource_name")
        totalAmount = tracker.get_slot("add_resource_amount")
        costPerHour = tracker.get_slot("add_resource_cost")
        timetableName = tracker.get_slot("add_resource_time_table")
        task_new_role = tracker.get_slot("add_resource_new_role")
        
        csv_output_path, new_model_path , sce_name= add_new_resource(resourceName,df_timetables, timetableName, resourceId, costPerHour, task_new_role, totalAmount, model_path, df_resources)
        output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Resource Addition')
        
        csv_org_path = 'outputs/resources/output_baseline.csv'
        esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = esc.return_message_stats_complete(csv_org_path, 'Stats for the Baseline Scenario')
            
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
            return [SlotSet("add_resource_name", None),
                    SlotSet("add_resource_amount", None),
                    SlotSet("add_resource_cost", None),
                    SlotSet("add_resource_time_table", None),
                    SlotSet("comparison_scenario", new_model_path),
                    SlotSet("name_scenario", sce_name),
                    SlotSet("add_resource_new_role", None),
                    FollowupAction('action_declarative_action_rules')]  
        return [SlotSet("add_resource_name", None),
                SlotSet("add_resource_amount", None),
                SlotSet("add_resource_cost", None),
                SlotSet("add_resource_time_table", None),
                SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name),
                SlotSet("add_resource_new_role", None)]


def add_new_resource(resourceName, df_timetables, timetableName,resourceId, costPerHour, task_new_role, totalAmount, model_path, df_resources):
        
        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        timetableId = df_timetables[df_timetables['timetableName']== timetableName]['timetableId'].values[0]
        
        df_new_role = pd.DataFrame([{'resourceId':resourceId, 'resourceName':resourceName, 'totalAmount':totalAmount, \
                            'costPerHour':costPerHour, 'timetableId':timetableId}])
        df_resources = pd.concat([df_resources, df_new_role])
        
        df_elements = esc.extract_elements(model_path)
        df_tasks = esc.extract_tasks(model_path)
        df_tasks_elements = df_tasks.merge(df_elements, how='left', on='elementId')
        df = df_tasks_elements[['taskName', 'elementId', 'resourceId']].merge(df_resources, how='left', on='resourceId')
        
        df_transformed = df.copy()

        
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'resourceId'] = resourceId
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'resourceName'] = resourceName
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'totalAmount'] = totalAmount
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'costPerHour'] = costPerHour
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'timetableId'] = timetableId

        ptt_s = '<qbp:elements>'
        ptt_e = '</qbp:elements>'
        elements = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        element_lines = elements.split('\n')
        elements_list = []
        start, end = None, None
        for idx, line in enumerate(element_lines):
            if '<qbp:element ' in line and start == None:
                start = idx
            if '</qbp:element>' in line and end == None:
                end = idx
            if start != None and end != None:
                elements_list.append('\n'.join(element_lines[start:end+1]))
                start, end = None, None
                
        df = df.sort_values(by='taskName')
        df_transformed = df_transformed.sort_values(by='taskName')
        
        # Extract new elements and replace old one with new elements extracted
        new_elements = []
        for i in range(len(elements_list)):
            element = elements_list[i]
            old_elem = list(df[df['taskName'].str.lower() == task_new_role.lower()]['resourceId'])[0]
            new_elem = list(df_transformed[df_transformed['taskName'].str.lower() == task_new_role.lower()]['resourceId'])[0]
            if 'elementId="{}"'.format(list(df[df['taskName'].str.lower() == task_new_role.lower()]['elementId'])[0]) in element:
                new_element = element.replace(old_elem, new_elem)
                new_elements.append(new_element)
        
        new_elements = '\n'.join([element_lines[0]] + new_elements + [element_lines[-1]])
        
        with open(model_path) as file:
            model= file.read()
        new_model = model.replace(elements, new_elements)        
        
        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e).split('\n')
        new_res = '      <qbp:resource id="{}" name="{}" totalAmount="{}" costPerHour="{}" timetableId="{}"/>'.format(resourceId, resourceName, totalAmount, \
                                                                                                                costPerHour, timetableId)
        new_resources = '\n'.join(resources[:-1] + [new_res] + [resources[-1]])
        new_model = new_model.replace('\n'.join(resources), new_resources)
        
        new_model_path = model_path.split('.')[0] + '_add_resource_{}'.format(resourceName.replace(' ', '_')) + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/resources/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
        sce_name = resourceName.replace(' ', '_')
        csv_output_path = 'outputs/resources/output_add_resource_{}.csv'.format(sce_name)
        esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        return csv_output_path, new_model_path, sce_name