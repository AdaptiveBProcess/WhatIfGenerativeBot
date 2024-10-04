# This file contains the code for the action that removes a resource from the model and executes the simulation for the new model.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions.inc_demand import *
import glob
import os
import shutil
class ActionRemoveResources(Action):
    def name(self) -> Text:
        return "action_remove_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = tracker.get_slot("model")

        df_resources = esc.extract_resources(model_path)
        df_timetables = esc.extract_timetables(model_path)
        
        res_remove = tracker.get_slot("remove_resources_role")
        new_res_remove = tracker.get_slot("remove_resources_transfer_role")

        df_elements = esc.extract_elements(model_path)
        df_tasks = esc.extract_tasks(model_path)
        df_tasks_elements = df_tasks.merge(df_elements, how='left', on='elementId')
        df = df_tasks_elements[['taskName', 'elementId', 'resourceId']].merge(df_resources, how='left', on='resourceId')

        resource = df_resources[df_resources['resourceName'] == res_remove][['resourceId', 'resourceName']]
        new_resource = df_resources[df_resources['resourceName'] == new_res_remove ][['resourceId', 'resourceName']]
        
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
                
        # Extract new elements and replace old one with new elements extracted
        new_elements = []
        for i in range(len(elements_list)):
            element = elements_list[i]
            old_e = list(resource['resourceId'])[0]
            new_e = list(new_resource['resourceId'])[0]
            if '<qbp:resourceId>{}</qbp:resourceId>'.format(list(resource['resourceId'])[0]) in element:
                new_element = element.replace(old_e, new_e)
            else:
                new_element = element
            new_elements.append(new_element)
        
        new_elements = '\n'.join([element_lines[0]] + new_elements + [element_lines[-1]])
        with open(model_path) as file:
            model= file.read()
        new_model = model.replace(elements, new_elements) 
        
        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e).split('\n')
        new_resources = '\n'.join([x for x in resources if 'name="{}"'.format(list(resource['resourceName'])[0]) not in x])
        new_model = new_model.replace('\n'.join(resources), new_resources)
        
        new_model_path = model_path.split('.')[0] + '_rem_resource_{}'.format(res_remove.replace(' ', '_')) + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/resources/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
        
        sce_name = 'Remotion of resource {}'.format(res_remove)
        csv_output_path = 'outputs/resources/output_rem_resource_{}.csv'.format(res_remove.replace(' ', '_'))
        esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Remove resource')
        
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
            return [SlotSet("remove_resources_role", None),
                    SlotSet("comparison_scenario", new_model_path),
                    SlotSet("name_scenario", sce_name),
                    SlotSet("remove_resources_transfer_role", None),
                    FollowupAction('action_declarative_action_rules')]
        return [SlotSet("remove_resources_role", None),
                SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name),
                SlotSet("remove_resources_transfer_role", None)]