with open('../documents/dracula1.txt') as f1:
    for i in range(0, 4):
        filename = f'../documents/data/file{i}.txt'

        with open(filename, 'w+') as f2:
            for y in range(i*100, i*100+100):
                line = f1.readline()
                f2.write(line)
 
print("all done")