import sys
import os
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
from src.helper.companieStats import  companyDisclosureStats, updateDataFrame, pdfDownloader
#---------- for text mining from pdfs ------
import os
from tika import parser

def pdfTextScrapper(df: pd.DataFrame,task: int = None, basepath: str = None,verbose = False):

    console = Console()
    symbolList = df['symbol'].values
    linkDateList = df['linkDateList'].values
    linkTitleList= df['linkTitleList'].values
    articlesLinksList = df['articlesLinksList'].values
    globalArticleIndex = df['globalArticleIndex'].values
    relativeArticleIndex = df['relativeArticleIndex'].values
    pageIndexList = df['pageIndex'].values
    pdfNameList = df['pdfName'].values
    contentList = []

    if basepath is None:
        basepath = "./database/disclosureProcessedData/"
    else:
        basepath = basepath


    try:
        # --------------
        # 1. prepare the document to be scrapped
        # -------------

        for symbol,articlePDFIdex, sublinkPerPageIndex,sublinkPageIndex ,linkDate, linkTitle, pdfName in zip(symbolList,globalArticleIndex, relativeArticleIndex, pageIndexList, linkDateList, linkTitleList, pdfNameList):

            # ---- Debugger ------
            if verbose:
                rprint(
                    emoji.emojize(
                        f"[:o:]Global n:{articlePDFIdex}, Relative k: {sublinkPerPageIndex} Page p: {sublinkPageIndex} Article Date TS: {linkDate} Article Title: {linkTitle} PDF Name: {pdfName}"
                    )
                )

            # ---- Getting the content -------
            # - Subtask A - remove the encryptions
            try:
                if verbose:
                    rprint(
                        emoji.emojize(
                            f"[:sparkles:][{articlePDFIdex}/{len(globalArticleIndex)}] subtask(A) Removing Encryption of {pdfName}, symbol: {symbol}, article num: {sublinkPerPageIndex} at article-page: {sublinkPerPageIndex}/{sublinkPageIndex}, with features, date: {linkDate}, title: {linkTitle}"
                        )
                    )

                pdf_RemovedEncyrption = pikepdf.open(
                    f"{basepath}{pdfName}.pdf",
                    allow_overwriting_input=True,
                )
                pdf_RemovedEncyrption.save(f"{basepath}{pdfName}.pdf")

            except Exception as e:
                rprint(
                    emoji.emojize(
                        f"[:heavy_exclamation_mark:] Error occured at subtask(A) Removing Encription of {pdfName}, symbol: {symbol}, article num: {articlePDFIdex} at article-page: {sublinkPerPageIndex}/{sublinkPageIndex}, with features, date: {linkDate}, title: {linkTitle}"
                    )
                )
                raise
            # - Subtask B - Applying OCR to the pdf and allow it to be scrapable.

            try:
                if verbose:
                    rprint(
                        emoji.emojize(
                            f"[:sparkles:][{articlePDFIdex}/{len(globalArticleIndex)}] subtask(B) Applying OCR to {pdfName}, symbol: {symbol}, article num: {articlePDFIdex} at article-page: {sublinkPerPageIndex}/{sublinkPageIndex}, with features, date: {linkDate}, title: {linkTitle}"
                        )
                    )

                process = f"ocrmypdf -l jpn --jobs 4 {basepath}{pdfName}.pdf {basepath}{pdfName}.pdf --output-type pdf"
                content = subprocess.run(process, shell=True, capture_output=True)

            except Exception as e:
                rprint(
                    emoji.emojize(
                        f"[:heavy_exclamation_mark:] Error occured at subtask(B) Applying OCR to {pdfName}, symbol: {symbol}, article num: {articlePDFIdex} at article-page: {sublinkPerPageIndex}/{sublinkPageIndex}, with features, date: {linkDate}, title: {linkTitle}"
                    )
                )
                raise

            # - Subtask C - Scraping the content

            try:
                if verbose:
                    rprint(
                        emoji.emojize(
                            f"[:sparkles:][{articlePDFIdex}/{len(globalArticleIndex)}] subtask(C) Text Scrapping of {pdfName}, symbol: {symbol}, article num: {articlePDFIdex} at article-page: {sublinkPerPageIndex}/{sublinkPageIndex}, with features, date: {linkDate}, title: {linkTitle}"
                        )
                    )
                # import parser object from tike

                #path =  os.path.join(os.getcwd(), 'src/tester/Firm_3612_n4_k4_p1_TS_2022_03_15_00_53_53.pdf')
                # opening pdf file
                parsed_pdf = parser.from_file(f"{basepath}{pdfName}.pdf")

                # saving content of pdf
                # you can also bring text only, by parsed_pdf['text']
                # parsed_pdf['content'] returns string
                content = parsed_pdf['content']

                # Printing of content
                #print(data)
                # <class 'str'>
                #print(type(data))
                # ------ Slow and stuck sometimes. ---------- got replaced with Tika
                #process = f"pdf2txt.py {basepath}{pdfName}.pdf"
                #content = subprocess.run(process, shell=True, capture_output=True)
                #content = content.stdout.decode("utf8")

            except Exception as e:
                rprint(
                    emoji.emojize(
                        f"[:heavy_exclamation_mark:] Error occured at subtask(C) Text Scrapping of {pdfName}, symbol: {symbol}, article num: {articlePDFIdex} at article-page: {sublinkPerPageIndex}/{sublinkPageIndex}, with features, date: {linkDate}, title: {linkTitle}"
                    )
                )
                raise
            # check if the content is available otherwise record 0 in the content list
            if content is None:
                content = "0"
                contentList.append(content)
            else:
                contentList.append(content)

        df['content'] = contentList

        return df

    except Exception as e:
        rprint(
            emoji.emojize(
                f"[:no_entry:] Error at Task = {task} pdf scrapping symbole = {symbol} see for more details: {e}"
            ))
        raise






if __name__ == "__main__":
    pass
