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
from src.utilities.serverChecker import loadFromPickle, saveFromPickle
import pandas as pd
import numpy as np
import emoji
import time
from datetime import datetime
from src.utilities.webDriver import firFoxDriver
from rich import print as rprint

def mainPageIndex_mainLinks(driver):
    """How many links at the given webpage, using last visited website\n
    Input:\n
        - Uses the (driver) selenium object at given visited webpage.\n
    output:\n
        - Return a list of all the given links at the current webpage.\n
            expected one of `css selector`, `link text`, `partial link text`, `tag name`, `xpath`\n

    """
    console = Console()
    kList = []
    try:
        linkIndexClassName = "pageIndexNum "
        linkIndexNum = driver.find_elements_by_class_name(linkIndexClassName)
            # Subpages links
        for idx, link in enumerate(linkIndexNum):
            for l in link.find_elements(by="tag name", value="a"):
                kList.append(l.get_attribute("href"))
        return len(linkIndexNum), kList
    except Exception as e:
        console.log(f"[red]\u26a0[reset] [yellow] Error occurred at {str(str(inspect.currentframe())).split(' ')[-1][:-1]} function check here:[reset] {e}", log_locals=False)

# This will give us all links for a given symble at given page
#//*[@id="CONTENTS_MAIN"]/div[6]/div/div[2]/table/tbody
# This will give us the index of how many subpages
#//*[@id="CONTENTS_MAIN"]/div[6]/div/div[2]/div[1]/div/ul/li[3]

def loadingSymbols():
    '''This will load a previous pickl
        Note:
            Pickle data has been stored at
            ./database/artifacts/companiesSymbols/allValidCompaniesCorrected.pickle \n
            Assume you run the code from project root directory (where src is) \n
            e.g.,\n
                python src/helper/companieStats.py\n
                python src/main.py\n
            or using modules\n
                python -m src.helper.companieStats\n
                python -m src.main\n
    '''
    console = Console()
    with open("./database/artifacts/companiesSymbols/allValidCompaniesCorrected.pickle", mode = 'rb') as handle:
        symbolsPickle = pickle.load(handle)
        # Getting all the elements in more nice shape to autoamte symbol by symbol
    companyDisclosure = OrderedDict()
    for index, P0 in enumerate(list(symbolsPickle.items())):
        symbol = P0[0]
        mainPage = P0[1][0][0]
        companyDisclosure[f"{symbol}"] = mainPage
    return companyDisclosure



def companiesSymboleLinks():
    driver = firFoxDriver().engine()
    companySLandingPageDict = loadingSymbols()
    final_output = OrderedDict()
    for symbol, mainPage in tqdm(companySLandingPageDict.items()):
        driver.get(mainPage)
        subPageIndex, subPagesList = mainPageIndex_mainLinks(driver= driver)
        mainAndSubPageList = [mainPage]
        for item in subPagesList:
            mainAndSubPageList.append(item)
        final_output[f"{symbol}"] = [subPageIndex, mainAndSubPageList]
    driver.quit()
    return final_output

def showMaxSubPageCompanies():
    console = Console()
    d = loadFromPickle("./database/artifacts/companiesSymbols/companieslinksSubLinksDict.pickle")
    linkPages = defaultdict()
    for idx, (key,val) in enumerate(d.items()):
        linkPages[f"{key}"] = int(val[0])
    console.log(max(linkPages.items(), key = lambda k : k[1]))
    console.log(dict(sorted(linkPages.items(), key=lambda item: item[1])))



# ----------------------------------------------------------------
#                        Help function
#
# ----------------------------------------------------------------

