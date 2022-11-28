import pickle
from rich import print as rprint
from rich.console import Console

console = Console()

def checkBatch(batch : int = None):
  '''#Checking Batch Validation\n
    Note:
        This function is used to check the batch and validate if it has all the required fields.
        eacch batch consists of 100 symbols.
    Args:
        batch : int, batch number
    Returns:
        True if batch is valid, False otherwise
        len of the batch which should be 100
  '''
  try:

      with open(f"./database/disclosureProcessedData/parsedConverated/Batch_{batch}/Global_DataFrame_up_to_batch_{batch}.pickle", mode = 'rb') as handle:
          df = pickle.load(handle)
      return len(df['symbol'].unique())

  except FileNotFoundError:
        #console.log(f"Batch [blue]{batch}[reset] is not existed yet[yellow] ... ")
        pass



def noArticlesSymbols(batch : int = None):
    '''#No Articles Symbols\n
        Note: \n
            This function is used to get the symbols which have no articles in the database.
        Args:
            None
        Returns:
            list of symbols which have no articles
    '''
    try:
        with open(f"./database/disclosureProcessedData/parsedConverated/noArticles_{batch}.pickle", mode = 'rb') as handle:
            list_no_articles = pickle.load(handle)
        return list_no_articles
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    # How to run: python -m src.tester.CheckingBatches
    for batch in range(1,37):
        rprint(f"Batch {batch} has {checkBatch(batch)} symbols ...")

    for batch in range(1,37):
        console.log(f"[red]Batch:[magenta]{batch} [reset]=>[blue] {noArticlesSymbols(batch)}[reset] symbols have no articles [yellow]...")
