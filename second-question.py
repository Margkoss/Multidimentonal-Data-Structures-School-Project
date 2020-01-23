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
start_lsh = time.time()
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

with yaspin(Spinners.earth, text="Jaccard similarity(Characteristic matrix)", color="yellow") as spinner:
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
    file.write('Characteristic matrix\n')
    file.write(tabulate(jaccard_table, headers, tablefmt="psql"))


# ----------------
# GENERATE MINHASH
# ----------------
with yaspin(Spinners.earth, text="Minhashing", color="yellow") as spinner:
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

    permutated_rows = []
    for i, shingle in enumerate(table):
        row_to_add = []
        for a, b in zip(coa, cob):
            row_to_add.append((a * i + b)%nextPrime(len(table)))
        permutated_rows.append(row_to_add)

    # Permutaded columns
    permutated_columns = []
    for i in range(0, len(permutated_rows[0])):
        column = []
        for row in permutated_rows:
            column.append(row[i])
        permutated_columns.append(column)
    # Document columns
    document_rows = [doc[1:] for doc in table]
    document_columns = []
    for i in range(0, len(document_rows[0])):
        column = []
        for row in document_rows:
            column.append(row[i])
        document_columns.append(column)

    minhash = []

    for hash_values in permutated_columns:
        found = 0
        min = 0
        minhash_to_add = [-1] * len(document_columns)
        while found < 3:
            for i, hash_value in enumerate(hash_values):
                if hash_value == min:
                    for y, doc in enumerate(document_columns):
                        if doc[i] == 1:
                            if minhash_to_add[y] < 0:
                                minhash_to_add[y] = hash_value
                                found+=1
                            else:
                                continue
            min+=1
        minhash.append(minhash_to_add)

    with open('logs/minhash.log', 'w+') as file:
        file.write(tabulate([doc+["-"]+perm for doc, perm in zip(document_rows, permutated_rows)],
            headers=[f'Doc_{i}' for i, doc in enumerate(document_columns)]+["-"]+[f'Hash{i}' for i, hash_func in enumerate(permutated_columns)],
            tablefmt="psql"))

        file.write(f'\n\n{tabulate(minhash,headers=[f"Doc_{i}" for i, doc in enumerate(document_columns)],tablefmt="psql")}')
    spinner.ok("✅ ")

with yaspin(Spinners.earth, text="Jaccard Similarity(from signature matrix)", color="yellow") as spinner:
    combinations = itertools.combinations(range(len(document_columns)), 2)
    
    similarity_table = []

    for combination in combinations:
        agree = 0

        for minh in minhash:
            if minh[combination[0]] == minh[combination[1]]:
                agree+=1
        
        similarity_table.append([combination, agree/len(minhash)])

    with open('logs/jaccard.log', 'a') as file:
        headers = ["Combination", "Similarity Index"]
        file.write('\nFrom Signature matrix\n')
        file.write(tabulate(similarity_table, headers, tablefmt="psql"))
    
    spinner.ok("✅ ")

# ---
# LSH
# ---
# Split into bands
with yaspin(Spinners.earth, text="LSH", color="yellow") as spinner:
    doc_combinations = itertools.combinations(list(range(len(minhash[0]))), 2)
    bands = []
    for i, hash in enumerate(minhash[::2]):
        bands.append([hash, minhash[i]])

    for combination in doc_combinations:

        agree = 0
        for band in bands:
            for row in band:
                if row[combination[0]] == row[combination[1]]:
                    agree += 1
        if agree >= 2:
            with open('logs/minhash.log', 'a') as file:
                file.write(f'\nDocuments {combination} should be checked\n')
    spinner.ok("✅ ")
finish_lsh = time.time()
print(f'Finished LSH for {len(data)} files in time {(finish_lsh - start_lsh)*1000}ms')

# -----------------
# Cosine Similarity
# -----------------
# Get bag of words
with yaspin(Spinners.earth, text="Cosine Similarity", color="yellow") as spinner:
    cosine_start = time.time()
    bag = []
    for filename in data:
        lines = []
        with open(f'documents/data/{filename}') as file:
            line = file.readline()
            while line:
                lines.append(line)
                line = file.readline()
        bag.append(lines)       

    text = ''
    for doc in bag:
        for line in doc:
            text += line

    text = text.strip('.').split()
    bag = []
    for key in text:
        if not key in bag:
            bag.append(key)

    word_occurances = []
    for filename in data:
        word_dict = {x:0 for x in bag}
        with open(f'documents/data/{filename}') as file:
            line = file.readline()
            while line:
                sentence = line.strip('.').split()
                for word in sentence:
                    if word in word_dict.keys():
                        word_dict[word] += 1
                line = file.readline()
        word_occurances.append(word_dict)

    cosine_table = []
    combinations = itertools.combinations(list(range(len(word_occurances))), 2)
    for combination in combinations:
        enumerator = 0
        denominator = 0

        values_a = list(word_occurances[combination[0]].values())
        values_b = list(word_occurances[combination[1]].values())

        zipped = zip(values_a, values_b)
        
        for a, b in zipped:
            enumerator += a*b
        
        denominator = math.sqrt(sum([k*k for k in values_a])) * math.sqrt(sum([k*k for k in values_b]))
        cosine_table.append([f'Document Combination {combination}']+[enumerator/denominator])
        

    with open('logs/cosine.log', 'w+') as file:
        file.write(tabulate(cosine_table, headers=['Combinations', 'Cosine Similarity Index'], tablefmt="psql"))

    cosine_end = time.time()
    spinner.ok("✅ ")
print(f'Finished Cosine Similarity for {len(data)} files in time {(cosine_end - cosine_start)*1000}ms')