def companyDisclosureStats(url, basepath: str = None,verbose = False, driver = None) -> pd.DataFrame:
    ''' Full Table function
        Note:\n
            The following function will get us for a given symoble the full table
            with: \n
            symbol, timestamp, hour, article title, article link,
            can be filtered based on our given period of time of analysis.
    '''
    # This is a global counter for all articles for a given company.
    console = Console()
    symbol = url.split("scode=")[1].split("&")[0]
    articlePDFIndex = 1
    try:
        driver.get(url)
        # Getting all the body of the html of the given webpage
        # body_html = driver.find_element_by_xpath("/html/body")
        if verbose:
            console.log(driver.title)
        # console.log(body_html.text)

        # 1. Find the elements of subpages index and how many pages for the given url
        # --------------
        # current_url  is the main landing page
        kList = [driver.current_url]
        linkIndexClassName = "pageIndexNum "
        linkIndexNum = driver.find_elements(by='class name', value = linkIndexClassName)
        linkDateList = [ ]
        linkTitleList = [ ]
        articlesLinksList = [ ]
        mainLinkList = []
        globalArticleIndexList = []
        relativeArticleIndexList = []
        pageIndexList = []
        for idx, link in enumerate(linkIndexNum):
            for l in link.find_elements(by="tag name", value="a"):
                kList.append(l.get_attribute("href"))
        if verbose:
            console.log(kList, len(linkIndexNum))
        # 2. Find the links of each subpage including the main page.
        # --------------
        for pageIndex, link in enumerate(kList, 1):
            driver.get(link)
            if verbose:
                console.log(f"{pageIndex}{driver.title}")
                console.log(f"---------------")
            class_name = "m-dateTimeTable_body"
            articleTableElements = driver.find_elements(by="class name",value = class_name)
            for articleTableElement in articleTableElements:
                class_name="m-dateTimeTable_body_dateTime "
                dateTimeElements = articleTableElement.find_elements(by="class name", value = class_name)
                class_name="m-dateTimeTable_body_index"
                articleTitleTableEelements = articleTableElement.find_elements(by="class name", value = class_name)
                for sublinkIdx,(placeholderDate, placeholderTitle) in enumerate(zip(dateTimeElements, articleTitleTableEelements),1):
                    articlelink = placeholderTitle.find_element(by="tag name", value="a").get_attribute("href")
                    if verbose:
                        console.log(placeholderDate.text, placeholderTitle.text, articlelink)
                    linkDateList.append(placeholderDate.text)
                    linkTitleList.append(placeholderTitle.text)
                    articlesLinksList.append(articlelink)
                    mainLinkList.append(link)
                    # update globalArticleIndexList
                    globalArticleIndexList.append(articlePDFIndex)
                    relativeArticleIndexList.append(sublinkIdx)
                    pageIndexList.append(pageIndex)
                    articlePDFIndex += 1

        assert (len(linkDateList) == len(linkTitleList) == len(articlesLinksList)), emoji.emojize(f"[:no_entry_sign:] Error occur at symbol: {symbol} at Page {link}  of linkDateList: , the length of linkTitleList and the length of articlesLinksList are:{len(linkDateList)}, {len(articlesLinksList)} and {len(linkTitleList)} consequently! the asseration of elements is not equal the lenght")
        if verbose:
            console.log("[:sparkles:] Done with the scraping of the given symbol:", symbol)
        # Now we download the pdf for each article and we also rename the pdf we download.

        companyArticleInfoDict = {
            "symbol": symbol,
            "globalArticleIndex": globalArticleIndexList,
            "relativeArticleIndex": relativeArticleIndexList,
            "pageIndex": pageIndexList,
            "mainWebPage": url,
            "mainLinkList": mainLinkList,
            "linkDateList": linkDateList,
            "linkTitleList": linkTitleList,
            "articlesLinksList": articlesLinksList,

        }
        df = pd.DataFrame(companyArticleInfoDict)
        return df
    except Exception as e:
        console.log(f"[red]:warning:[reset] [yellow] Error occurred at {str(str(inspect.currentframe())).split(' ')[-1][:-1]} function check here:[reset] {e}", log_locals=False)
        e.args += ('problem occurred with the input ... ', )
        raise


