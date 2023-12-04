from . import bimp_essential as esc
from dis import dis
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions import *
from rasa_sdk.events import FollowupAction
import glob
import os
import shutil
class ActionIncreaseDemand(Action):
    """
    Action for increase demand
    """

    def name(self) -> Text:
        return "action_increase_demand"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:      
        model_path = tracker.get_slot("model")
        inc_percentage = float(next(tracker.get_latest_entity_values("inc_percentage")))
        output_message,org_message, new_model_path, sce_name=increase_demand(inc_percentage,model_path)
        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(output_message)
        option_selected = tracker.get_slot("option")
        if(option_selected == "Both"):
            dir_path = 'inputs/demand/models/'
            files = glob.glob(dir_path + '*')
            source_path = max(files, key=os.path.getctime)
            target_path = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/simod/'
            target_path_files = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files/'
            shutil.copy(source_path, target_path)
            shutil.copy(source_path, target_path_files)
            return [SlotSet("comparison_scenario", new_model_path),
                    SlotSet("name_scenario", sce_name),
                    FollowupAction('action_declarative_action_rules')]
        
        return [SlotSet("comparison_scenario", new_model_path),
                SlotSet("name_scenario", sce_name)]    
def increase_demand(inc_percentage,model_path):

    bimp_path = 'bimp\qbp-simulator-engine_with_csv_statistics.jar'
    percentage = inc_percentage/100 if inc_percentage > 1 else inc_percentage 
    sce_name = str(int(percentage*100))
    new_model_path = esc.modify_bimp_model_instances(model_path, percentage)
    csv_output_path = 'outputs/demand/output_inc_demand_{}.csv'.format(sce_name)      
    esc.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
    output_message = esc.return_message_stats_complete(csv_output_path, 'Stats for the what-if scenario: Increase Demand')
    csv_org_path = 'outputs/demand/output_baseline.csv'
    esc.execute_simulator_simple(bimp_path, model_path, csv_org_path)
    org_message = esc.return_message_stats_complete(csv_org_path, 'Stats for the Baseline Scenario')

    return output_message, org_message, model_path, sce_name