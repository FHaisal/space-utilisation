import json
from datetime import datetime
import os


def update_json(value, location=None):
    dir_path = os.path.expanduser('~/Desktop')
    if location:
        dir_path = os.path.dirname(os.path.realpath(location))

    if not os.path.isfile(f'{dir_path}/people_counter_log.json'):
        with open(f'{dir_path}/people_counter_log.json', 'w') as file:
            json.dump({"total_entered": 0, "total_exited": 0, "date_log": []}, file)
        file.close()

    with open(f'{dir_path}/people_counter_log.json', 'r+') as file:
        data = json.load(file)

        if value == 'entered':
            data['total_entered'] += 1
        elif value == 'exited':
            data['total_exited'] += 1

        data['date_log'].append({
            'type': value,
            'date': str(datetime.now())
        })

        file.truncate(0)
        file.seek(0)
        json.dump(data, file)

    file.close()


def update_csv(value, location=None):
    dir_path = os.path.expanduser('~/Desktop')
    if location:
        dir_path = os.path.dirname(os.path.realpath(location))

    if not os.path.isfile(f'{dir_path}/people_counter_log.csv'):
        with open(f'{dir_path}/people_counter_log.csv', 'w') as file:
            file.writelines('date,type\n')
        file.close()

    with open(f'{dir_path}/people_counter_log.csv', 'a') as file:
        file.writelines(f'{datetime.now()},{value}\n')

    file.close()
