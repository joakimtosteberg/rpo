import argparse
from datetime import datetime, date
from pathlib import Path
import relay

parser = argparse.ArgumentParser()
parser.add_argument('--results', type=Path, required=True)
parser.add_argument('--output', '-o', type=Path)
args = parser.parse_args()

teams = relay.parse_results(args.results)
results = {}

def format_time(total_minutes):
    hours = int(total_minutes / (60 * 60))
    minutes = int((total_minutes - (hours * 60 * 60)) / 60)
    seconds = total_minutes - (hours * 60 * 60) - (minutes * 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_hcp(runner):
    if not runner['birth']:
        return 0
    age = int(date.today().strftime("%Y")) - runner['birth']
    hcp = 0 if age < 50 else int((age - 50) / 2)
    if 'Modig' in runner['name']:
        hcp += 5
    return hcp * 60

for team_name, legs in teams.items():
    results[team_name] = {
        'time': 0,
        'legs': {}
    }

    team_results = results[team_name]['legs']
    for leg in sorted(legs):
        best_finish_datetime = None
        best_runner = None
        for runner in legs[leg]:
            finish_datetime = datetime.strptime(runner['finish'].strip(), "%H:%M:%S")
            if not best_finish_datetime or finish_datetime < best_finish_datetime:
                best_finish_datetime = finish_datetime
                best_runner = runner
            if best_runner:
                hcp = get_hcp(best_runner)
                team_results[leg] = {'name': runner['name'],
                                     'runtime': runner['runtime'],
                                     'runtime_hcp': runner['runtime'] - hcp}
                results[team_name]['time'] += team_results[leg]['runtime_hcp']

sorted_results = sorted(results.items(), key=lambda item:item[1]['time'])
last_time = 0
place = 1
html_results = "<table><tr><td></td><td>Team</td><td>Time</td></tr>\n"
results = f"    Team    Time\n"
for team,result in sorted_results:
    results += f"{place:2}: {team:7} {format_time(result['time'])}\n"
    html_results += f"<tr><td>{place}.</td><td>{team}</td><td>{format_time(result['time'])}</td></tr>\n"
    for leg in sorted(result['legs']):
        runner = result['legs'][leg]
        html_results += f"<tr><td></td><td>{runner['name']}</td><td>{format_time(runner['runtime_hcp'])} ({format_time(runner['runtime'])})</td></tr>\n"

    if result['time'] > last_time:
        place += 1
        last_time = result['time']


html_results += "</table>\n"
print(results, end='')

if args.output:
    args.output.write_text(html_results)
