import requests
import json
import os
from datetime import datetime
import sys
import bs4
from time import localtime
import time
import hashlib
import base64
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET
import random
import string
from urllib.parse import unquote
from flask import Flask, request, make_response

app = Flask(__name__)

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
    return note_ch,note_en

class WeChatWork:
    def __init__(self):
        # 企业微信配置
        self.corpid = "wwbd1a3d5c0ff54fa4"
        self.corpsecret = "45AZEb6fRruKKxpbBIl2VQSDTtX2twprciM4pZX4stE"
        self.agentid = "1000003"
        self.token = "NO9kHTgPpL845YikgC"
        self.encoding_aes_key = "GkHTeGXvJO0vwF5SeGJdxsp5yrA6waoRHVJPRoEdPss"
        
        # 获取访问令牌
        self.access_token = self.get_access_token()
        if not self.access_token:
            raise Exception("配置错误: 无法获取访问令牌")

    def get_access_token(self):
        """获取访问令牌"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        try:
            response = requests.get(url)
            result = response.json()
            print(f"获取访问令牌响应: {result}")
            if result.get("errcode") == 0:
                return result.get("access_token")
            else:
                print(f"获取访问令牌失败: {result.get('errmsg')}")
                return None
        except Exception as e:
            print(f"获取访问令牌异常: {str(e)}")
            return None

    def verify_signature(self, msg_signature, timestamp, nonce):
        """验证签名"""
        sorted_list = sorted([self.token, timestamp, nonce])
        signature = hashlib.sha1(''.join(sorted_list).encode()).hexdigest()
        return signature == msg_signature

    def decrypt_message(self, encrypted_message):
        """解密消息"""
        try:
            aes_key = base64.b64decode(self.encoding_aes_key + "=")
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
            decrypted = cipher.decrypt(base64.b64decode(encrypted_message))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"解密错误: {str(e)}")
            return None

    def encrypt_message(self, message):
        """加密消息"""
        try:
            aes_key = base64.b64decode(self.encoding_aes_key + "=")
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
            encrypted = cipher.encrypt(message.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"加密错误: {str(e)}")
            return None

    def handle_callback(self, msg_signature, timestamp, nonce, echostr):
        """处理回调验证"""
        try:
            # URL decode 参数
            msg_signature = unquote(msg_signature)
            timestamp = unquote(timestamp)
            nonce = unquote(nonce)
            echostr = unquote(echostr)

            # 验证签名
            if not self.verify_signature(msg_signature, timestamp, nonce):
                return None

            # 解密消息
            decrypted_msg = self.decrypt_message(echostr)
            return decrypted_msg

        except Exception as e:
            print(f"回调处理错误: {str(e)}")
            return None

    def send_message(self, user_id, content):
        """发送消息"""
        if not self.access_token:
            return False
            
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": content
            }
        }
        try:
            response = requests.post(url, json=data)
            result = response.json()
            print(f"发送消息响应: {result}")
            
            if result.get("errcode") == 60020:
                print("IP 访问受限，请在企业微信管理后台添加 IP 白名单")
                print(f"当前 IP: {result.get('from_ip')}")
                return False
            
            return result.get("errcode") == 0
        except Exception as e:
            print(f"发送消息异常: {str(e)}")
            return False

# 创建全局企业微信实例
wechat = WeChatWork()

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        # 处理验证请求
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        decrypted_msg = wechat.handle_callback(msg_signature, timestamp, nonce, echostr)
        if decrypted_msg:
            return decrypted_msg
        return "验证失败"
    
    elif request.method == 'POST':
        # 处理消息接收
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        
        xml_data = request.data
        root = ET.fromstring(xml_data)
        encrypt = root.find('Encrypt').text
        
        decrypted_msg = wechat.handle_callback(msg_signature, timestamp, nonce, encrypt)
        if decrypted_msg:
            # 这里可以处理接收到的消息
            print(f"收到消息: {decrypted_msg}")
            return "success"
        return "处理失败"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 