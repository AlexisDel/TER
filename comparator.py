filename = "d4-lactose-H2O2"

f = open(filename + ".ssa", "r")
f_correct = open(filename + "_patrick.ssa", "r")

for line_correct in f_correct.readlines():
    for line in f.readlines():
        if line == line_correct:
            print("OK")
        else:
            print(line)
            print(line_correct)
            print("-------------")
