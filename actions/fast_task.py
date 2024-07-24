# This file contains the code for the action that will be executed when the user wants to make a task faster.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions.inc_demand import *
import os
import shutil
class ActionFastTask(Action):
    def name(self) -> Text:
        return "action_fast_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = tracker.get_slot("model")

        df_tasks, task_dist = esc.extract_task_add_info(model_path)
        
        task = tracker.get_slot("fast_task_name")

        percentage = int(tracker.get_slot("fast_task_percentage"))/100

        df_tasks.loc[df_tasks['name'].str.lower() == task.lower(), ['mean']] = (1-percentage)*int(df_tasks[df_tasks['name'].str.lower() == task.lower()]['mean'].values[0])

        elements = """
            <qbp:elements>
                {}
            </qbp:elements>
        """
        
        element = """      <qbp:element id="{}" elementId="{}">
                <qbp:durationDistribution type="{}" mean="{}" arg1="{}" arg2="{}">
                <qbp:timeUnit>{}</qbp:timeUnit>
                </qbp:durationDistribution>
                <qbp:resourceIds>
                <qbp:resourceId>{}</qbp:resourceId>
                </qbp:resourceIds>
            </qbp:element>
        """
        
        df_tasks['element'] = df_tasks.apply(lambda x: element.format(x['id'], x['elementId'], x['type'], x['mean'], \
                                                                    x['arg1'], x['arg2'], x['timeUnit'], x['resourceId']), \
                                            axis= 1)
            
        new_elements = elements.format("""""".join(df_tasks['element']))
        
        with open(model_path) as file:
            model= file.read()

        new_model = model.replace('\n'.join(task_dist[0]), new_elements)
        sce_name = '_{}_faster_{}'.format(percentage, task)
        
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/fast_slow_task/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'outputs/fast_slow_task/output_{}.csv'.format(sce_name)
        esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Faster Task')
        
        csv_org_path = 'outputs/fast_slow_task/output_baseline.csv'
        esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = esc.return_message_stats_complete(csv_org_path, 'Stats for the baseline scenario')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)
        option_selected = tracker.get_slot("option")
        if(option_selected == "Both"):
            dir_path = 'inputs/fast_slow_task/models/'
            files = glob.glob(dir_path + '*')
            source_path = max(files, key=os.path.getctime)
            target_path = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/simod/'
            target_path_files = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/'
            shutil.copy(source_path, target_path)
            shutil.copy(source_path, target_path_files)
            return [SlotSet("fast_task_name", None),
                    SlotSet("comparison_scenario", new_model_path),
                    SlotSet("name_scenario", sce_name),
                    SlotSet("fast_task_percentage", None),
                    FollowupAction('action_declarative_action_rules')]
        return [SlotSet("fast_task_name", None),
                SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name),
                SlotSet("fast_task_percentage", None)]