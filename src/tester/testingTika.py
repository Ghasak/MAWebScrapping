# import parser object from tike
import os
from tika import parser

path =  os.path.join(os.getcwd(), 'src/tester/Firm_3612_n4_k4_p1_TS_2022_03_15_00_53_53.pdf')
# opening pdf file
parsed_pdf = parser.from_file(path)

# saving content of pdf
# you can also bring text only, by parsed_pdf['text']
# parsed_pdf['content'] returns string
data = parsed_pdf['content']

# Printing of content
print(data)

# <class 'str'>
print(type(data))
