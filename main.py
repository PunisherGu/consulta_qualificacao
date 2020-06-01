from esocial import ESocial


def main():
    cpf = '121.354.046-16'
    birth_date = '16/08/1994'
    name = 'GUSTAVO ANDRE SANTOS NOGUEIRA'
    nis = '201.84302.52-2'

    retries = 15
    esocial = ESocial(cpf, birth_date, name, nis)
    esocial.login_page()
    esocial.add_page()
    print(f'Logged: {esocial.logged} Added:{esocial.logged}')
    img = esocial.captcha_to_img()
    # captcha_resp = esocial.solve_captcha(img)
    captcha_resp = input('captcha: ')
    resp = esocial.consultar_page(captcha_resp)

    while not resp:
        captcha = esocial.captcha_to_img()
        captcha_resp = esocial.solve_captcha(captcha)
        if len(captcha_resp) >= 4:
            retries = retries - 1
            print(f'Tentativa {retries} [{captcha_resp}]')
            resp = esocial.consultar_page(captcha_resp)
        if retries == 0:
            break
    print(resp)


if __name__ == "__main__":
    main()