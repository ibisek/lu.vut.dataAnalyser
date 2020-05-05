
from utils.autodict import autodict

if __name__ == '__main__':

    PATH = '/home/ibisek/wqz/prog/python/lu.vut.dataAnalyser/data/out'
    # IN_FILES = ['2017.csv', '2018.csv', '2019.csv']
    IN_FILES = ['all-combined.csv']
    OUT_FILE = f"{PATH}/results-summarised.csv"

    dd = autodict()

    for inFile in IN_FILES:
        fn = f"{PATH}/{inFile}"

        with open(fn, 'r') as f:

            for line in f.readlines():
                line = line.strip()
                # print('line:', line)

                items = line.split(';')

                filename = items[1].strip()
                function = items[2].strip()
                value = items[3].strip()

                dd[filename][function] = value
                # print(' > ', filename, function, value)

    REQUIRED_KEYS = [
        'FC = fn (SP)',
        'NG = fn (SP)',
        'ITT = fn (SP)',
        'ITT = fn (NG)',

        'FCR = fn (SPR)',
        'NGR = fn (SPR)',
        'ITTR = fn (SPR)',
        'ITTR = fn (NGR)',
    ]

    with open(OUT_FILE, 'w') as f:
        header = "filename;" + ";".join(REQUIRED_KEYS)
        f.write(header)
        f.write('\n')

        for filename in sorted(dd.keys()):

            line = f"{filename};"
            for key in REQUIRED_KEYS:
                val = dd[filename].get(key, '')
                line += f"{val};"

            print('line:', line)
            f.write(line)
            f.write('\n')

    print('KOHEU.')


