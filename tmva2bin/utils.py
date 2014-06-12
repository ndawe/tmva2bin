
def readline(file, cont=None):
    line = file.readline()
    if cont != None:
        while line.strip().endswith(cont):
            line = " ".join([line.strip()[:-1 * len(cont)], file.readline()])
    return line


def readlines(file, cont=None):
    lines = []
    line = readline(file, cont)
    while line != '':
        lines.append(line)
        line = readline(file, cont)
    return lines
