import argparse
import csv
import functools
from pathlib import Path

def parse_time(time):
    time = time.split("'")
    return int(time[0])*60 + int(time[1])

def format_time(total_minutes):
    hours = int(total_minutes / (60 * 60))
    minutes = int((total_minutes - (hours * 60 * 60)) / 60)
    seconds = total_minutes - (hours * 60 * 60) - (minutes * 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

class Runner:
    def __init__(self, name, foxes, runtime, included):
        self.name = name
        self.foxes = foxes
        self.runtime = runtime
        self.included = included

    def get_name(self):
        return self.name

    def get_foxes(self):
        return self.foxes

    def get_time(self):
        return format_time(self.runtime)

    def is_included(self):
        return self.included

    def __eq__(self, other):
        return self.name == other.name

class Runners:
    def __init__(self):
        self.runners = list()

    def add_runner(self, runner):
        self.runners.append(runner)

    def __eq__(self, other):
        if len(self.runners) != len(other.runners):
            return False

        for runner in self.runners:
            if not runner in other.runners:
                return False

        return True

    def __iter__(self):
        self.iter_pos = 0
        return self

    def __next__(self):
        if self.iter_pos >= len(self.runners):
            raise StopIteration
        pos = self.iter_pos
        self.iter_pos = self.iter_pos + 1
        return self.runners[pos]

    def __len__(self):
        return len(self.runners)

    def get_names(self):
        names = list()
        for runner in self.runners:
            names.append(runner.get_name())
        return sorted(names)

class TeamResult:
    def __init__(self, foxes, time, runners):
        self.foxes = int(foxes)
        self.time = parse_time(time)
        self.runners = runners

def get_runners(row):
    runners = Runners()
    for i in range(1,4):
        if not row[f"Fnam{i}"]:
            continue

        name = row[f"Fnam{i}"] + " " + row[f"Nam{i}"]
        foxes = int(row[f"Fo{i}"])
        time = parse_time(row[f"Runt{i}"])
        runners.add_runner(Runner(name, foxes, time, i <= 2))
    return runners

@functools.total_ordering
class TeamResults:
    def __init__(self, team_name):
        self.team_name = team_name
        self.competitions = dict()
        self.total_foxes = 0
        self.total_time = 0
        self.runners = set()

    def add_result(self, competition, result):
        if not self.runners:
            self.runners = result.runners
        elif self.runners != result.runners:
            print(f"WARNING: runner mismatch for {self.team_name} at competition {competition}. Got {result.runners.get_names()} but expected {self.runners.get_names()}")

        if competition in self.competitions:
            return
        
        self.competitions[competition] = result.runners
        self.total_foxes += result.foxes
        self.total_time += result.time

    def get_name(self):
        return self.team_name

    def get_foxes(self):
        return self.total_foxes

    def get_time(self):
        return format_time(self.total_time)

    def print(self, place):
        print(f"{place}: {self.team_name} {self.total_foxes} {self.get_time()}")

    def __eq__(self, other):
        return (self.total_foxes == other.total_foxes) and (self.total_time == other.total_time)

    def __lt__(self, other):
        return (self.total_foxes < other.total_foxes) or ((self.total_foxes == other.total_foxes) and (self.total_time < other.total_time))

team_results = dict()

parser = argparse.ArgumentParser()

parser.add_argument('team_results_csv', type=Path, nargs=2)
parser.add_argument('--output', '-o', type=Path)
parser.add_argument('--output_detailed', '-od', type=Path)
args = parser.parse_args()

for competition in range(0,len(args.team_results_csv)):
    with open(args.team_results_csv[competition]) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            team_name = row['Clb']
            if team_name not in team_results:
                team_results[team_name] = TeamResults(team_name)

            team_result = TeamResult(row['totFo'], row['totRun'], get_runners(row))
            team_results[team_name].add_result(competition, team_result)

sorted_results = sorted(team_results.values())

place = 1
html_results = "<table><tr><td></td><td>Team</td><td>Foxes</td><td>Time</td></tr>\n"
html_results_detail = "<table><tr><td></td><td>Team</td><td>Foxes</td><td>Time</td></tr>\n"
results = f"    Team    Foxes   Time\n"
for i in range(0, len(sorted_results)):
    if i>0 and (sorted_results[i] != sorted_results[i-1]):
        place = i+1
    results += f"{place:2}: {sorted_results[i].get_name():7} {sorted_results[i].get_foxes()!s:7} {sorted_results[i].get_time()}\n"
    html_results += f"<tr><td>{place}.</td><td>{sorted_results[i].get_name()}</td><td>{sorted_results[i].get_foxes()}</td><td>{sorted_results[i].get_time()}</td></tr>\n"
    html_results_detail += f"<tr><td>{place}.</td><td>{sorted_results[i].get_name()}</td><td>{sorted_results[i].get_foxes()}</td><td>{sorted_results[i].get_time()}</td></tr>\n"
    for competition, runners in sorted_results[i].competitions.items():
        competition_name = "Natt" if competition == 0 else "Dag"
        html_results_detail += f'<tr><td></td><td style="text-align: center;" colspan="2">{competition_name}</td><td></td></tr>'
        for i,runner in enumerate(runners):
            extra_formatting = ""
            if runner.is_included():
                extra_formatting += "font-weight:bold;"
            html_results_detail += f'<tr style="{extra_formatting}"><td></td><td>{runner.get_name()}</td><td>{runner.get_foxes()}</td><td>{runner.get_time()}</td></td>'
html_results += "</table>"
html_results_detail += "</table>"

print(results, end='')

if args.output:
    args.output.write_text(html_results)

if args.output_detailed:
    args.output_detailed.write_text(html_results_detail)
