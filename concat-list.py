

def concat_list(alist):
    newlist = []
    st = False
    last = False
    try:
        for item in alist:
            item = int(item)
            if not st:
                st = item
                last = item
            elif item == last + 1:
                last = item
            else:
                if last == st:
                    newlist.append(str(st))
                elif last == st + 1:
                    newlist.append(str(st))
                    newlist.append(str(last))
                else:
                    rngstr = "{}-{}".format(st, last)
                    newlist.append(rngstr)
                st = item
                last = item

    except ValueError as ve:
        pass

    return newlist


def read_list(url):
    with open(url, 'r') as datain:
        idlist = datain.readlines()

    idlist = [int(l.strip()) for l in idlist]
    return idlist


if __name__ == '__main__':
    url = '../checks/imgcheck-notup-54500-55011.data'
    idlist = read_list(url)
    idlist = concat_list(idlist)
    print(" ".join(idlist))


