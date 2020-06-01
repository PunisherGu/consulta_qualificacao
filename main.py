import os

import cv2
import numpy
import pytesseract
from lxml import html
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from requests import Session
from captcha.image import ImageCaptcha
from scipy.ndimage.filters import gaussian_filter

s = Session()

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
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
data = {
    'DTPINFRA_TOKEN':token,
    'formQualificacaoCadastral':'formQualificacaoCadastral',
    'formQualificacaoCadastral':'btAdicionar:Adicionar',
    'formQualificacaoCadastral:cpf':cpf,
    'formQualificacaoCadastral:dataNascimento':data,
    'formQualificacaoCadastral:nis':nis,
    'formQualificacaoCadastral:nome':name,
    'javax.faces.ViewState': view,
}
resp = s.post('http://consultacadastral.inss.gov.br/Esocial/pages/qualificacao/qualificar.xhtml', data=data, headers=header)
img = Image.open('imagem.jpeg')

th1 = 100
th2 = 200 # threshold after blurring
sig = 0.5 # the blurring sigma
original = Image.open("imagem.jpeg")
original.save("original.png") # reading the image from the request
black_and_white =original.convert("L") #converting to black and white
black_and_white.save("black_and_white.png")
first_threshold = black_and_white.point(lambda p: p > th1 and 255)
first_threshold.save("first_threshold.png")
blur=numpy.array(first_threshold) #create an image array
blurred = gaussian_filter(blur, sigma=sig)
blurred = Image.fromarray(blurred)
blurred.save("blurred.png")
final = blurred.point(lambda p: p > th2 and 255)
final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
final = final.filter(ImageFilter.SHARPEN)
final.save("final.png")
number = pytesseract.image_to_string(Image.open('final.png'))
print(number)
