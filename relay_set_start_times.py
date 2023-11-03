import argparse
import csv
from datetime import datetime
from pathlib import Path
import shutil
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--results', type=Path, required=True)
parser.add_argument('--kor', type=Path)
args = parser.parse_args()

teams = {}
start_times = {}

with open(args.results, 'r') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        start_no = row['StNo']
        team_name = row['Clb']
        finish = row['Finish']
        start = row['Start']
        leg = int(row['Grp']) if row['Grp'] != '' else -1
        if leg == -1:
            continue
        if team_name not in teams:
            teams[team_name] = {}
        team = teams[team_name]
        if not leg in team:
            team[leg] = []
        team[leg].append({'start_no': start_no,
                          'start': start,
                          'finish': finish})

for team_name, legs in teams.items():
    for leg in sorted(legs):
        if leg+1 not in legs:
            break
        best_finish = ''
        finish_datetime = None
        for runner in legs[leg]:
            if runner['finish'] == ' 0:00:00':
                continue
            finish_datetime = datetime.strptime(runner['finish'].strip(), "%H:%M:%S")
            if not best_finish or finish_datetime < best_finish_datetime:
                best_finish = runner['finish']
                best_finish_datetime = finish_datetime
        runner = legs[leg]
        next_runner = legs[leg+1]

        if best_finish:
            for runner in legs[leg+1]:
                if not runner['start']:
                    start_times[runner['start_no']] = best_finish

for start_no, start_time in start_times.items():
    print(f"Start time for runner {start_no} will be set to {start_time}")

if args.kor and start_times:
    shutil.copyfile(args.kor, args.kor.with_suffix(f"{args.kor.suffix}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"))
    with open(args.kor, "a") as f:
        f.write(f"\n@SAVE: {datetime.now().strftime('%H:%M:%S %d-%m-%y')} VER1908\n")
        f.write("@BEGIN-KOR\n")
        for start_no, start_time in start_times.items():
            f.write(f" 253 {start_no.rjust(2)} {start_time}'00 {datetime.now().strftime('%d-%m-%y')} 0; #startT\n")
        f.write("@END\n")
