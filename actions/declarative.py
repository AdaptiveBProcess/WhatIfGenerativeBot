# This file contains the actions for the declarative process simulation
from typing import Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, List
from rasa_sdk.events import EventType
from actions import *
from actions import declarative_changing_variables as dv
import subprocess
import shutil
import os
import glob
class ActionDeclarativeActionRules(Action):
    def name(self) -> Text:
        return "action_declarative_action_rules"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        option_selected = tracker.get_slot("option")
        event_log= tracker.get_slot("log")
        rule=tracker.get_slot("rule")
        if option_selected == "Flux":
            model=tracker.get_slot("model")
            dv.ChangeModelNameDeclarative(model)
        elif option_selected == "Both":
            model=tracker.get_slot("comparison_scenario")
        else:
            print("how")
        #print(model)
        with open('declarative/DeclarativeProcessSimulation/GenerativeLSTM/rules.ini', 'w') as f:
            f.write("# Production\n")
            f.write("[RULES]\n")
            f.write(f"path =  {rule}\n")
            f.write("variation = =1\n")
        destination_path = 'declarative/DeclarativeProcessSimulation/GenerativeLSTM/input_files'
        shutil.copy(event_log, destination_path)           
        env_name='deep_generator'
        #TODO: Include all original chatbot rules (Parameters)
        #TODO: UI (reusar)
        #TODO: Ajustar validaciones del declarative
        #TODO: Mostrar metricas en una grafica

        #TODO: Varias reglas para el declarative!!!!
        #TODO: Definir los cambios 
        #TODO: Halucinar una vez cada regla            
        #TODO: Variation no tiene funcionalidad
        #TODO: SIMOD puede llamarse 2 veces
        #TODO: La entrada del chatbot es un modelo de simulación ASIS, es el que entrega SIMOD.
        #TODO: Visualizar y comparar los modelos , e integrar gráficas
        #Este codigo cambia en los archivos del codigo los valores necesarios para que funcione
        dv.ChangeModelNameTraining(event_log)
        #mandar el modelo a alucinar (Mas o menos una hora)
        #script_path = "declarative/DeclarativeProcessSimulation/dg_training.py"
        #subprocess.call(["python", script_path])
        log_name=os.path.basename(event_log)
        directory='declarative/DeclarativeProcessSimulation/GenerativeLSTM/output_files'
        dv.ReturnFolderName(directory)
        dv.ChangeModelName(log_name)
        dir_path = 'inputs/demand/models/'
        files = glob.glob(dir_path + '*')
        file_path = max(files, key=os.path.getctime)
        #file_name = os.path.basename(files_path)
        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
        if option_selected == "Flux":
            settings=f"    settings['asis_bpmn_path'] = os.path.join('GenerativeLSTM','input_files', 'simod', settings['file'] + '.bpmn')"
            dv.ChangeModelNameDeclarative(settings)
        elif option_selected == "Both":
            settings=f"    settings['asis_bpmn_path'] = os.path.join('GenerativeLSTM','input_files', 'simod', '{file_name_without_extension}' + '.bpmn')"
            dv.ChangeModelNameDeclarative(settings)             
        script_path = "declarative\DeclarativeProcessSimulation\dg_prediction.py"
        command=f'python {script_path}'
        subprocess.Popen(f'conda run -n {env_name} {command}', shell=True)
        dispatcher.utter_message(text='Process running in background, you will see new files on declarative\DeclarativeProcessSimulation\output_files when finishes')
        return []