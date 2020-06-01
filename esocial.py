import json
import re
from io import BytesIO
from random import choice

import pytesseract
from lxml import html
from PIL import Image, ImageOps
from requests import Session

class CONST_URL:
    INDEX = 'http://consultacadastral.inss.gov.br/Esocial/pages/index.xhtml'
    QUALIFICAR = 'http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtm'
    CAPTCHA = 'http://consultacadastral.inss.gov.br/Esocial/captcha-load/'
    CAPTCHA_IMG = 'http://consultacadastral.inss.gov.br/Esocial/api/imagem?d='


class ESocial(object):
    def __init__(self, cpf, birth_date, name, nis):
        self.session = Session()
        self.cpf = cpf
        self.birth_date = birth_date
        self.name = name
        self.nis = nis
        self.logged = False
        self.added = False
        self.captcha = False
        self.urls = CONST_URL()
        self.token, self.view = self._get_hidden_inputs()

    def _get_ua(self):
        ua_list = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
            'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
        ]
        return choice(ua_list)

    def _gen_header(self):
        return {
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'http://consultacadastral.inss.gov.br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self._get_ua(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
        }

    def _get_hidden_inputs(self):
        page = self.session.get(self.urls.INDEX)
        tree = html.fromstring(page.content)
        inputs = tree.xpath('//input[@type="hidden"]/@value')
        return inputs[1], inputs[2]

    def login_page(self):
        payload = {
            'DTPINFRA_TOKEN': self.token,
            'formQualificacaoCadastral': 'formQualificacaoCadastral',
            'formQualificacaoCadastral:btAdicionar': 'Adicionar',
            'formQualificacaoCadastral:cpf': self.cpf,
            'formQualificacaoCadastral:dataNascimento': self.birth_date,
            'formQualificacaoCadastral:nis': self.nis,
            'formQualificacaoCadastral:nome': self.name,
            'javax.faces.ViewState': self.view,
        }

        page = self.session.post(self.urls.QUALIFICAR,
                                 data=payload, headers=self._gen_header())
        tree = html.fromstring(page.content)
        self.logged = True
    

    def add_page(self):
        payload = {
            'DTPINFRA_TOKEN': self.token,
            'formValidacao2': 'formValidacao2',
            'formValidacao2:botaoValidar2': 'Consultar',
            'javax.faces.ViewState': self.view,

        }
        if self.logged:
            self.session.post(self.urls.QUALIFICAR,
                              data=payload, headers=self._gen_header())
            self.added = True

    def captcha_to_img(self):
        page = self.session.get(self.urls.CAPTCHA)
        captcha =  f"I_{re.findall('(?<=I_)(.*?)(?=_interne)', page.content.decode('ISO-8859-1'))[0]}_internet"
        self.captcha = captcha
        response = self.session.get(
            f'{self.urls.CAPTCHA_IMG}{captcha}')
        img = Image.open(BytesIO(response.content))
        img.show()
        return img

    def solve_captcha(self, img):
        black_and_white = img.convert("L") #converting to grayscale
        black_and_white.save("black_and_white.png")
        text = pytesseract.image_to_string(Image.open('black_and_white.png'))
        
        #auto_contrast
        # im2 = ImageOps.autocontrast(black_and_white, cutoff = 2, ignore = 2) 
        # im2.save('auto.jpg')
        # text = pytesseract.image_to_string(Image.open('auto.jpg'))
        text = re.sub(r'[\W_]+', '', text)
        return text

    def consultar_page(self, captcha_resp):
        paylod = {
            'DTPINFRA_TOKEN': self.token,
            'captcha_campo_desafio': self.captcha,
            'captcha_campo_resposta': captcha_resp,
            'formValidacao': 'formValidacao',
            'formValidacao:botaoValidar': 'Consultar',
            'javax.faces.ViewState': self.view,
        }
        page = self.session.post(self.urls.QUALIFICAR,data=paylod, headers=self._gen_header())
        tree = html.fromstring(page.content)
        xpath_data = tree.xpath('//tbody/tr/td/span/text()')
        data = dict(nome=xpath_data[0],
                        data_nascimento=xpath_data[1],
                        cpf=xpath_data[2],
                        nis=xpath_data[3],
                        status=xpath_data[4],
                        detail=xpath_data[5])
        return json.dumps(data, indent=4)
