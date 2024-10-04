# This file contains the code for the action automate_task. This action is used to automate a task in the BPMN model.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions.inc_demand import *
class ActionAutomateTask(Action):
    def name(self) -> Text:
        return "action_automate_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = tracker.get_slot("model")

        with open(model_path) as file:
            model= file.read()

        df_tasks, _ = esc.extract_task_add_info(model_path)

        task = tracker.get_slot("automate_task_name")
        percentage = int(tracker.get_slot("automate_task_percentage"))/100

        df_tasks_new = df_tasks.copy()

        if percentage == 100:
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['type']] = 'UNIFORM'
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['mean']] = 0
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['arg1']] = 0.0
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['arg2']] = 0.0
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['resourceName']] = 'SYSTEM'
        else:
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['mean']] = (1-percentage)*df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['mean']]

            resource_msg = """      <qbp:element id="{}" elementId="{}">
                    <qbp:durationDistribution type="{}" mean="{}" arg1="{}" arg2="{}">
                    <qbp:timeUnit>{}</qbp:timeUnit>
                    </qbp:durationDistribution>
                    <qbp:resourceIds>
                    <qbp:resourceId>{}</qbp:resourceId>
                    </qbp:resourceIds>
                </qbp:element>"""

            elements_new = '\n'.join([resource_msg.format(x['id'], x['elementId'], x['type'], x['mean'], \
                        x['arg1'], x['arg2'], x['timeUnit'], x['resourceId']) for idx, x in df_tasks_new.iterrows()])

            elements_new = """    <qbp:elements>
            {}
    </qbp:elements>""".format(elements_new)
            ptt_s = '<qbp:elements>'
            ptt_e = '</qbp:elements>'
            elements_old = esc.extract_bpmn_resources(model_path, ptt_s, ptt_e)

            new_model = model.replace(elements_old, elements_new)

            sce_name = '_automate_task_{}'.format(task.replace(' ', '_'))

            new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
            new_model_path = new_model_path.replace('inputs','inputs/automate_task/models')
            with open(new_model_path, 'w+') as new_file:
                new_file.write(new_model)
                
            csv_output_path = 'outputs/automate_task/output_{}.csv'.format(sce_name)
            esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
            output_message = esc.return_message_stats(csv_output_path, 'Stats for the what-if scenario: Task Automation')

            csv_org_path = 'outputs/automate_task/output_baseline.csv'
            esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
            org_message = esc.return_message_stats(csv_org_path, 'Stats for the baseline scenario')

            dispatcher.utter_message(text=org_message)
            dispatcher.utter_message(text=output_message)
        
        return [SlotSet("automate_task_name", None),
                SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name),
                SlotSet("automate_task_percentage", None)]
