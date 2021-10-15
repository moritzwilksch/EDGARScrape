import random
import copy
## check score
import re
import subprocess

pattern = re.compile(r'failed to identify (\d+) problems')

def run_and_get_score():
    result = subprocess.run(['./run_all.sh'], stdout=subprocess.PIPE)
    test_output = result.stdout.decode('utf-8')
    return int(pattern.findall(test_output)[0])

def write(strings, file):
    with open(file, 'w') as f:
        for line in strings:
            f.write(line)

def read(file):
    out=[]
    with open(file) as f:
        for line in f:
            out.append(line)

    return out

def trim():
    input = read("tests.txt")
    while len(input) > 50:
        temp_test = random.choices(input, k=len(input) - 8)
        print(len(temp_test))
        write(temp_test, "tests.txt")
        newscore = run_and_get_score()
        if newscore == 0:
            input = copy.deepcopy(temp_test)
            print(len(input))
