# This file contains the action that creates a new working time in the BPMN model and executes the simulation for the new scenario.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions.inc_demand import *
import pandas as pd
import re
import glob
import os
import shutil
class ActionCreateWorkingTime(Action):
    def name(self) -> Text:
        return "action_create_working_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = tracker.get_slot("model")
  
        ptt_s = '<qbp:timetables>'
        ptt_e = '</qbp:timetables>'
        time_tables_text = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        time_tables = time_tables_text.split('\n')
        
        data = []
        start = None
        end = None
        for idx, time_table in enumerate(time_tables):
            start = 0
            if '<qbp:timetable ' in time_table and start == None:
                start = idx
            elif '</qbp:timetable>' in time_table and end == None:
                end = idx
                data.append(time_tables[start:end+1])
                start, end = None, None
        
        df_tt = pd.DataFrame(data = [], columns = ['id','name','fromTime', 'toTime', 'fromWeekDay', 'toWeekDay'])
        ptts = ['id','name','fromTime', 'toTime', 'fromWeekDay', 'toWeekDay']
        for time_table in data:
            rules = []
            for line in time_table:
                row = {}
                for ptt in ptts:
                    ptt_s = r'{}="(.*?)"'.format(ptt)
                    text = re.search(ptt_s, line)
                    if ptt == 'id' and text != None:
                        id_tt = text.group(1)
                    elif ptt == 'name' and text != None:
                        name_tt = text.group(1)
                    elif text != None:
                        row[ptt] = text.group(1)
                if row != {}:
                    rules.append(row)
            df = pd.DataFrame(rules)
            df['id'] = id_tt
            df['name'] = name_tt
            df = df[ptts]
            df_tt = pd.concat([df_tt, df])

        scenario_name = []
        tt_id = tracker.get_slot("create_working_time_id")
        tt_name = tracker.get_slot("create_working_time_name")

        scenario_name.append('add_{}'.format(tt_name))

        new_tt_rules = []
        from_time = tracker.get_slot("create_working_time_from_time")
        to_time = tracker.get_slot("create_working_time_to_time")
        from_weekday = tracker.get_slot("create_working_time_from_weekday").upper()
        to_weekday = tracker.get_slot("create_working_time_to_weekday").upper()
        rule = [from_time, to_time, from_weekday, to_weekday]
        new_tt_rules.append(rule)

        new_tt_df = pd.DataFrame(new_tt_rules, columns = ['fromTime', 'toTime', 'fromWeekDay', 'toWeekDay'])
        new_tt_df['id'] = tt_id
        new_tt_df['name'] = tt_name

        df_tt = pd.concat([df_tt, new_tt_df[df_tt.columns]])
        
        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources_text = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        resources = resources_text.split('\n')
        
        ptts = ['id', 'name', 'totalAmount', 'costPerHour', 'timetableId']
        data = []
        for line in resources:
            row = {}
            for ptt in ptts:
                ptt_s = r'{}="(.*?)"'.format(ptt)
                text = re.search(ptt_s, line)
                if text != None:
                    row[ptt] = text.group(1)
            if row != {}:
                data.append(row)
                
        df_resources = pd.DataFrame(data)

        res_change_tt = tracker.get_slot("create_working_time_resource")

        df_resources.loc[df_resources['name'] == res_change_tt, 'timetableId'] = tt_id

        format_time_tables = """    <qbp:timetables>{}</qbp:timetables>"""
    
        format_time_table = """\n        <qbp:timetable id="{}" default="false" name="{}">
                <qbp:rules>{}</qbp:rules>
            </qbp:timetable>"""
        
        format_rules_time_tables = """\n            <qbp:rule fromTime="{}" toTime="{}" fromWeekDay="{}" toWeekDay="{}"/>"""
        
        time_tables = list(df_tt['name'].drop_duplicates())
        
        time_tables_updated = []
        for time_table in time_tables:
            df_time_table = df_tt[df_tt['name'] == time_table]
            name_tt = df_time_table['name'].values[0]
            id_tt = df_time_table['id'].values[0]
            df_time_table['rule'] = df_time_table.apply(lambda x: format_rules_time_tables.format(x['fromTime'], x['toTime'], x['fromWeekDay'], x['toWeekDay']), axis= 1)
            rules = """""".join(df_time_table['rule'])
            time_table_tmp = format_time_table.format(id_tt, name_tt, rules)
            time_tables_updated.append(time_table_tmp)
            
        final_time_tables = format_time_tables.format("""""".join(time_tables_updated))

        with open(model_path) as f:
            model = f.read()
            
        new_model = model.replace(time_tables_text, final_time_tables)

        resources = """    <qbp:resources>
          {} 
        </qbp:resources>"""
        
        resource = """<qbp:resource id="{}" name="{}" totalAmount="{}" costPerHour="{}" timetableId="{}"/>"""
        df_resources['resource'] = df_resources.apply(lambda x: resource.format(x['id'], x['name'], x['totalAmount'], \
                                                                                x['costPerHour'], x['timetableId']
                                                                                ), axis=1)
        new_resources = resources.format("""""".join(df_resources['resource']))
        
        new_model = new_model.replace(resources_text, new_resources)
    
        sce_name = '_' + ('_'.join(scenario_name)).replace('/', '_')
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/working_tables/models')
        
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'outputs/working_tables/output{}.csv'.format(sce_name)
        esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Timetable Creation')
        
        csv_org_path = 'outputs/working_tables/output_baseline.csv'
        esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = esc.return_message_stats_complete(csv_org_path, 'Stats for the baseline scenario')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)
        option_selected = tracker.get_slot("option")
        if(option_selected == "Both"):
            dir_path = 'inputs/working_tables/models/'
            files = glob.glob(dir_path + '*')
            source_path = max(files, key=os.path.getctime)
            target_path = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/simod/'
            target_path_files = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/'
            shutil.copy(source_path, target_path)
            shutil.copy(source_path, target_path_files)
            return [SlotSet("create_working_time_id", None),
                    SlotSet("create_working_time_name", None),
                    SlotSet("create_working_time_from_time", None),
                    SlotSet("create_working_time_to_time", None),
                    SlotSet("create_working_time_from_weekday", None),
                    SlotSet("create_working_time_resource", None),
                    SlotSet("comparison_scenario", new_model_path),
                    SlotSet("name_scenario", sce_name),
                    SlotSet("create_working_time_to_weekday", None),
                    FollowupAction('action_declarative_action_rules')]        
        return [SlotSet("create_working_time_id", None),
                SlotSet("create_working_time_name", None),
                SlotSet("create_working_time_from_time", None),
                SlotSet("create_working_time_to_time", None),
                SlotSet("create_working_time_from_weekday", None),
                SlotSet("create_working_time_resource", None),
                SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name),
                SlotSet("create_working_time_to_weekday", None)]