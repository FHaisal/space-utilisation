import json
from datetime import datetime


def update_json(value):
    with open('./output/log.json', 'r+') as file:
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


def update_csv(value):
    with open(r'./output/log.csv', 'a') as file:
        file.writelines(f'{datetime.now()},{value}\n')
