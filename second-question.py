import string
import os
import time

from tabulate import tabulate
from yaspin import yaspin
from yaspin.spinners import Spinners

with yaspin(Spinners.earth, text="Creating Shingles", color="yellow") as spinner:
    time.sleep(2)

    text = []
    shingles = []

    file_dir = 'documents/data/'
    data = os.listdir(file_dir)
    data.sort()

    headers = ["Shingles"]

    for filename in data:
        headers.append(filename)

        with open(file_dir + filename) as file:
            new_line = file.readline()
            line = new_line

            while new_line:
                new_line = file.readline()
                line += new_line

            table = str.maketrans(dict.fromkeys(string.punctuation))
            new_string = line.translate(table)
            text.append(new_string.lower().replace("\n", " "))

    for line in text:
        words = line.split()

        for i in range(len(words) - 2):
            if f'{words[i]} {words[i+1]} {words[i+2]}' in shingles:
                continue
            else:
                shingles.append(f'{words[i]} {words[i+1]} {words[i+2]}')

    table = []

    for shingle in shingles:
        
        table_row = []
        table_row.append(shingle)
        
        for i, filename in enumerate(data):
            cnt = text[i].count(shingle)
            table_row.append(cnt)

        table.append(table_row)
    
    table = tabulate(table, headers, tablefmt="psql")

with open('logs/shingles.log', 'w+') as file:
    file.write(table)
