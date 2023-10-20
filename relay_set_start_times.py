import argparse
import csv
import datetime
from pathlib import Path
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
        if leg in team:
            print(f"Error: Duplicate runner on leg {leg} for {team_name}")
            sys.exit(1)
        team[leg] = {'start_no': start_no,
                     'start': start,
                     'finish': finish}

for team_name, legs in teams.items():
    for leg in sorted(legs):
        runner = legs[leg]
        if leg+1 not in legs:
            break
        next_runner = legs[leg+1]
        if runner['finish'] != ' 0:00:00' and not next_runner['start']:
            start_times[next_runner['start_no']] = runner['finish']

for start_no, start_time in start_times.items():
    print(f"Start time for runner {start_no} will be set to {start_time}")

if args.kor and start_times:
    with open(args.kor, "a") as f:
        f.write(f"\n@SAVE: {datetime.datetime.now().strftime('%H:%M:%S %d-%m-%y')} VER1908\n")
        f.write("@BEGIN-KOR\n")
        for start_no, start_time in start_times.items():
            f.write(f" 253 {start_no.rjust(2)} {start_time}'00 {datetime.datetime.now().strftime('%d-%m-%y')} 0; #startT\n")
        f.write("@END\n")
