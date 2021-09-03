import json
import subprocess

# i am paranoid now so we use absolute path
PROPOSALS_DIR = "/home/celeste/Software/public/nomic/data/proposals"

with open("data/proposals.json") as f:
    proposals = json.load(f)

for index in range(len(proposals) - 1, -1, -1):
    # so that it does not run itself
    if index != 20 and proposals[index] == "passed":
        for _ in range(3):
            subprocess.run(["python3", f"{PROPOSALS_DIR}/{index}.py"])

print("what the fcuk did you do")
