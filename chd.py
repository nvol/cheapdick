#!/usr/bin/python3
import urllib.request as ur
import re
import ntpath

def get_price(u):
    print('opening url', u)
    req = ur.urlopen(u)
    h = req.read()
    with open('responses.txt', 'ba') as f:
        f.write(h + b'\n'*5)
    ### <meta itemprop="price" content="45" />
    ### <div class="ordering-mainoffer-price nw"><span class="ordering__value" id="price_9000190983">45</span> руб.</div>
    m = re.search(b'<span class="ordering__value".*>(.*)</span>', h)
    if m:
        return float(m.group(1))

def process_bom(f_n):
    ret = list()
    with open(f_n, 'r') as f:
        while True:
            s = f.readline()
            if not s: break
            s = s.replace('"', '')
            s = s.replace('\n', '')
            sep = s.split(',')
            if len(sep) == 3:
                cost = None
                comp = sep[1]
                value = sep[2]
                try:
                    cnt = int(sep[0])
                except:
                    print('skipping line {%s}' % s)
                    continue # skip this line
                if value == '*':
                    print('skipping:', comp, value, cnt)
                    continue # skip this component
                if comp.startswith('PAD'):
                    print('skipping:', comp, value, cnt)
                    continue # skip this component
                v = urls.get(comp)
                print('>>>', v)
                print('  comp:', comp)
                print(' value:', value)
                print('   cnt:', cnt)
                if type(v) is dict:
                    url = v.get(value)
                else:
                    url = v
                if url:
                    prc = get_price(url)
                    if prc:
                        cost = cnt * prc
                ret.append([comp, value, url, cnt, prc, cost])
    return ret

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


if __name__ == '__main__':
    from urls import urls
    import sys

    try:
        bom = sys.argv[1]
        #csv = path_leaf(bom) + '.csv'
        csv = bom + '.csv'
    except:
        print('Need to specify .bom file')
        exit(1)

    result = process_bom(bom)
    notfound = list()
    print('='*40)
    for i in result:
        print(i)
        if None in i:
            notfound.append(i)
    print('='*40)
    print('Total:', sum([i[-1] for i in result if i[-1]]))
    print('='*40)

    if notfound:
        print()
        print('WARNING!!!!! There are some unsolved dependencies:')
        for i in notfound:
            print('  ', i)

    print()
    print('Writing results to file %s' % csv)
    for i in result: # price and cost: '.' --> ','
        i[-2] = str(i[-2]).replace('.', ',')
        i[-1] = str(i[-1]).replace('.', ',')
    with open(csv, 'w') as f:
        for i in result:
            f.write(';'.join([('"' + str(j) + '"') for j in i]) + '\n')
    print()

