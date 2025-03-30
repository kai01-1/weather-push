import random
from datetime import datetime, timedelta
from requests import get, post
import json
import os

def get_qywx_token():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={config['qywx']['corpid']}&corpsecret={config['qywx']['corpsecret']}"
    response = get(url)
    data = response.json()
    if data.get("errcode") != 0:
        raise Exception(f"获取token失败: {data.get('errmsg')}")
    return data["access_token"]

def get_weather():
    url = f"https://devapi.qweather.com/v7/weather/now?location={config['weather']['city_id']}&key={config['weather']['api_key']}"
    response = get(url).json()
    
    today = {
        "temp": response["now"]["temp"],
        "text": response["now"]["text"],
        "wind": f"{response['now']['windDir']} {response['now']['windScale']}级"
    }
    
    forecast_url = f"https://devapi.qweather.com/v7/weather/3d?location={config['weather']['city_id']}&key={config['weather']['api_key']}"
    forecast = get(forecast_url).json()["daily"][1]
    
    return {
        "city_name": config['weather']['city'],
        "today_date": datetime.now().strftime("%m月%d日"),
        "today_weather": today["text"],
        "now": today["temp"],
        "today_wind": today["wind"],
        "tomorrow_weather": forecast["textDay"],
        "tomorrow_max": forecast["tempMax"],
        "tomorrow_min": forecast["tempMin"]
    }

def send_qywx_message(user, token, weather_data, note_ch, note_en):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    data = {
        "touser": user,
        "agentid": config['qywx']['agentid'],
        "msgtype": "text",
        "text": {
            "content": f"""【每日简报】
📍 城市：{weather_data['city_name']}
🌤️ 天气：{weather_data['today_weather']}
🌡️ 温度：{weather_data['now']}℃
💨 风力：{weather_data['today_wind']}
            
💡 每日一句：
{note_ch}
{note_en}"""
        },
        "safe": 0
    }
    response = post(url, json=data)
    if response.json().get("errcode") != 0:
        print(f"推送失败: {response.text}")

if __name__ == "__main__":
    try:
        # 读取配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取token和天气
        token = get_qywx_token()
        weather_data = get_weather()
        
        # 测试推送第一个用户
        send_qywx_message(
            user=config["users"][0],
            token=token,
            weather_data=weather_data,
            note_ch="测试中文句子",
            note_en="Test English sentence"
        )
        
    except Exception as e:
        print(f"错误: {str(e)}")
        os.system("pause")
