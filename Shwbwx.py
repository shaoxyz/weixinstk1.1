# -*- coding: utf-8  -*-
#
# noinspection PyUnresolvedReferences
"""
    用户通过微信公众平台发送股票/stk+股票代码即可获得股票实时行情信息;
    支持深沪港美不同市场多支股票同时获取;
    ...v1.0版
    reply_msg待优化..
"""
import re
import hashlib
import xml.etree.ElementTree as ET

from QStk_hk import *
from SinaStk_us import *
from QStk_cn import *
from flask import Flask, request, make_response

app = Flask(__name__)


@app.route("/hello")
def hello():
    return "hello"


def reply_msg(s_words):
    x = 0
    y = 1
    new_words = list()

    stk_msgs = list()

    tips = u"请输入正确的格式：'stk/股票（空格）股票代码\
        支持同时查询多种市场多支股票；\
        如: 输入'stk 00700 000001 600001 jd'：)"
    if s_words == 'hi':
        return 'hi~'
    else:
        words = s_words.split()
        if len(words) >= 2 and (words[0] in ['stk', u"股票"]):
            while x <= len(words) and (y < len(words)):
                if re.match(r'\d{6}', words[y]):
                    if re.match(r'\A[0,3]', words[y]):
                        new_words.append('sz' + words[y])
                        stk_msgs.append(get_cn_stk_info(new_words[x]))
                    elif re.match(r'\A[6]', words[y]):
                        new_words.append('sh' + words[y])
                        stk_msgs.append(get_cn_stk_info(new_words[x]))
                elif re.match(r'\d{5}', words[y]):
                    new_words.append('hk' + words[y])
                    stk_msgs.append(get_hk_stk_info(new_words[x]))
                elif re.match(r'(\w)+|(\w)+\.(\w)', words[y]):
                    new_words.append(words[y].lower())
                    stk_msgs.append(get_us_stk_info(new_words[x]))
                else:
                    return tips
                x += 1
                y = x+1
#            return u'\n'.join(stk_msgs)
            return u"\n-------------------------------------------------\n".join(stk_msgs)
        else:
            return tips


@app.route('/weixinstk', methods=['GET', 'POST'])
def weixinstk():
    if request.method == 'GET':
        token = 'ShawlibTest666'  # your token
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
    print type(in_content)

    resp_msg = u"<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"


    out_content = reply_msg(in_content)

    out_msg = resp_msg % (from_user, to_user,  str(int(time.time())), out_content)
    response = make_response(out_msg)
    response.content_type = 'application/xml'
    return response


if __name__ == "__main__":
#    app.run()
    print 'ok~'