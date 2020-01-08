import string
import os
import time
import itertools
import math

from random import randrange
from tabulate import tabulate
from yaspin import yaspin
from yaspin.spinners import Spinners

# -----------------
# GENERATE SHINGLES
# -----------------
with yaspin(Spinners.earth, text="Creating Shingles", color="yellow") as spinner:
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
    spinner.ok("✅ ")
    

with open('logs/shingles.log', 'w+') as file:
    file.write(tabulate(table, headers, tablefmt="psql"))

# ---------------------------------
# GENERATE JACCARD SIMILARITY INDEX
# ---------------------------------

with yaspin(Spinners.earth, text="Creating Jaccard similarity", color="yellow") as spinner:
    combinations = itertools.combinations(range(1,len(table[0])), 2)
    headers = ["Combination", "Value"]
    jaccard_table = []


    for combination in combinations:
        type1 = 0
        type2 = 0

        for row in table:
            if row[combination[0]] >= 1 and row[combination[1]] >= 1:
                type1 += 1
            if row[combination[0]] >= 1 and row[combination[1]] == 0 or row[combination[0]] == 0 and row[combination[1]] >= 1:
                type2 += 1
        

        jacard = type1 / (type1 + type2)
        jaccard_table.append([combination, jacard])
    spinner.ok("✅ ")

with open('logs/jaccard.log', 'w+') as file:
    file.write(tabulate(jaccard_table, headers, tablefmt="psql"))


# ----------------
# GENERATE MINHASH
# ----------------
with yaspin(Spinners.earth, text="Creating MinHash", color="yellow") as spinner:
    def generate_coefficients(signature_number, x):
        coefa = []
        coefb = []

        while not len(coefa) == signature_number:
            random_no = randrange(1, x)
            if random_no in coefa or random_no in coefb:
                continue
            else:
                coefa.append(random_no)
        
        while not len(coefb) == signature_number:
            random_no = randrange(1, x)
            if random_no in coefb or random_no in coefa:
                continue
            else:
                coefb.append(random_no)
        
        return coefa, coefb

    def isPrime(n): 
        
        # Corner cases  
        if(n <= 1): 
            return False
        if(n <= 3): 
            return True
        
        # This is checked so that we can skip  
        # middle five numbers in below loop  
        if(n % 2 == 0 or n % 3 == 0): 
            return False
        
        for i in range(5,int(math.sqrt(n) + 1), 6):  
            if(n % i == 0 or n % (i + 2) == 0): 
                return False
        
        return True

    def nextPrime(N): 
    
        # Base case  
        if (N <= 1): 
            return 2
    
        prime = N 
        found = False
    
        # Loop continuously until isPrime returns  
        # True for a number greater than n  
        while(not found): 
            prime = prime + 1
    
            if(isPrime(prime) == True): 
                found = True
    
        return prime

    coa, cob = generate_coefficients(math.floor(math.sqrt(len(table))), len(table))

    headers = ['Row']
    hash_functions_table = []
    for a, b in zip(coa, cob):
        headers.append(f'({a}x + {b})mod{nextPrime(len(table))}')

    for i, row in enumerate(table):
        new_table_row = []
        new_table_row.append(i)
        for a, b in zip(coa, cob):
            new_table_row.append((a*i + b) % nextPrime(len(table)))
        hash_functions_table.append(new_table_row)

    with open('logs/minhash.log', 'w+') as file:
        file.write('\nHash functions used:\n')
        file.write(tabulate(hash_functions_table, headers, tablefmt="psql"))

    # Transform rows into columns
    hashes_columns = []
    for i in range(len(hash_functions_table[0]) - 1):
        column = []
        for hash in hash_functions_table:
            column.append(hash[i+1])
        hashes_columns.append(column)

    docs_columns = []
    for i in range(len(table[0]) - 1):
        column = []
        for doc in table:
            column.append(doc[i+1])
        docs_columns.append(column)

    minhashes = []
    for doc in docs_columns:
        minhash_to_add = []
        for i, hash_function in enumerate(hashes_columns):

            res = sorted(range(len(hash_function)), key = lambda sub: hash_function[sub])[:len(hash_function)]

            for index in res:
                if doc[index] >= 1:
                    minhash_to_add.append(hash_function[index])
                    break
        minhashes.append(minhash_to_add)
    

    with open('logs/minhash.log', 'a') as file:
        file.write('\nMinHash\n')
        file.write(tabulate(minhashes, headers=[f'Minhash {i}' for i in range(1, len(minhashes[0]) + 1)], tablefmt="psql"))

    file_combinations = itertools.combinations(range(1, len(minhashes[0])), 2)
    print(minhashes)
    for comb in file_combinations:
        no = 0
        for one, two in zip(minhashes[comb[0] - 1], minhashes[comb[1] - 1]):
            if one == two:
                no += 1
        print(f'{comb} match in {no} out of 4')
    spinner.ok("✅ ")