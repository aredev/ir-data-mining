import csv


def transformToList(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        your_list = list(reader)

    for column in your_list:
        del column[0]

    your_list = [list(map(int, x)) for x in your_list]

    lyl = len(your_list)

    nl = []

    for x in range(lyl):
        pa = your_list[x][0]
        au = your_list[x][1]

        lnl = len(nl)
        if lnl == 0:
            nl.append([pa, au])

        else:
            ch = False
            for y in range(lnl):
                if nl[y][0] == pa:
                    nl[y].insert(len(nl[y]), au)
                    ch = True

                if ch == True:
                    break

            if ch == False:
                nl.append([pa, au])

    return nl