def updateDataFrame(df, options: dict = None):
    '''Update DateFrame with the given options\n
    params:\n
    -------
        - df `pd.DataFrame`: dataframe of the company stats for discolsure
        articles, following a specific single symbol\n
        - options `dict`: options
        for the update, the timestamp to the desrible period\n
        - Note:\n
            - This function needs your pd.DataFrame to generate from the
              function `companyDisclosureStats`, it assumes you have run the
              previous function, if this will not be called, then the full
              dataframe will be returned, for all timestamps.
    output:\n
    -------
        - output `pd.DataFrame`: updated dataframe with the given options.
    '''

    # Notice that for the timestamp format you have Y and y and the difference
    # between them is one give full format while the other is shortcut such as
    # Y:2022 while y:220
    df['timestamp'] = pd.to_datetime(df['linkDateList'], format='%y/%m/%d %H:%M')
    if options is not None:
        '''the format for starting date and end date is YYYY-MM-DD'''
        start_date = options['start_date']
        end_date = options['end_date']

        mask = (df['timestamp'] > start_date) & (df['timestamp'] <= end_date)
        df = df.loc[mask]
        return df
    else:
        # Default full timestamp
        return df



def pdfDownloader(df: pd.DataFrame, basepath: str = None, verbose = False, driver = None):
    console = Console()
    try:
        # ----------- Rename the pdf ----------
        """Renaming the article is based on the following policy
        - Firm --> symbol
        - n the pdf global number (all articles related to the given company)
        - k the pdf relative number to the page
        - p the page number
        - time stamp of the downloading.
        """
        # ------ Download the pdf files and rename them -------
        symbolList = df['symbol'].values
        linkDateList = df['linkDateList'].values
        linkTitleList= df['linkTitleList'].values
        articlesLinksList = df['articlesLinksList'].values
        globalArticleIndex = df['globalArticleIndex'].values
        relativeArticleIndex = df['relativeArticleIndex'].values
        pageIndexList = df['pageIndex'].values

        pdfNameList = [ ]
        for symbol,articlePDFIdex, sublinkPerPageIndex,sublinkPageIndex ,linkDate, linkTitle, articleLink in zip(symbolList,globalArticleIndex, relativeArticleIndex, pageIndexList, linkDateList, linkTitleList, articlesLinksList):
            # if verbose:
            #     console.log(f"{symbol} {articlePDFIdex} {sublinkPerPageIndex} {sublinkPageIndex} {linkDate}{linkTitle}")
            # ----------- Download the pdf files and rename them -------
            # --------------
            # 1. Download the pdf files
            # --------------

            createdTime = datetime.now()
            pdfNameChangerTime = createdTime.strftime("TS_%Y_%m_%d_%H_%M_%S")
            pdfName = f"Firm_{symbol}_n{articlePDFIdex}_k{sublinkPerPageIndex}_p{sublinkPageIndex}_{pdfNameChangerTime}"
            # -------- Download the pdf ----------
            if basepath is None:
                basepath = "./database/disclosureProcessedData/"
            else:
                basepath = basepath

            # --------------
            # 1.1. Download the pdf files
            # --------------
            driver.get(articleLink)
            buttonLocation = '//*[@id="btn-download"]'
            buttonObject = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, buttonLocation)))
            time.sleep(5)
            buttonObject.click()
            driver.implicitly_wait(10)
            oldName = max([basepath + f for f in os.listdir(basepath)], key=os.path.getctime,)
            newName = os.path.join(basepath, f"{pdfName}.pdf")
            os.rename(oldName, newName)
            # articlePDFIndex += 1
            # --- Debugger ----
            if verbose:
                rprint(
                    emoji.emojize(
                        f"[:party_popper:] At Symbol: {symbol} Page:{sublinkPageIndex}-{articlePDFIdex}/{len(articlesLinksList)} Article PDF No.:{articlePDFIdex} Downloading PDF {pdfName}, Article Date:{linkDate}, Title: {linkTitle}, Link: {articleLink}"
                    )
                )
            # --------------
            # 1.2. Download the pdf files
            # --------------
            #
            pdfNameList.append(pdfName)
        df['pdfName'] = pdfNameList
        return df

    except Exception as e:
        console.log(f":warning: Error occurre at downloading the pdf files of company {symbol}: check: {e}")
        raise





if __name__ == "__main__":
    console = Console()
    #url = "https://www.nikkei.com/nkd/company/disclose/?scode=9913&ba=9&hm="
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
    console.log(df)

    driver.quit()
