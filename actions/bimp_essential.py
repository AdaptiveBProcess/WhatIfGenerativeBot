import subprocess
import re
import pandas as pd
import os
import matplotlib.pyplot as plt
from glob import glob

def execute_simulator_simple(bimp_path, model_path, csv_output_path):
    args = ['java', '-jar', bimp_path, model_path, '-csv', csv_output_path]
    subprocess.run(args, stdout=open(os.devnull, 'wb'))
def modify_bimp_model_instances(path_bimp_model, inc_percentage):
    
    with open(path_bimp_model) as file:
        model_bimp = file.read()
    
    ptt = r'processInstances="(.*?)"'
    process_inst = int(re.search(ptt, model_bimp).group(1))
    new_instances = int(process_inst*(1+inc_percentage))

    rep_proc_ins = 'processInstances="{}"'.format(process_inst)
    new_rep_proc_ins = 'processInstances="{}"'.format(new_instances)
    model_bimp = model_bimp.replace(rep_proc_ins, new_rep_proc_ins)
    new_model_path = path_bimp_model.split('.')[0] + '_inst_{}'.format(new_instances) + '.bpmn'
    
    with open(new_model_path.replace('inputs','inputs/demand/models'), 'w+') as new_file:
        new_file.write(model_bimp)
    
    return new_model_path.replace('inputs','inputs/demand/models')


def return_message_stats_complete(stats_path, scenario_name):
    
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    
    ptt_s = 'Scenario statistics'
    ptt_e = 'Process Cycle Time (s) distribution' 
    text = extract_text(stats_path, ptt_s, ptt_e)

    data = [x.split(',') for x in text.split('\n') if x != '']
    df = pd.DataFrame(data = data[1:], columns=data[0])

    df['Average'] = df['Average'].astype(float).astype(str).apply(lambda x: format(float(x),".2f")).astype(float)
    df['Average'], df['Units'] = zip(*df.apply(lambda x: standarize_metric(x['Average'], x['KPI']), axis=1))
    df['Average'] = df['Average'].round(2)
    df['KPI'] = df.apply(lambda x: x['KPI'].replace(' (s)', ''), axis=1)

    message = '{} \n'.format(scenario_name)
    message += '\n'.join(df['KPI'] + ': ' + df['Average'].astype(str) + ' ' + df['Units'])
    # plt.plot.bar(df['KPI'],df['Average'])
    # plt.show()
    return message

def return_message_stats(stats_path, scenario_name):

    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    
    ptt_s = 'Scenario statistics'
    ptt_e = 'Process Cycle Time (s) distribution' 
    text = extract_text(stats_path, ptt_s, ptt_e)

    data = [x.split(',') for x in text.split('\n') if x != '']
    df = pd.DataFrame(data = data[1:], columns=data[0])

    df = df[df['KPI']== 'Process Cycle Time (s)']
    df['Average'] = df['Average'].astype(float).astype(str).apply(lambda x: format(float(x),".2f")).astype(float)
    df['Average'], df['Units'] = zip(*df.apply(lambda x: standarize_metric(x['Average'], x['KPI']), axis=1))
    df['Average'] = df['Average'].round(2)
    df['KPI'] = df.apply(lambda x: x['KPI'].replace(' (s)', ''), axis=1)


    message = '{}: \n'.format(scenario_name)
    message += '\n'.join(df['KPI'] + ': ' + df['Average'].astype(str) + ' ' + df['Units'])
    
    return message

def extract_text(model_path, ptt_s, ptt_e):
    with open(model_path) as file:
        model= file.read()
    lines = model.split('\n')
    start, end = None, None
    for idx, line in enumerate(lines):
        if ptt_s in line and start == None:
            start = idx
        if ptt_e in line and end == None:
            end = idx
        if start != None and end != None:
            break
    return '\n'.join(lines[start+1:end])

def standarize_metric(value, kpi):
    if 'cost' not in kpi.lower():
        if (value <= 60*1.5):
            return value, 'seconds'
        elif (value > 60*1.5) and (value <= 60*60*1.5):
            return value/(60), 'minutes'
        elif (value > 60*60*1.5) and (value <= 60*60*24*1.5):
            return value/(60*60), 'hours'
        elif (value > 60*60*24*1.5) and (value <= 60*60*24*7*1.5):
            return value/(60*60*24), 'days'
        elif (value > 60*60*24*7*1.5):
            return value/(60*60*24*7), 'weeks'
    else:
        return value, ''
    