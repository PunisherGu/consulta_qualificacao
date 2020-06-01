import re
from io import BytesIO
import pytesseract

from PIL import Image
from requests import Session
from lxml import html

import json


def get_captcha(s):
    page = s.get("http://consultacadastral.inss.gov.br/Esocial/captcha-load/")

    captcha = f"I_{re.findall('(?<=I_)(.*?)(?=_interne)', page.content.decode('ISO-8859-1'))[0]}_internet"

    response = s.get(f'http://consultacadastral.inss.gov.br/Esocial/api/imagem?d={captcha}')
    return [captcha, response.content]


def solve_captcha(img):
    black_and_white = img.convert("L") #converting to black and white 
    black_and_white.save("black_and_white.png")
    text = pytesseract.image_to_string(Image.open('black_and_white.png'))
    return text


def make_request(s, data, header):
    page = s.post('http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtml', data=data, headers=header)
    tree = html.fromstring(page.content)
    xpath_data = tree.xpath('//tbody/tr/td/span/text()')
    data = dict(nome=xpath_data[0], data_nasimento=xpath_data[1], cpf=xpath_data[2], nis=xpath_data[3], status=xpath_data[4], detail=xpath_data[5])
    print(json.dumps(data, indent = 4))

