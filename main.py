from selenium import webdriver
import time
import requests
import base64
import config
import sys

driver = webdriver.Chrome()
if len(sys.argv) < 2:
    print('Please supply email and password as argument')
    sys.exit()
email = str(sys.argv[1])
password = str(sys.argv[2])

# Load google login page
def load_site():
    url = "https://accounts.google.com/AccountChooser/signinchooser?service=mail&continue=https%3A%2F%2Fmail.google" \
          ".com%2Fmail%2F&flowName=GlifWebSignIn&flowEntry=AccountChooser "
    driver.maximize_window()
    driver.get(url)

# Login in using credentials
def login(mail, passwd):
    driver.implicitly_wait(5)
    login_label = driver.find_element("id", 'identifierId')
    login_btn = driver.find_element('xpath',
                                    '//*[@id="identifierNext"]/div/button/span')
    login_label.send_keys(mail)
    login_btn.click()
    time.sleep(5)
    # if there's a captcha, let it handle by AZcaptcha API
    if driver.current_url.find("identifier"):
        print('Captcha found')
        time.sleep(5)
        check = driver.current_url
        # wait for correct captcha - takes some time
        while driver.find_element('id', 'captchaimg'):
            if driver.current_url != check:
                break
            print('solving captcha')
            guess_captcha()
            time.sleep(5)

    driver.implicitly_wait(5)
    time.sleep(3)
    # password field must by found using xpath, otherwise Selenium can't see him
    password_label = driver.find_element('xpath',
                                         '//*[@id="password"]/div[1]/div/div[1]/input')
    password_label.click()
    password_label.clear()
    password_btn = driver.find_element('xpath',
                                       '//*[@id="passwordNext"]/div/button/span')

    password_label.send_keys(passwd)
    password_btn.click()


def guess_captcha():
    src = driver.find_element('id', 'captchaimg').get_attribute("src")
    base_image = base64.b64encode(requests.get(src).content)
    payload_post = {'key': config.api_key, 'method': 'base64', 'body': base_image}
    r_post = requests.post('http://azcaptcha.com/in.php', data=payload_post)
    captcha_id = r_post.text.split('|')[1]
    payload_get = {'key': config.api_key, 'action': 'get', 'id': captcha_id}
    time.sleep(6)
    r_get = requests.get('http://azcaptcha.com/res.php', payload_get)
    driver.find_element('xpath', '//*[@id="ca"]').send_keys(r_get.text.split('|')[1])
    driver.find_element('xpath', '//*[@id="identifierNext"]/div/button/span').click()


def main():
    print('Logging to gmail')
    load_site()
    login(email, password)
    print('Successful')


if __name__ == '__main__':
    main()
