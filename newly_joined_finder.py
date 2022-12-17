import pandas as pd
import datetime

old_addr = "Student Manifest Sep 6 1 PM.csv"
new_addr = "Student Manifest Sep 7 1 PM.csv"

with open(old_addr, "r") as t1, open(new_addr, "r") as t2:
    older_version = t1.readlines()
    newer_version = t2.readlines()

now = datetime.date.today().strftime("%b_%d")
with open(f"{now}_diff.csv", "w") as outFile:
    # write the header
    outFile.write(newer_version[0])
    for line in newer_version:
        if line not in older_version:
            outFile.write(line)


# Generate a xlsx version
read_file = pd.read_csv(f"{now}_diff.csv")
read_file.to_excel(f"{now}_diff.xlsx", index=None, header=True)
