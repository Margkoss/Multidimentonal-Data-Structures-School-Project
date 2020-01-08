with open('../documents/dracula1.txt') as f1:
    for i in range(0, 30):
        filename = f'../documents/data/file{i}.txt'

        with open(filename, 'w+') as f2:
            for y in range(i*10, i*10+10):
                line = f1.readline()
                f2.write(line)
 
print("all done")