import copy

filename = "d4-lactose-H2O2"
f_correct = open(filename + "_patrick.ssa", "r")
f = open(filename + ".ssa", "r")

p_result = len(f_correct.readlines()) - 2
print("Number of reactions (patrick's file) :", p_result)
print("Number of reactions (our file) :", len(f.readlines()) - 2)

f_correct = open(filename + "_patrick.ssa", "r")
counter = 0
for line_correct in f_correct.readlines():
    f = open(filename + ".ssa", "r")
    for line in f.readlines():
        if line == line_correct:
            counter += 1
    f.close()

print("Number of common reactions :", counter - 2)
print("Recouvrement :", float(counter - 2) / float(p_result) * 100, "%")
