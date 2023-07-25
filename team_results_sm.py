import argparse
import csv
import functools
from pathlib import Path

class TeamResult:
    def __init__(self, foxes, time, nam1, fnam1, nam2, fnam2, nam3, fnam3):
        self.foxes = int(foxes)
        time = time.split("'")
        self.time = int(time[0])*60 + int(time[1])
        self.runners = set()
        if nam1 or fnam1:
            self.runners.add(f"{fnam1} {nam1}")
        if nam2 or fnam2:
            self.runners.add(f"{fnam2} {nam2}")
        if nam3 or fnam3:
            self.runners.add(f"{fnam3} {nam3}")

@functools.total_ordering
class TeamResults:
    def __init__(self, team_name):
        self.team_name = team_name
        self.competitions = list()
        self.total_foxes = 0
        self.total_time = 0
        self.runners = set()

    def add_result(self, competition, result):
        if not self.runners:
            self.runners = result.runners
        elif self.runners != result.runners:
            print(f"WARNING: runner mismatch for {self.team_name} at competition {competition}. Got {result.runners} but expected {self.runners}")

        if competition in self.competitions:
            return
        
        self.competitions.append(competition)
        self.total_foxes += result.foxes
        self.total_time += result.time

    def get_name(self):
        return self.team_name

    def get_foxes(self):
        return self.total_foxes

    def get_time(self):
        hours = int(self.total_time / (60 * 60))
        minutes = int((self.total_time - (hours * 60 * 60)) / 60)
        seconds = self.total_time - (hours * 60 * 60) - (minutes * 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

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
args = parser.parse_args()

for competition in range(0,len(args.team_results_csv)):
    with open(args.team_results_csv[competition]) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            team_name = row['Clb']
            if team_name not in team_results:
                team_results[team_name] = TeamResults(team_name)

            team_results[team_name].add_result(competition, TeamResult(row['totFo'], row['totRun'], row['Nam1'], row['Fnam1'], row['Nam2'], row['Fnam2'], row['Nam3'], row['Fnam3']))

sorted_results = sorted(team_results.values())

place = 1
results = f"    Team    Foxes   Time\n"
for i in range(0, len(sorted_results)):
    if i>0 and (sorted_results[i] != sorted_results[i-1]):
        place = i+1
    results += f"{place:2}: {sorted_results[i].get_name():7} {sorted_results[i].get_foxes()!s:7} {sorted_results[i].get_time()}\n"

if args.output:
    args.output.write_text(results)
else:
    print(results, end='')
