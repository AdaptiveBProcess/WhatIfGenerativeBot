from dis import dis
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_core_sdk.forms import FormAction
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions.inc_demand import *
import json
#TODO: Remodularizar para que muestre todos los resultados con graficas comparativas
class ValidateComparisonScenariosForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_compare_scenarios_form"

    @staticmethod
    def scenarios_db() -> List[Text]:
        """Database of supported scenarios."""

        dict_scenarios = esc.extract_scenarios()
        return dict_scenarios

    def validate_compared_scenarios(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate compared_scenarios value."""

        scenarios = self.scenarios_db()
        scenarios_names = {x : scenarios[x].split('\\')[-1] for x in scenarios.keys()}
        input_scenarios = [int(x.strip()) for x in value.split(',') if x.strip() != '' and x.strip() != ' ' and x.strip().isdigit()]
        compared_scenarios = []

        if len(input_scenarios)==0:
            dispatcher.utter_message(response="utter_wrong_compared_scenarios")
            for scenario in scenarios_names.keys():
                dispatcher.utter_message(json.dumps({scenario: scenarios_names[scenario].split('\\')[-1].split('.')[0]}))
            return {"compared_scenario_names": None}
        else:
            for input_scenario in input_scenarios:

                if input_scenario in scenarios.keys():
                    # validation succeeded, set the value of the "cuisine" slot to value
                    compared_scenarios.append(scenarios[input_scenario])
            if len(compared_scenarios)>0:
                return {"compared_scenario_names": compared_scenarios}
            else:
                dispatcher.utter_message(response="utter_wrong_compared_scenarios")
                for scenario in scenarios_names.keys():
                    dispatcher.utter_message(json.dumps({scenario: scenarios_names[scenario].split('\\')[-1].split('.')[0]}))
                return {"compared_scenario_names": None}

class CompareScenariosForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "compare_scenarios_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["compared_scenarios"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """
        return []

class AskForComparedScenarios(Action):
    def name(self) -> Text:
        return "action_ask_compared_scenarios"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        dispatcher.utter_message(text="Which of the following scenarios do you want to compare? (write the number of scenarios separated by coma i.e. 1,2,4)")
        
        scenarios = esc.extract_scenarios()
        for scenario in scenarios.keys():
            dispatcher.utter_message(json.dumps({scenario: scenarios[scenario].split('\\')[-1].split('.')[0]}))
        
        return []