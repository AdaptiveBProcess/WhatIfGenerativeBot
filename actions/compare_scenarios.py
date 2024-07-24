# This file contains the action that compares the scenarios selected by the user.
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, List
from actions.inc_demand import *
class CompareScenarios(Action):

    def name(self) -> Text:
        return "action_compare_scenarios"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'bimp/qbp-simulator-engine_with_csv_statistics.jar'

        compared_scenarios = tracker.get_slot("compared_scenario_names")

        scenario_paths = []
        for comparison_scenario in compared_scenarios:
            name_sce = comparison_scenario.split('\\')[-1].split('.')[0].replace('_', ' ')
            csv_output_path = 'outputs/comparison/' + comparison_scenario.replace('bpmn', 'csv').split('\\')[-1]
            esc.execute_simulator_simple(bimp_path, comparison_scenario, csv_output_path)
            scenario_message = esc.return_message_stats_complete(csv_output_path, name_sce)
            dispatcher.utter_message(text=scenario_message)

        return [SlotSet("compared_scenarios", None),
                SlotSet("compared_scenario_names", None)]