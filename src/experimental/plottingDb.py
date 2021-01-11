"""
A script plotting regression results from DB.

@see https://www.datacamp.com/community/tutorials/moving-averages-in-pandas
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from dao.regressionResultDao import listFunctionsForEngine, getValues

if __name__ == '__main__':

    ENGINE_ID = 1

    functions = listFunctionsForEngine(ENGINE_ID)
    print("Available functions:", functions)

    for fn in functions:

        items = fn.split('-')
        title = f"{items[0]} = fn ( {items[2]} )"

        df = getValues(ENGINE_ID, fn)

        df['ma20'] = df['delta'].rolling(window=20).mean()
        df['ma40'] = df['delta'].rolling(window=40).mean()
        df['ema5'] = df['delta'].expanding(min_periods=5).mean()

        plt.close('all')

        ax = df[['delta', 'ma20', 'ma40', 'ema5']].plot(figsize=(20, 8), marker='+', markersize=4, ls='None')

        plt.subplots_adjust(left=0.05, right=0.98, top=0.94, bottom=0.13)

        ax.legend(fontsize=14, loc='lower right')
        # ax.get_legend().remove()

        plt.title(title, fontsize=20)

        plt.xlabel('sample index', fontsize=14)
        # plt.xlabel(None)

        plt.ylabel('value delta', fontsize=14)
        # ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        # ax.xaxis.set_minor_formatter(mdates.DateFormatter("%Y-%m-%d"))
        # axes.set_xlim([xmin, xmax])
        # ax.set_ylim([90, 100])    # NG 90-100
        plt.xticks(rotation=90)
        # plt.show()

        fn = f"/tmp/00/engineId-{ENGINE_ID}-{fn}.png"
        plt.savefig(fn, dpi=300)
        print(f"[INFO] File {fn} saved.")

    print("KOHEU.")



