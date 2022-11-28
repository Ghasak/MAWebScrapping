from rich.console import Console
from rich.progress import track
import pandas as pd
console = Console()


import pickle
b1_path = "./database/disclosureProcessedData/parsedConverated/Batch_1/Global_DataFrame_up_to_batch_1.pickle"
def aggreate_articles(batch_path= b1_path):
    with open(batch_path, mode = 'rb') as handle:
        df = pickle.load(handle)
    df.set_index(['symbol', 'timestamp'], inplace = True, drop = False)
    df_symbols_processed = len(df['symbol'].unique())
    return df , df_symbols_processed



def create_full_data_frame():
    dft_list = []
    for batch_num in  track(range(1,37)):
        batch_path = f"./database/disclosureProcessedData/parsedConverated/Batch_{batch_num}/Global_DataFrame_up_to_batch_{batch_num}.pickle"
        df, L = aggreate_articles(batch_path = batch_path)
        dft_list.append(df)
    dfT = pd.concat(dft_list, axis = 'rows')

    with open("./database/disclosureProcessedData/parsedConverated/TOTAL_BATCHES/Global_dataFrame_all_batches.pickle", mode = 'wb') as handle:
        pickle.dump(dfT, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return dfT


def no_articles_in_all_batches():
    no_articles = []
    for batch_num in track(range(1,37)):
        with open(f"./database/disclosureProcessedData/parsedConverated/noArticles_{batch_num}.pickle",  mode = 'rb') as handle:
            L = pickle.load(handle)
            for item in L:
                no_articles.append(item)
    console.log(f"The following symbols has no discolusre information: {(no_articles)} ... ")
    return no_articles


if __name__ == "__main__":
    no_articles_in_all_batches()
    #dfT = create_full_data_frame()
