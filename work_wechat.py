import requests
import json
import os
from datetime import datetime
import sys
import bs4
from time import localtime
import time

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
    response = requests.get(url=url, headers=headers)

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
    weather_list = soup.find_all('p', class_='wea')
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
    r = requests.get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en

def get_access_token(corpid, corpsecret):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}"
    try:
        response = requests.get(url)
        result = response.json()
        if result["errcode"] != 0:
            print(f"获取 access_token 失败: {result}")
            if result["errcode"] == 60020:
                print("\n请在企业微信管理后台进行以下设置：")
                print("1. 进入应用管理")
                print("2. 找到您的应用")
                print("3. 点击'设置接收消息服务器URL'")
                print("4. 填写一个域名（如：https://kai01-1.github.io/weather-push/）")
                print("5. 点击'保存'")
                print("6. 在同一个页面找到'IP白名单'")
                print("7. 添加以下 IP：")
                print("   - 42.236.235.233")
                print("   - 或者添加 '0.0.0.0' 来允许所有 IP 访问（测试时可以这样做）")
                print("\n当前 IP: 42.236.235.233")
            return None
        return result["access_token"]
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None

def send_message(access_token, agentid, city_name, today_date, today_weather, now, today_wind, tomorrow,
                 tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind, note_ch, note_en):
    if not access_token:
        print("无法获取 access_token，推送失败")
        return
        
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]

    message = f"""🌅 今天是 {today} {week}
📍 我现在在 {city_name}
📅 {today_date} 天气 {today_weather}
🌡️ 当前温度 {now}
💨 风力 {today_wind}

📅 明天 {tomorrow} 的天气是 {tomorrow_weather}
⬆️ 最高温度 {tomorrow_max}
⬇️ 最低温度 {tomorrow_min}
💨 风力 {tomorrow_wind}

💡 今日英语：
{note_en}
{note_ch}"""

    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": message
        }
    }

    # 添加重试机制
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.post(url, json=data)
            result = response.json()
            
            if result["errcode"] == 0:
                print("推送消息成功")
                return
            elif result["errcode"] == 60020:
                print(f"\nIP 访问受限，请在企业微信管理后台进行以下设置：")
                print("1. 进入应用管理")
                print("2. 找到您的应用")
                print("3. 点击'设置接收消息服务器URL'")
                print("4. 填写一个域名（如：https://kai01-1.github.io/weather-push/）")
                print("5. 点击'保存'")
                print("6. 在同一个页面找到'IP白名单'")
                print("7. 添加以下 IP：")
                print("   - 42.236.235.233")
                print("   - 或者添加 '0.0.0.0' 来允许所有 IP 访问（测试时可以这样做）")
                print(f"\n当前 IP: {result.get('ip', '未知')}")
                return
            else:
                print(f"推送消息失败: {result}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"将在 5 秒后重试... ({retry_count}/{max_retries})")
                    time.sleep(5)
                else:
                    print("达到最大重试次数，推送失败")
        except Exception as e:
            print(f"发生错误: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"将在 5 秒后重试... ({retry_count}/{max_retries})")
                time.sleep(5)
            else:
                print("达到最大重试次数，推送失败")

def main():
    try:
        # 从环境变量获取配置
        corpid = os.getenv("CORPID")
        corpsecret = os.getenv("CORPSECRET")
        agentid = os.getenv("AGENTID")
        
        if not all([corpid, corpsecret, agentid]):
            raise ValueError("缺少必要的配置信息")
            
    except Exception as e:
        print(f"配置错误: {str(e)}")
        sys.exit(1)

    # 获取accessToken
    access_token = get_access_token(corpid, corpsecret)
    
    # 获取天气信息
    city_name, today_date, today_weather, now, today_wind, tomorrow, tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind = get_weather()
    
    # 获取每日一句英语
    note_ch, note_en = get_ciba()
    
    # 发送消息
    send_message(access_token, agentid, city_name, today_date, today_weather, now, today_wind, tomorrow,
                 tomorrow_weather, tomorrow_max, tomorrow_min, tomorrow_wind, note_ch, note_en)

if __name__ == "__main__":
    main() 