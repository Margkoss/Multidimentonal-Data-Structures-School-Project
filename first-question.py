from lib.bptree import BPlusTree
from lib.bloomfilter import BloomFilter
from tabulate import tabulate
from time import time

def file_len(fname):
    '''Helper function to get lines in file'''
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def time_to_ms(value):
    '''Helper function to give time formated in miliseconds'''
    return str(round(value * 1000, 4)) + 'ms'

def text_to_color(text, color):
    '''Helper function to add color to text'''
    return f'{color}{text}\033[0m'

usernames_file = 'usernames/usernames.txt'
usernames_not_exist_file = 'usernames/usernames-not-exist.txt'
usernames_lines = file_len(usernames_file)
non_username_lines = file_len(usernames_not_exist_file)

# Usernames
print('\n\nGetting data from:\n',tabulate([
    [text_to_color('Usernames ', '\033[92m'), usernames_file, usernames_lines], 
    [text_to_color('Usernames not existing ', '\033[92m'), usernames_not_exist_file, non_username_lines]
], tablefmt="psql"), '\n\n')

# Declare lists for terminal table
table_headers = [
    text_to_color('Data Structures', '\033[94m'),
    text_to_color('Build Time', '\033[94m'),
    text_to_color('Insert Time(All)', '\033[94m'), 
    text_to_color('True Positives', '\033[94m'),
    text_to_color('False Positives', '\033[94m')
]

bloom_row = [text_to_color('Bloom Filter', '\033[92m')]
bplus_row = [text_to_color('B+ Tree', '\033[92m')]
table_format = 'fancy_grid'

# -------------------------------------------
# Create test bloom filter and test bplustree
# -------------------------------------------
create_start = time()
bloomfilter = BloomFilter(usernames_lines, 0.05)
create_end = time()
bloom_row.append(time_to_ms(create_end-create_start))

create_start = time()
bplustree = BPlusTree(order=15)
create_end = time()
bplus_row.append(time_to_ms(create_end-create_start))


# --------------------------------------------------
# Insert all of the usernames in the data structures
# --------------------------------------------------
with open(usernames_file) as file:
    insert_start = time()
    line = file.readline()
    while line:
        bloomfilter.add(line.rstrip())
        line = file.readline()
    insert_end = time()
bloom_row.append(time_to_ms(insert_end - insert_start))


with open(usernames_file) as file:
    insert_start = time()
    line = file.readline()
    while line:
        bplustree.insert(line.rstrip())
        line = file.readline()
    insert_end = time()
bplus_row.append(time_to_ms(insert_end - insert_start))

# -------------------------
# Check for true positives
# -------------------------
with open(usernames_file) as file:
    positives = 0
    line = file.readline()
    while line:
        exists = bloomfilter.check(line.rstrip())
        if exists:
            positives += 1
        line = file.readline()
bloom_row.append(positives)


with open(usernames_file) as file:
    positives = 0
    line = file.readline()
    while line:
        exists = bplustree.retrieve(line.rstrip())
        if exists:
            positives += 1
        line = file.readline()
bplus_row.append(positives)

# -------------------------
# Check for false positives
# -------------------------
with open(usernames_not_exist_file) as file:
    false_positives = 0
    line = file.readline()
    while line:
        exist = bloomfilter.check(line.rstrip())
        if exist:
            false_positives += 1
        line = file.readline()  
bloom_row.append(false_positives)

with open(usernames_not_exist_file) as file:
    line = file.readline()
    false_positives = 0
    while line:
        exist = bplustree.retrieve(line.rstrip())
        if exist != None:
            false_positives += 1
        line = file.readline()
bplus_row.append(false_positives)




# Print data table
print('Data:')
print(tabulate([bloom_row, bplus_row], headers=table_headers, tablefmt=table_format), '\n\n')

time_dif = str(round(float(bplus_row[2].strip('ms')) - float(bloom_row[2].strip('ms')), 4)) + 'ms'
print(f'Bloom filter is faster by {time_dif} while producing {bloom_row[4]} false postives!', '\n\n')