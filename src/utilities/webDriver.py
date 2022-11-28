import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from rich.console import Console
console = Console()


WEBDRIVEDIR = os.environ["FIREFOXWEBDRIVEDIR"]
DATASTORAGEDIR = os.environ["DATASTORAGE"]


class firFoxDriver:
    '''Fire Fox driver based on Selenium driver\n
        Note:\n
            The current selenium version is 4.1 compatable with firefox geckodriver version 0.3.1\n
            geckodriver 0.30.0 (d372710b98a6 2021-09-16 10:29 +0300)\n
                `pipenv run python -c "import selenium;print(selenium.__version__)"`\n
            Loading .env environment variables...\n
                `4.1.2`\n
    '''
    def __init__(self):
        # Define the location of your driver
        self.service = Service(str(WEBDRIVEDIR))
        # Define the options of firefox to use
        self.options = Options()

    def __str__(self):
        console.log(f"Our Driver is located at [red]{WEBDRIVEDIR}", log_locals=False)


    def engine(self):
        try:
            self.options.headless = True
            # Setting for where to store the downloaded files like (PDF)
            self.options.set_preference("browser.download.dir", DATASTORAGEDIR)
            self.options.set_preference("browser.download.folderList", 2)
            self.options.set_preference("browser.download.manager.showWhenStarting", False)
            self.options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            self.options.set_preference("browser.helperApps.alwaysAsk.force", False)
            self.options.set_preference("browser.download.manager.showWhenStarting", False)
            self.options.set_preference("browser.download.manager.alertOnEXEOpen", False)
            self.options.set_preference("browser.helperApps.alwaysAsk.force", False)
            self.options.set_preference("browser.download.manager.focusWhenStarting", False)
            self.options.set_preference("browser.download.manager.useWindow", False)
            self.options.set_preference("browser.download.manager.showAlertOnComplete", False)
            self.options.set_preference("browser.download.manager.closeWhenDone", False)
            self.options.set_preference("browser.download.viewableInternally.previousHandler.alwaysAskBeforeHandling.pdf",False)
            self.options.set_preference("browser.download.viewableInternally.previousHandler.preferredAction.pdf", 0)
            self.options.set_preference("pdfjs.migrationVersion", 2)
            # Testing
            driver = webdriver.Firefox(service = self.service , options=self.options)
            return driver
        except Exception as e:
            console.log(f"[red]\u26a0[reset] [yellow] Error occurred at driver engine class initialization:[reset] {e}", log_locals=False)

    def testing(self):
        driver = self.engine()
        driver.get("http://www.python.org")
        console.log(driver.title)
        driver.close()


