# -*- coding: utf-8  -*-

"""
    用户通过微信公众平台发送股票 g+股票代码即可获得股票实时行情信息;
    支持深沪港美不同市场多支股票同时获取;
    ...v1.1
"""
# -*- coding=utf-8 -*-

import time  
from flask import Flask,request, make_response  
import hashlib  
import xml.etree.ElementTree as ET
import stock.SinaStk as stock

app = Flask(__name__)

# 测试
@app.route("/hello")
def hello():
    return "hello"

# 回复 f
def reply_msg(in_msg):
    tips =u"📈查询股票行情请输入：\n'g（空格）股票代码'\n支持同时查询多种市场多支股票~\n如: \n'g 00700 000001 600001 jd'\n😊"

    words = in_msg.split()
    count = len(words)
    word0 = words[0].lower()
    if word0 in stock.handler:
        return stock.reply_msg(words[1:], from_user)
    else:
        return tips

# 接口
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        token = 'XXX' # your token
        query = request.args
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if hashlib.sha1(s).hexdigest() == signature:
            return make_response(echostr)  

    recv_xml = ET.fromstring(request.data)
    from_user = recv_xml.find("FromUserName").text
    to_user = recv_xml.find("ToUserName").text
    in_content = recv_xml.find("Content").text

    resp_msg = u"<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"

    out_content = reply_msg(in_content)

    out_msg = resp_msg % (from_user, to_user,  str(int(time.time())), out_content)
    response = make_response(out_msg.encode('utf-8'))
    response.content_type = 'application/xml'
    return response

if __name__ == "__main__":
    #app.run()
    print (reply_msg('1'))
    msg = reply_msg(u"g 00700")
