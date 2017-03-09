# -*- coding: utf-8  -*-

"""
    用户通过微信公众平台发送股票/stk+股票代码即可获得股票实时行情信息;
    支持深沪港美不同市场多支股票同时获取;
    ...v1.1
"""

import re
import hashlib
import xml.etree.ElementTree as ET

from QStk_hk import *
from SinaStk_us import *
from QStk_cn import *
from flask import Flask, request, make_response

app = Flask(__name__)

#测试
@app.route("/hello")
def hello():
    return "hello"


# 根据代码判断股票市场并请求数据
def get_stk_infos(stk_codes):
    stk_infos = list()
    error_msg = u'不支持的代码类型'

    for word in stk_codes:# 遍历用户输入代码
        if re.match(r'\d{6}', word):# 判断是否深沪市场
            if re.match(r'\A[0,3]', word):# 判断是否深圳市场
                word = 'sz' + word
                stk_infos.append(get_cn_stk_info(word))
            elif re.match(r'\A[6]', word):# 判断是否上海市场
                word = 'sh' + word
                stk_infos.append(get_cn_stk_info(word))
            else:
                stk_infos.append(error_msg)# 输出错误信息error_msg
        elif re.match(r'\d{5}', word):# 判断是否香港市场
            word = 'hk' + word
            stk_infos.append(get_hk_stk_info(word))
        elif re.match(r'([A-Za-z]+)|([A-Za-z]+\.[A-Za-z])', word):# 判断是否美国市场
            word.lower()
            stk_infos.append(get_us_stk_info(word))
        else:
            stk_infos.append(error_msg)
    return u"\n-------------------------------------------------\n".join(stk_infos)


# 判断输入信息并返回信息
def reply_msg(new_words):
    """
    传入的参数即用户输入的内容
    判断用户输入是否符合查询股票行情的关键词规则
    是则调用get_stk_infos函数返回股票信息
    否则返回提示信息tips
    """
    tips =u"📈查询股票行情请输入：\n'stk/股票（空格）股票代码'\n支持同时查询多种市场多支股票~\n如: \n'stk 00700 000001 600001 jd'\n😊"
    stk_codes = new_words.split()

    if len(stk_codes) >= 2 and (stk_codes[0] in ['stk', u"股票"]):
        stk_codes.pop(0)
        return get_stk_infos(stk_codes)
    else:
        return tips

    
# 微信公众平台接口相关设置
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
