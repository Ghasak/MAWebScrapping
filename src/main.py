import os
import sys
import csv
import re
import random
import time
import datetime
import shutil
import emoji  # https://pypi.org/project/emoji/  print(emoji.emojize('Python is :sparkles:'))
from datetime import datetime
import subprocess
import requests
from collections import defaultdict, OrderedDict
import pickle
from requests_html import HTML
from requests_html import HTMLSession
import fire
import numpy as np
import pandas as pd
from rich import print as rprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from typing import List, Dict
# For better logging use console form rich
from rich.console import Console
from src.utilities.serverChecker import server_info
from src.utilities.webDriver import firFoxDriver
from src.utilities.serverChecker import saveFromPickle, loadFromPickle

#WEBDRIVEDIR = os.environ["GOOGLEWEBDRIVEDIR"]
WEBDRIVEDIR = os.environ["FIREFOXWEBDRIVEDIR"]
DATASTORAGEDIR = os.environ["DATASTORAGE"]

console = Console()
console.log(f"Our Driver is located at [red]{WEBDRIVEDIR}", log_locals=False)
console.log(f"storing all the data at {DATASTORAGEDIR}", log_locals=False)

# ----------
from src.helper.companieStats import loadingSymbols
from src.utilities.serverChecker import makeParsedConveratedDir
from src.helper.companieStats import  companyDisclosureStats, updateDataFrame, pdfDownloader
from src.helper.textMiningUnit import pdfTextScrapper
from src.helper.docManager import StoringAndManging
from src.utilities.serverChecker import LoadPreviousWork
# Calcuate the time of execution

start_time = time.time()
# --------------
# 1. [x] Check the updated df if its empty after passing the options
# 2. [x] Collect all pd tables for each company symobl using the df concat method.
# 3. [x] Make the script finish from where it is stopped, this allow for multi-run
# -------------
# ---------------------------------------------------------
#                Create collector directory
#  Note: this will be created only once and if exist will be passed.
# ---------------------------------------------------------
# Create a directory to store for all companies files that will created only once.
# create a new directory if it doesn't exists
# -----------------
# 1. Automate the articles Text Mining:
# -----------------
# create the directory called "parsedConverted" at the ./database/disclosureProcessedData of the project.
makeParsedConveratedDir()

# ---------- Create your webdriver object ----------
console = Console() # for logging
driver = firFoxDriver().engine()  # our firefox dirver
# -----------------
# 1.1. Obtain all the URLS of all the companies in the nikkei
# -----------------
symbolsDict = loadingSymbols()
urlsList = []
symbolsList = []
for key,url in symbolsDict.items():
    symbolsList.append(key)
    urlsList.append(url)

# -----------------
# 1.2. Getting the desriable batch of urls
# -----------------
# to avoide bloating the memory, we will splits all the urls into batches of
# 100 that can be accepted from the user input CLI args.

# -----------------
# 1.3. Obtain the user CLI args.
# -----------------
# Getting the arguments from the CLI
try:
    args: List[str] = sys.argv
    # Getting the batch name
    BATCHVAR = args[1]
    BATCHVAR = str(BATCHVAR)
    # Getting the sequence of the Batch
    startVar = args[1].split("_")[1]
    startVar = int(startVar) -1
    console.log(f"[[green]\uf00c[reset] ] starting at: [blue] {BATCHVAR}")
    console.log(emoji.emojize(f"[[green]\uf00c[reset] ]  Currently running [red]{BATCHVAR} [reset]at [green] {os.getcwd()}"))
    console.log(f"[red] Note [reset] there are in total [blue]{np.round(len(symbolsList)/100)}[reset] batches, each batch is 100 companies in the nikkei website ... ")

    try:
        if not os.path.exists(f"./database/disclosureProcessedData/parsedConverated/{BATCHVAR}"):
            console.log(
                emoji.emojize(
                    f"[[red]\uf482[reset] ] Creating directory for:[green] {BATCHVAR} [reset]at[blue] {os.path.join(os.getcwd(), f'database/disclosureProcessedData/parsedConverated/{BATCHVAR}')}"
                )
            )
            os.mkdir(f"./database/disclosureProcessedData/parsedConverated/{BATCHVAR}")

    except OSError as err:
        console.log(
            emoji.emojize(
                f"[:x:] On BATCH:{BATCHVAR}!! Error occured while creating a host directory for our Batch artifacts ...Check{err}"
            )
        )

