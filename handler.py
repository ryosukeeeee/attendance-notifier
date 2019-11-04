from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import os
import requests
from bs4 import BeautifulSoup
import html5lib

URL = os.environ['URL']
COMPANY_ID = os.environ['COMPANY_ID']
user_id = os.environ['USER_ID']
password = os.environ['PASSWORD']
token = os.environ['SLACK_TOKEN']
slack_channel = os.environ['SLACK_CHANNEL_ID']

def main(event, context):
        
    chromedriver_path = '/opt/chromedriver'
    o = Options()
    o.binary_location = '/opt/headless-chromium'
    o.add_argument('--headless')
    o.add_argument('--disable-gpu')
    o.add_argument('--no-sandbox')
    o.add_argument("--window-size=1280x1696")
    o.add_argument("--disable-application-cache")
    o.add_argument("--disable-infobars")
    o.add_argument("--hide-scrollbars")
    o.add_argument("--enable-logging")
    o.add_argument("--log-level=0")
    o.add_argument("--single-process")
    o.add_argument("--ignore-certificate-errors")
    o.add_argument("--homedir=/tmp")

    driver = webdriver.Chrome(chromedriver_path, options=o)

    try:
        cells = get_cells(driver)
        working_days, sum_time, over_time = calculate_working_time(cells)
        text = show_working_time(working_days, sum_time, over_time)

    except Exception as e:
        print("webdriverでエラー")
        print(e)

        return {
            'statusCode': 500,
            'body': "Error occured\n",
            'isBase64Encoded': False
        }

    driver.quit()

    try:
        param = {
            'token': token,
            'channel': slack_channel, 
            'mrkdwn': True,
            'text': text
        }

        response = requests.post(url="https://slack.com/api/chat.postMessage", params=param)
        print("status code: ", response.status_code)
        print("response text: ", response.text)
    except Exception as e:
        print("Slackへの投稿でエラー")
        print(e)

        return {
            'statusCode': 500,
            'body': "Error occured\n",
            'isBase64Encoded': False
        }

    return {
        'statusCode': 200,
        'body': "succeeded\n",
        'isBase64Encoded': False
    }



def get_cells(driver):
    """Akashiの出勤簿からtableタグのcellを取得する
    Returns:
        list -- trタグのlist
    """

    driver.get(URL)

    driver.find_element_by_id('form_company_id').send_keys(COMPANY_ID)
    driver.find_element_by_id('form_login_id').send_keys(user_id)
    driver.find_element_by_id('form_password').send_keys(password)
    driver.find_element_by_xpath('//*[@id="new_form"]/input[4]').click()

    # jQueryで描画しているので待つ
    sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html5lib')
    table = soup.find(class_='c-main-table-body')
    cells = table.find_all(class_='c-main-table-body__row')

    driver.close()

    return cells


def calculate_working_time(cells):
    """勤務予定日、総勤務時間、超過or不足時間を計算する
    Arguments:
        cells {list} -- trタグのlist
    Returns:
        tuple(int, int, int) -- 勤務予定総時間、総勤務時間、超過or不足時間 (分)
    """

    # 総勤務時間（分）
    sum_time = 0
    # 勤務実績（日）
    worked_days = 0
    # まだ勤務していない日（日）
    working_days = 0

    for cell in cells:
        work = cell.find_all('td', class_='c-main-table-body__cell')[2]
        work = work.text.strip()

        time = cell.find_all('td', class_='c-main-table-body__cell')[3]
        time = time.text.strip()

        # timeが存在かつ0:00ではない
        if time and time != '0:00':
            hour, minute = time.split(':')
            sum_time += int(hour) * 60 + int(minute)
            worked_days += 1
        elif not time and work == '勤務':
            working_days += 1

    # 超過or不足時間（分）＝　総勤務時間　- （勤務実績（日）* 8時間 * 60分）
    over_time = sum_time - worked_days * 8 * 60

    return working_days, sum_time, over_time


def show_working_time(working_days, sum_time, over_time):
    """総勤務時間と超過or不足時間を出力する
    TODO: 超過or不足していたら 1日あたりどれくらい早く(or遅く)帰ればいいのか計算する
    Arguments:
        sum_time {int} -- 総勤務時間
        over_time {int} -- 超過or不足時間
    """

    if over_time > 0:
        over_hour, over_minute = divmod(over_time, 60)
        result_hour, result_minute = divmod(sum_time, 60)
        print('total : ' + '{:02}:{:02}'.format(result_hour, result_minute))
        print('over : ' + '{:02}:{:02}'.format(over_hour, over_minute))
        print(over_time // working_days)

        text = '昨日までの労働時間: '+'{:02}:{:02}'.format(result_hour, result_minute) + '\n'
        text = text + '超過労働時間: ' + '{:02}:{:02}'.format(over_hour, over_minute)
    else:
        over_hour, over_minute = divmod(abs(over_time), 60)
        result_hour, result_minute = divmod(sum_time, 60)
        print('total : ' + '{:02}:{:02}'.format(result_hour, result_minute))
        print('under : ' + '{:02}:{:02}'.format(over_hour, over_minute))
        print(abs(over_time) // working_days)
        text = '昨日までの労働時間: '+'{:02}:{:02}'.format(result_hour, result_minute) + '\n'
        text = text + '不足労働時間: ' + '{:02}:{:02}'.format(over_hour, over_minute)
    
    return text
