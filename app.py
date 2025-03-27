import random
from time import time, localtime
from requests import get, post
from datetime import datetime, date
import sys
import os
import bs4
import requests
import json

# 全局变量
config = None

def get_color():
    # 往list中填喜欢的颜色即可
    color_list = ['#6495ED', '#3CB371']

    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather():
    city_name = '郑州'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'HttpOnly; userNewsPort0=1; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1660634957; f_city=%E9%87%91%E5%8D%8E%7C101210901%7C; defaultCty=101210901; defaultCtyName=%u91D1%u534E; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1660639816',
        'Host': 'www.weather.com.cn',
        'Referer': 'http://www.weather.com.cn/weather1d/101180101.shtml',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54'

    }
    url = "http://www.weather.com.cn/weather/101180101.shtml"
    response = get(url=url, headers=headers)

    text = response.content.decode('utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    # 存放日期
    list_day = []
    i = 0
    day_list = soup.find_all('h1')
    for each in day_list:
        if i <= 1:  # 今明两天的数据
            list_day.append(each.text.strip())
            i += 1

    # 天气情况
    list_weather = []
    weather_list = soup.find_all('p', class_='wea')  # 之前报错是因为写了class 改为class_就好了
    for i in weather_list:
        list_weather.append(i.text)
    list_weather = list_weather[0:2]  # 只取今明两天

    # 存放当前温度，和明天的最高温度和最低温度
    tem_list = soup.find_all('p', class_='tem')

    i = 0
    list_tem = []
    for each in tem_list:
        if i == 0:
            list_tem.append(each.i.text)
            i += 1
        elif i > 0 and i < 2:
            list_tem.append([each.span.text, each.i.text])
            i += 1

    # 风力
    list_wind = []
    wind_list = soup.find_all('p', class_='win')
    for each in wind_list:
        list_wind.append(each.i.text.strip())
    list_wind = list_wind[0:2]  # 同只取今明两天

    today_date = list_day[0]
    today_weather = list_weather[0]
    now = list_tem[0]
    today_wind = list_wind[0]
    tomorrow = list_day[1]
    tomorrow_weather = list_weather[1]
    tomorrow_max = list_tem[1][0]
    tomorrow_min = list_tem[1][1]
    tomorrow_wind = list_wind[1]

    return city_name, today_date, today_weather, now, today_wind, tomorrow, tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind


def get_ciba():
    # 每日一句英语（来自爱词霸）
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


def send_message(to_user, access_token, city_name, today_date, today_weather, now, today_wind, tomorrow,
                 tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind, daily_love, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "🌅 {} {}".format(today, week),
                "color": "#FF69B4"
            },
            "city": {
                "value": "📍 {}".format(city_name),
                "color": "#4169E1"
            },
            "today": {
                "value": "📅 {}".format(today_date),
                "color": "#FF4500"
            },
            "today_weather": {
                "value": "☀️ {}".format(today_weather),
                "color": "#FF8C00"
            },
            "now": {
                "value": "🌡️ {}".format(now),
                "color": "#FF1493"
            },
            "today_wind": {
                "value": "💨 {}".format(today_wind),
                "color": "#00CED1"
            },
            "tomorrow": {
                "value": "📅 {}".format(tomorrow),
                "color": "#FF4500"
            },
            "tomorrow_weather": {
                "value": "☀️ {}".format(tomorrow_weather),
                "color": "#FF8C00"
            },
            "tomorrow_max": {
                "value": "⬆️ {}".format(tomorrow_max),
                "color": "#FF4500"
            },
            "tomorrow_min": {
                "value": "⬇️ {}".format(tomorrow_min),
                "color": "#4169E1"
            },
            "tomorrow_wind": {
                "value": "💨 {}".format(tomorrow_wind),
                "color": "#00CED1"
            },
            "daily_love": {
                "value": "💝 {}".format(daily_love),
                "color": "#FF69B4"
            },
            "note_en": {
                "value": "📚 {}".format(note_en),
                "color": "#FF1493"
            },
            "note_ch": {
                "value": "💡 {}".format(note_ch),
                "color": "#4169E1"
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


def main():
    global config
    try:
        # 从环境变量获取配置
        config = {
            "app_id": os.getenv("APP_ID"),
            "app_secret": os.getenv("APP_SECRET"),
            "template_id": os.getenv("TEMPLATE_ID"),
            "user": [os.getenv("USER_ID")],
            "weather_token": "d4af1f233754455fbd808aea8f879b34",
            "city": "郑州"
        }
        
        # 验证必要的配置是否存在
        if not all([config["app_id"], config["app_secret"], config["template_id"], config["user"][0]]):
            raise ValueError("缺少必要的配置信息")
            
    except Exception as e:
        print(f"配置错误: {str(e)}")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入省份和市获取天气信息
    city_name, today_date, today_weather, now, today_wind, tomorrow, tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind = get_weather()
    # 获取每日一句英语
    note_ch, note_en = get_ciba()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, city_name, today_date, today_weather, now, today_wind, tomorrow,
                     tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind, "今天也要开开心心的哦", note_ch, note_en)


if __name__ == "__main__":
    main()
    os.system("pause")