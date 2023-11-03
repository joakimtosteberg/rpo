import csv
import json

def parse_time(time):
    time = time.split("'")
    return int(time[0])*60 + int(time[1])

def parse_results(results_file):
    teams = {}
    with open(results_file, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            name = f"{row['Fnam']} {row['Nam']}"
            start_no = row['StNo']
            team_name = row['Clb']
            finish = row['Finish']
            start = row['Start']
            runtime = parse_time(row['Runt']) if row['Runt'] else None
            foxes = int(row['Fo'])
            birth = int(row['Birth']) if row['Birth'] else None
            leg = int(row['Grp']) if row['Grp'] != '' else -1
            if leg == -1:
                continue
            if team_name not in teams:
                teams[team_name] = {}
            team = teams[team_name]
            if not leg in team:
                team[leg] = []
            team[leg].append({'name': name,
                              'start_no': start_no,
                              'start': start,
                              'finish': finish,
                              'runtime': runtime,
                              'foxes': foxes,
                              'birth': birth})
        return teams
