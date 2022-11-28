import os
import subprocess
import sys
from rich import print as rprint



path = os.path.dirname(os.path.abspath(__file__))
#base_path = os.path.dirname(path)
#rprint(path)
# create a new directory if it doesn't exists
# if not os.path.exists(path+ '/database/disclosureProcessedData/parsedConverated'):
#     rprint("[ :file_cabinet: ] Creating ./database/disclosureProcessedData/parsedConverated")
#     os.makedirs(path+ '/database/disclosureProcessedData/parsedConverated')
basepath = f"{path}/database/disclosureProcessedData/"

symbol = '1333'
pdfName= "Firm_1333_n1_k1_p1_TS_2022_03_11_19_28_09"
#os.chmod(f"{path}/database/parsedConverated/{symbol}", 0o666)
subprocess.run("mv {basepath}{pdfName}.pdf {basepath}parsedConverated/{symbol}/".format(basepath=basepath,pdfName=pdfName,symbol=symbol), shell=True)
