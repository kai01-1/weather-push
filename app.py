from flask import Flask, request
from urllib.parse import unquote
import base64
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Replace these with your actual Token and EncodingAESKey from WeChat Work admin panel
TOKEN = "NO9kHTgPpL845YikgC"
ENCODING_AES_KEY = "GkHTeGXvJO0vwF5SeGJdxsp5yrA6waoRHVJPRoEdPss"

def decrypt_message(encrypted_message):
 # Decrypt the message
 aes_key = base64.b64decode(ENCODING_AES_KEY + "=")
 cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
 decrypted = cipher.decrypt(base64.b64decode(encrypted_message))
 return decrypted.decode('utf-8')

@app.route('/callback', methods=['GET'])
def callback():
 # Get request parameters
 msg_signature = request.args.get('msg_signature')
 timestamp = request.args.get('timestamp')
 nonce = request.args.get('nonce')
 echostr = request.args.get('echostr')

 # URL decode the parameters
 msg_signature = unquote(msg_signature)
 timestamp = unquote(timestamp)
 nonce = unquote(nonce)
 echostr = unquote(echostr)

 # Decrypt echostr to get the message content
 decrypted_msg = decrypt_message(echostr)

 # Return the decrypted message content
 return decrypted_msg

@app.route('/callback', methods=['POST'])
def receive_message():
 # Get request parameters
 msg_signature = request.args.get('msg_signature')
 timestamp = request.args.get('timestamp')
 nonce = request.args.get('nonce')

 # Get request body
 xml_data = request.data

 # Parse XML
 root = ET.fromstring(xml_data)
 to_user_name = root.find('ToUserName').text
 agent_id = root.find('AgentID').text
 encrypt = root.find('Encrypt').text

 # Decrypt the message
 decrypted_msg = decrypt_message(encrypt)

 # Construct passive response package
 response_xml = f"""
 <xml>
    <Encrypt><![CDATA[{encrypt}]]></Encrypt>
    <MsgSignature><![CDATA[{msg_signature}]]></MsgSignature>
    <TimeStamp>{timestamp}</TimeStamp>
    <Nonce><![CDATA[{nonce}]]></Nonce>
 </xml>
 """

 # Return response
 return response_xml, 200

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=80)
