import argparse
import csv
from datetime import datetime, date
from operator import itemgetter
from pathlib import Path

def parse_time(time):
    time = time.split("'")
    return int(time[0])*60 + int(time[1])

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

def parse_results(results_file):
    with open(results_file, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        results = []
        for row in reader:
            name = f"{row['Fnam']} {row['Nam']}"
            runtime = parse_time(row['Runt']) if row['Runt'] else None
            foxes = int(row['Fo'])
            birth = int(row['Birth']) if row['Birth'] else None
            results.append({'name': name,
                            'runtime': runtime,
                            'foxes': foxes,
                            'birth': birth})
        return results


parser = argparse.ArgumentParser()
parser.add_argument('--results', type=Path, required=True)
parser.add_argument('--output', '-o', type=Path)
args = parser.parse_args()

results = parse_results(args.results)

for result in results:
    result['runtime_hcp'] = result['runtime'] - get_hcp(result)


sorted_results = sorted(sorted(results, key=itemgetter('runtime_hcp')), key=itemgetter('foxes'), reverse=True)
last_time = 0
place = 1
html_results = "<table><tr><td></td><td>Name</td><td>Foxes</td><td>Time</td></tr>\n"
results = "    Name                           Foxes   Time\n"
for result in sorted_results:
    results += f"{place:2}: {result['name']:30} {result['foxes']!s:7} {format_time(result['runtime_hcp'])}\n"
    html_results += f"<tr><td>{place}.</td><td>{result['name']}</td><td>{result['foxes']}</td><td>{format_time(result['runtime_hcp'])} ({format_time(result['runtime'])})</td></tr>\n"

    if result['runtime_hcp'] > last_time:
        place += 1
        last_time = result['runtime_hcp']


html_results += "</table>\n"
print(results, end='')

if args.output:
    args.output.write_text(html_results)
