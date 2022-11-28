import os
import sys
import pickle
# For better logging use console form rich
from rich.console import Console
from rich import print as rprint
import emoji
import requests
import subprocess
console = Console()
#from src.helper.companieStats import loadingSymbols
from collections import defaultdict
import pandas as pd


def server_info(url):
    '''You will need rich library to allow the console.log works...'''
    r= requests.get(url)
    console.log(f"Current Status: {r.status_code}, {r.ok}", log_locals=False)
    for index, (key, val) in enumerate(r.headers.items()):
        console.log(f"->{index:>3} => : {key}::{val}", log_locals=False)



def loadFromPickle(pickleDir):
    '''Load from pickle\n
        input `str`: the direcotry in which your pickle object is located\n

    '''
    with open(pickleDir, mode = "rb") as handle:
        return pickle.load(handle)

def saveFromPickle(pickleDir, objectFile):
    '''Save from pickle\n
        input `str`: the direcotry in which your pickle object is stored\n
        oputput `object`: the object you want to saved
    '''
    with open(pickleDir, mode = "wb") as handle:
        pickle.dump(objectFile, handle, protocol=pickle.HIGHEST_PROTOCOL)



def makeParsedConveratedDir(basePath: str = None, verbose = True):
    '''
    ### Create collector directory\n
    **Note**: this will be created only once and if exist will be passed.\n
    Create a directory to store for all companies files that will created only once.\n
    create a new directory if it doesn't exists\n
    '''
    # if basePath is None:
    #     basepath = "/database/disclosureProcessedData/"
    # else:
    #     basepath
    verbosePlus = False

    try:
        if verbosePlus:
            # This will give us the directory of the serverChecker.py file
            path = os.path.dirname(os.path.abspath(__file__))
            rprint(path)
            # this will give us up to src/
            base_path = os.path.dirname(path)
            rprint(base_path)
        ROOT_DIR = os.getcwd()
        # this also can replace the getcwd()
        #ROOT_DIR = os.path.dirname(os.path.abspath("requirements.txt"))
        # Please be aware to not use(/) in the join method of the beginning of the second path string.
        basepath = os.path.join(ROOT_DIR,"database/disclosureProcessedData/")
        checking_path = os.path.join(ROOT_DIR, "database/disclosureProcessedData/parsedConverated/")
        if not os.path.exists(checking_path):
            process = f"{basepath}parsedConverated"
            subprocess.run("mkdir -p {basepath}parsedConverated/".format(basepath=basepath), shell=True)
            subprocess.run("chown -R {user}:{group} {basepath}parsedConverated".format(user=os.getuid(),group=os.getgid(),basepath=basepath), shell=True)

            if verbose:
                rprint(f"Root directory of this project: {ROOT_DIR}")
                rprint(f"basepath which we store our pdf files and other artificats: {basepath}")
                rprint(f"checking_path:{checking_path}")
                rprint(emoji.emojize(f"[ :file_cabinet:   ] {process}: Status: {os.path.exists(process)}", use_aliases=True))
    except OSError as e:
        sys.exit("Can't create {dir}: {err}".format(dir=process, err=e))



def LoadPreviousWork(BATCHNUM: str = None, chunkSymbols: list = None):
    '''Load Previous work
        Note:\n
        this function is used to scan and check all the symbols that are processed already for a given batch
        assume you already have loaded the function loadingSymbols.

    '''
    try:
        # All processed symbols so far for all batches.
        console = Console()
        dfTotalBatchList = []
        previousWorkExistedBool = False
        rawList = os.listdir("./database/disclosureProcessedData/parsedConverated")
        symbolsList = chunkSymbols
        # Assume you are at the root directory of this project.
        # Intersect the processed symbols of current batch with the all the processed symbols.
        L = list(filter(lambda x:x in rawList, symbolsList))
        if len(L) != 0:
            previousWorkExistedBool = True

        for symbol in symbolsList:
            if os.path.exists(f"./database/disclosureProcessedData/parsedConverated/{symbol}"):
                with open(f"./database/disclosureProcessedData/parsedConverated/{symbol}/{symbol}_DataFrame.pickle", mode = 'rb') as handle:
                    df = pickle.load(handle)
                dfTotalBatchList.append(df)
        if previousWorkExistedBool:
            dfTotalBatch = pd.concat(dfTotalBatchList, axis = 'rows')
            console.log(f"[[magenta]\uf12a[reset]] Percentage of processed data for Batch:[blue]{BATCHNUM}[reset], so far: [blue]{len(L)/len(symbolsList) * 100}[reset] %, rest symbols will be process momentarily ... ")
        else:
            console.log(f"[[magenta]\uf12a[reset]] No perviouse processed data for Batch:[blue]{BATCHNUM}[reset], so far: [blue]{0}[reset] %, reset will be process momentarily.")
            dfTotalBatch = pd.DataFrame()

    except Exception as e:
        rprint(e)
        raise
    return dfTotalBatch, previousWorkExistedBool
