import sys
import os, errno
import pickle
from collections import OrderedDict, defaultdict
from rich.console import Console
import inspect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from src.utilities.serverChecker import saveFromPickle, loadFromPickle
import pandas as pd
import numpy as np
import subprocess
import emoji
import time
from datetime import datetime
from src.utilities.webDriver import firFoxDriver
from rich import print as rprint
# Remove pdf Encryptions
import pikepdf
# --------------- import the developed modules -------------
from src.helper.textMiningUnit import pdfTextScrapper
from src.helper.companieStats import  companyDisclosureStats, updateDataFrame, pdfDownloader




# ------------------------------
# 1. Management of the pdf files
# ------------------------------

# You will need to create a directory only once to dump all the company pdf files.


def StoringAndManging(df:pd.DataFrame = None, task: int = None, basepath: str = None, verbose = False):
    '''Storing and managing pdf files\n
        Nonte:
            This function is used to manange the directories for each company \n
            and store the artificats that generated durning the process of getting the pdf document.

    '''
    if basepath is None:
        basepath = "./database/disclosureProcessedData/"
    else:
        basepath = basepath

    # -------------- define your parameters --------------
    console = Console()
    symbolList = df['symbol'].values
    linkDateList = df['linkDateList'].values
    linkTitleList= df['linkTitleList'].values
    articlesLinksList = df['articlesLinksList'].values
    globalArticleIndex = df['globalArticleIndex'].values
    relativeArticleIndex = df['relativeArticleIndex'].values
    pageIndexList = df['pageIndex'].values
    pdfNameList = df['pdfName'].values
    contentList = df['content'].values
    # -------- Pick only one value as it all same for the give company symbol in the df -------
    symbol = symbolList[0]



    # ---------------------------------------------------------
    #                 Create a directory of the given symbol
    # ---------------------------------------------------------
    try:
        process = f"{basepath}parsedConverated/{symbol}"
        subprocess.run("mkdir -p {basepath}parsedConverated/{symbol}".format(basepath=basepath,symbol=symbol), shell=True)
        subprocess.run("chown -R {user}:{group} {basepath}parsedConverated/{symbol}/".format(user=os.getuid(),group=os.getgid(),basepath=basepath,symbol=symbol), shell=True)
        if verbose:
            rprint(emoji.emojize(f"[:file_folder:]{symbol} : {process} : {os.path.exists(process)}", use_aliases=True))
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=process, err=e))


    try:
        # --------------
        # 1. Create a directory and dump the artifacts
        # -------------
        # path = os.path.dirname(os.path.abspath(__file__))
        # basepath = f"{path}/database/disclosureProcessedData/"
        # try:
        #     if verbose:
        #         rprint(emoji.emojize(f"[:file_folder:]{symbol} : {process} : {os.path.exists(process)}", use_aliases=True))
        # except OSError as e:
        #     sys.exit("Can't create {dir}: {err}".format(dir=process, err=e))

        for articlePDFIdex, sublinkPerPageIndex,sublinkPageIndex ,linkDate, linkTitle, pdfName in zip(globalArticleIndex, relativeArticleIndex, pageIndexList, linkDateList, linkTitleList, pdfNameList):

            originals = f"./database/disclosureProcessedData/{pdfName}.pdf"
            destinations = f"./database/disclosureProcessedData/parsedConverated/{symbol}/{pdfName}.pdf"

            subprocess.run("mv {originals} {destinations}".format(originals=originals, destinations=destinations), shell=True)

            # ---- Debugger ------
            if verbose:
                rprint(
                    emoji.emojize(
                        f"[:sparkles:] Moving {pdfName}.pdf to {basepath}{pdfName}.pdf  , with features:: Global n:{articlePDFIdex}, Relative k: {sublinkPerPageIndex} Page p: {sublinkPageIndex} Article Date TS: {linkDate} Article Title: {linkTitle} PDFName: {pdfName}"
                    )
                )
            # ----- Store the dataframe object also ------

        with open(
            f"{basepath}parsedConverated/{symbol}/{symbol}_DataFrame.pickle",
            mode="wb") as handle:
            pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)

    except Exception as e:
        rprint(
            emoji.emojize(
                f"[:no_entry:] Error at Task = {task} Moving and Storing {pdfName}, of symbole = {symbol} see for more details: {e}"
            )

        )
        raise
    # Compress the pdf files for saving space
    # Formula:
    # zip -vr DevOpsBackup20210605.zip ./nvim/* ./coc/* -x "*.DS_Store"
    baseDir = f"{basepath}parsedConverated/{symbol}/*"
    process = f"zip -vr {basepath}parsedConverated/{symbol}/{symbol}_artifact.zip {baseDir} -x '*.pickle'"
    subprocess.run(process, shell=True)
    process = f"rm -rf {basepath}parsedConverated/{symbol}/*.pdf"
    subprocess.run(process, shell=True)


def docManagerTester():
    '''Checking the individual performance of the above function

    '''
    console = Console()
    #url = "https://www.nikkei.com/nkd/company/disclose/?scode=1333&ba=1&hm="
    #url = "https://www.nikkei.com/nkd/company/disclose/?scode=6502&ba=1&hm="
    url = "https://www.nikkei.com/nkd/company/disclose/?scode=1333&ba=1&hm="
    driver = firFoxDriver().engine()
    df = companyDisclosureStats(url = url, verbose = False, driver = driver)
    #console.log(df)
    options = {
        "start_date":'2021/8/1',
        "end_date": '2022/3/1'
        }
    df = updateDataFrame(df, options)
    df = pdfDownloader(df = df, verbose = True, driver = driver)
    df = pdfTextScrapper(df = df, verbose = True )
    StoringAndManging(df = df, verbose = True)
    rprint(df.head())





if __name__ == "__main__":
    docManagerTester()