except IndexError:
    console.log(emoji.emojize(f"[:x:] Expected 1 arguement as Batch_1,2,..etc., got 0 arguement"))
    raise (SystemExit)






# Storing here companies without updated articles
noArticles = []
# options = {
#     "start_date":'2021/8/1',
#     "end_date": '2022/3/12'
#     }

options = {
    "start_date":'2022/3/13',
    "end_date": '2022/3/22'
    }
# ------------------
# 1.4. Main function of our pipeline
# ------------------

def main(url: str = None, symbol:str = None, options: dict = None, noArticles: list = noArticles, verbose: bool = False, tracer: list = None):
    '''Main Function ...
        Note:\n
        This is the main function for processing a single company symbol
        it includes several task that will:
            - Get each company up-to-date list of all disclosure files
            - Download the files
            - Remove Encryptions if existed.
            - Applying OCR to each file.
            - Convert the pdf to text
            - Parse the text and extract the relevant data
            - Save the data to a pd.DataFrame and other artificats.
    '''
    url = url
    symbol = symbol
    verbose = verbose
    tasks = [f"task {n}" for n in range(1, 6)]
    noArticles = noArticles
    BATCHNUM, idx, chunkSymbols = tracer

    if options is None:
        # --- fetch all the articles (exhaistive historical data) ----
        pass
    else:
        # --------- Get optoinal articles period from the user input ---------
        options = options


    with console.status(f"[bold red] Working on Batch:[reset][[blue]{BATCHNUM}[reset]/[blue]{np.round(len(symbolsList)/100)}[reset]] of Symbol:[magenta]{symbol}[reset] of:[blue]{idx}[reset]/[blue]{len(chunkSymbols)}[reset]...") as status:
        while tasks:

            # --- Task -1-
            task = tasks.pop(0)
            df = companyDisclosureStats(url = url, verbose = verbose, driver = driver)
            console.log(f"[[red]\uf63a[reset] ] Task:[magenta]{task}[reset] is completed, [green]obtain up-to-date each company stats tables[reset] ...")

            # ---- Task -2-
            if options:

                task = tasks.pop(0)
                df = updateDataFrame(df, options)
                if df.empty:
                    console.log(f"[[red]\ufbca[reset] ] [magenta]{symbol}[reset] has not updated articles in this period ... ")
                    noArticles.append(symbol)
                    df = pd.DataFrame([[f'{symbol}']*df.shape[1]],columns=df.columns)
                    return df, noArticles
                else:
                    console.log(f"[[red]\uf63a[reset] ] Task:[magenta]{task}[reset] is completed, [green]dataframe of symbol [red]{symbol}[green] has updated to the user input specified period[reset] ...")

            else:
                # ------ fetch all the articles and skip this task ------
                task = tasks.pop(0)
                console.log(f"[[red]\uf63a[reset] ] Task:[magenta]{task}[reset] is skipped, [green]dataframe will [red] fetch all historical articles[reset] exhustive historical articles in progress ...")

            # ---- Task -3-

            if not df.empty:

                task = tasks.pop(0)
                df = pdfDownloader(df = df, verbose = verbose, driver = driver)
                console.log(f"[[red]\uf63a[reset] ] Task:[magenta]{task}[reset] is completed, [green]Downloading all articles of symbol: {symbol}[reset] ...")

                # ---- Task -4-
                task = tasks.pop(0)
                df = pdfTextScrapper(df = df, verbose = verbose )
                console.log(f"[[red]\uf63a[reset] ] Task:[magenta]{task}[reset] is completed, [green]text scrapping finished of symbol: {symbol}[reset] ...")

                # ---- Task -5-
                task = tasks.pop(0)
                StoringAndManging(df = df, verbose = verbose)
                console.log(f"[[red]\uf63a[reset] ] Task:[magenta]{task}[reset] is completed, [green]storing adn managing is completed of symbol: {symbol}[reset] ...")

            else:
                console.log(f"[[red]\uf63a[reset]] Task:[magenta]{task}[reset] is skipped, [green]dataframe is empty of symbol: {symbol}[reset] ...")

            return df, noArticles



