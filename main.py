import json
import re
from io import BytesIO

import pytesseract
from lxml import html
from PIL import Image
from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent
from requests import Session

import utils

s = Session()
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
page = s.get("http://consultacadastral.inss.gov.br/Esocial/pages/index.xhtml")
tree = html.fromstring(page.content)
inputs = tree.xpath('//input[@type="hidden"]/@value')
token = inputs[1]
view = inputs[2]
cpf = '121.354.046-16'
data = '16/08/1994'
name = 'GUSTAVO ANDRE SANTOS NOGUEIRA'
nis = '201.84302.52-2'

header = {
    'Upgrade-Insecure-Requests':'1',
    'Origin':'http://consultacadastral.inss.gov.br',
    'Content-Type':'application/x-www-form-urlencoded',
    'User-Agent': user_agent_rotator.get_random_user_agent(),
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
data = {
    'DTPINFRA_TOKEN':token,
    'formQualificacaoCadastral':'formQualificacaoCadastral',
    'formQualificacaoCadastral:btAdicionar':'Adicionar',
    'formQualificacaoCadastral:cpf':cpf,
    'formQualificacaoCadastral:dataNascimento':data,
    'formQualificacaoCadastral:nis':nis,
    'formQualificacaoCadastral:nome':name,
    'javax.faces.ViewState': view,
}
page = s.post('http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtml', data=data, headers=header)
tree = html.fromstring(page.content)
name = tree.get_element_by_id("formQualificacaoCadastral:nome")
view = tree.xpath('//input[@type="hidden"]/@value')[2]

data = {
    'DTPINFRA_TOKEN':token,
    'formValidacao2':'formValidacao2',
    'formValidacao2:botaoValidar2':'Consultar',
    'javax.faces.ViewState': view,

}
page = s.post("http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtml", data=data, headers=header)
page = s.get("http://consultacadastral.inss.gov.br/Esocial/captcha-load/")

captcha = f"I_{re.findall('(?<=I_)(.*?)(?=_interne)', page.content.decode('ISO-8859-1'))[0]}_internet"

response = s.get(f'http://consultacadastral.inss.gov.br/Esocial/api/imagem?d={captcha}')
img = Image.open(BytesIO(response.content))
img.save("captcha.jpg")
# captcha_resp = input("Captcha:")

#quebrar captcha aqui

black_and_white = img.convert("L") #converting to black and white 
black_and_white.save("black_and_white.png")
number = pytesseract.image_to_string(Image.open('black_and_white.png'))
print(number)
captcha_resp = number


data = {
    'DTPINFRA_TOKEN':token,
    'captcha_campo_desafio':captcha,
    'captcha_campo_resposta':captcha_resp,
    'formValidacao':'formValidacao',
    'formValidacao:botaoValidar':'Consultar',
    'javax.faces.ViewState':view,
}
page = s.post('http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtml', data=data, headers=header)
tree = html.fromstring(page.content)
xpath_data = tree.xpath('//tbody/tr/td/span/text()')
try:
    data = dict(nome=xpath_data[0], data_nasimento=xpath_data[1], cpf=xpath_data[2], nis=xpath_data[3], status=xpath_data[4], detail=xpath_data[5])
except:
    i = 0
    while not 'nome' in data:
        content = utils.get_captcha(s)
        img = Image.open(BytesIO(content[1]))
        img.save("captcha.jpg")
        captcha_resp = utils.solve_captcha(img)
        if captcha_resp != '':
            import pdb; pdb.set_trace()
            i += 1
            print(i)
            data = {
                'DTPINFRA_TOKEN':token,
                'captcha_campo_desafio':content[0],
                'captcha_campo_resposta':captcha_resp,
                'formValidacao':'formValidacao',
                'formValidacao:botaoValidar':'Consultar',
                'javax.faces.ViewState':view,
            }
            page = s.post('http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtml', data=data, headers=header)
            tree = html.fromstring(page.content)
            xpath_data = tree.xpath('//tbody/tr/td/span/text()')
            if 'nome' in data:
                data = dict(nome=xpath_data[0], data_nasimento=xpath_data[1], cpf=xpath_data[2], nis=xpath_data[3], status=xpath_data[4], detail=xpath_data[5])
                print(json.dumps(data, indent = 4))
        else:
            pass