# -----------------
# 2. Automate over symbols in current batch
# -----------------
chunk = 100
chunkCount  = 0
chunkOrder = defaultdict(list)
for i in range(0, len(symbolsList), chunk):
    chunkCount += 1
    #rprint(f"[[green]\uf00c[reset]] Now Running: [blue]{chunkCount}[reset]/[blue]{int(len(symbolsList)/chunk)+1}")
    batchSize = symbolsList[i : i + chunk]
    chunkOrder[f"{chunkCount}"] = batchSize

# -----------------
# 2.1 automate over each chunk, chunk size is 100 symbols
# -----------------
# We get chunkStart and BATCHNUM from the user input
chunkStart = startVar
BATCHNUM = BATCHVAR.split("_")[1]
ROOT_DIR = os.getcwd()
basepath = os.path.join(ROOT_DIR, "database/disclosureProcessedData/")
processedDatapath = os.path.join(basepath, "parsedConverated")
console.log(f" basepath: {basepath}")
console.log(f"processedDatapath: {processedDatapath}")

# --------------------
# 2.2 Aggregation container:
# --------------------
# We aggregate the dataframe of each symbol in the list, which will be later
# converated to full pd.DataFrame.
pdTotalList = []

# --------------------
# 3. Articles Engine:
# --------------------
for batch, chunkSymbols in list(chunkOrder.items())[chunkStart:chunkStart+1]:
    rprint(
        emoji.emojize(
            f"[[red]\uf1c0[reset] ] Now Running Chunk: [blue]{batch}[reset]/[blue]{len(chunkOrder.keys())}"
        )
    )
    # ------- Start from last stopped location -----
    finishedSymbols = os.listdir(f"{processedDatapath}")
    if ".DS_Store" in finishedSymbols:
        finishedSymbols.remove(".DS_Store")
    if f"Batch_{BATCHNUM}" in finishedSymbols:
        finishedSymbols.remove(f"Batch_{BATCHNUM}")

    # ----------------------------------------------------------------
    # 3.1 Check if the saving document directory has symbol directories.
    # ----------------------------------------------------------------
    if bool(finishedSymbols):
        # --- Deserlize the processed dataframe if exists ---
        # ---------------------
        # 3.1.1 Deserialize the previous work in form of a dataframe
        # ---------------------
        dfTotalBatch, previousWorkExistedBool = LoadPreviousWork(BATCHNUM = BATCHNUM, chunkSymbols = chunkSymbols)
        if previousWorkExistedBool and (len(dfTotalBatch) != 0): # if the previous work existed and returned dataframe is not empty
            pdTotalList = [dfTotalBatch] # append the dataframe to the list of dataframes.
        else:
            pdTotalList = pdTotalList # otherwise get the aggregation container from zero

        # ---------------------
        # 3.3.2. Loop over all symobls of current batch.
        # ---------------------
        for idx, symbol in enumerate(chunkSymbols,1):
            tracer = [BATCHNUM, idx, chunkSymbols]
            url = symbolsDict[symbol]
            if symbol in finishedSymbols:
            # ------------------------------------------------------------
            # 3.3.3 skip if you already processed the symbol
            # ------------------------------------------------------------
                console.log(f"[[green]\uf6b9[reset] ] [green]{symbol}[reset] has already been processed ... ")
                # Go fetch another symobl.
                continue

            elif symbol not in finishedSymbols:
            # ------------------------------------------------------------
            # 3.3.4 process the one that has not been processed.
            # ------------------------------------------------------------
                console.log(f"[[red]\uf6b8[reset] ] [magenta]{symbol}[reset] on the waiting list to be processed ... ")
                # --- ensure that you don't have any pdf article from prevous symbol ----

                process = f"rm -rf {basepath}/*.pdf"
                subprocess.run(process,shell = True)

                # ------------------------------------------------------------
                # 3.3.5 Main task pipeline for data processing (check main function)
                # ------------------------------------------------------------
                dfSymbol,noArticles = main(url = url , symbol = symbol, options = options, tracer = tracer)

                if not dfSymbol.empty: # if the dataframe of current symbol is not empty
                    pdTotalList.append(dfSymbol) # append to our aggregation container
                    dfTotal = pd.concat(pdTotalList, axis = 'rows') # concat the dataframe of the aggregation container,
                    with open(f"{processedDatapath}/Batch_{BATCHNUM}/Global_DataFrame_up_to_batch_{BATCHNUM}.pickle", "wb") as handle:
                        pickle.dump(dfTotal, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # ----------
        # 3.3.6 Show all companies that not have articles within the specified period.
        # ----------
        console.log(f"[[red]\ufbca[reset]] No articles available in the period: {options} to the following companies ...\n [blue] {noArticles}")

    # ----------------------------------------------------------------
    # 3.2 This section for first time we start the script., fresh start, and no symobls (i.e.,symbol directories) have been processed.
    # ----------------------------------------------------------------
    elif not bool(finishedSymbols):
        console.log("[[red]\uf6b7[reset] ] Fresh Start [[magenta]first time to run[reset]] ...")

        for idx, symbol in enumerate(chunkSymbols,1):
            tracer = [BATCHNUM, idx, chunkSymbols]
            url = symbolsDict[symbol]

            # ------------------------------------------------------------
            # 3.2.1 Automate over all symbols in the current batch.
            # ------------------------------------------------------------
            console.log(f"[[red]\uf6b8[reset] ] [magenta]{symbol}[reset] on the waiting list to be processed ... ")

            process = f"rm -rf {basepath}/*.pdf"
            subprocess.run(process,shell = True)

            dfSymbol,noArticles = main(url = url , symbol = symbol, options = options, tracer = tracer)

            if not dfSymbol.empty:
                pdTotalList.append(dfSymbol)
                dfTotal = pd.concat(pdTotalList, axis = 'rows')
                with open(f"{processedDatapath}/Batch_{BATCHNUM}/Global_DataFrame_up_to_batch_{BATCHNUM}.pickle", "wb") as handle:
                    pickle.dump(dfTotal, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # Show all companies that not have articles within the specified period.
        console.log(f"[[red]\ufbca[reset]] No articles available in the period: {options} to the following companies ...\n [blue] {noArticles}")

# ----------------------------------------------------------------
# 4.             Save the symbols that has no articles
# ----------------------------------------------------------------
saveFromPickle(f"{processedDatapath}/noArticles_{BATCHNUM}.pickle", noArticles)



# -------
# 4.1 Shutdown the webdirver
# Action performed :
# - close() method closes the current window.
# - quit() method quits the driver instance, closing every associated window, which is opened.
# -------
driver.quit()

# -------
# 4.2 Calcuate the time taken to run the script
# -------

end_time = time.time()
execution_time = end_time - start_time
rprint(
    emoji.emojize(
        f'[:alarm_clock:] Task Exectution Time[:mega:]: {time.strftime("%H hour(s):%M min(s):%S sec(s)",time.gmtime(execution_time))}'
    )
)
