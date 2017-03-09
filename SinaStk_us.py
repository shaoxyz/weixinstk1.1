# -*- coding: UTF-8 -*-
#
# 新浪实时股票行情数据接口获取美股数据


import urllib
import re
import time

s_oriTitles = [
    u"名称", u"现价", u"当日变化率", u"查询时间", u"当日变化", u"开盘", u"当日最高", u"当日最低",
    u"52周最高", u"52周最低", u"成交量", u"10日均成交量", u"市值", u"每股收益", u"市盈率", u"未知指标1",
    u"贝塔系数", u"股息", u"收益率", u"总股数", u"未知指标2", u"盘后价", u"盘后变化率", u"盘后变化",
    u"盘后价查询时间", u"未知指标3", u"前日收盘价", u"盘后成交量"
]


s_valueNeedToSimplify = [
    u"市值", u"成交量"
]

s_valueIsPercentage = [
    u"当日变化率"
]

s_keptInfoFormat = u"{代码} {名称} {现价}({当日变化率}) {市值} {每股收益} {市盈率} {52周最低}-{52周最高} {成交量}股"


def get_us_info_titles():
    return u"代码 名称 现价 市值 EPS PE 52周变化 成交量"


def simplify_us_values(values):
    for x in s_valueNeedToSimplify:
        if x in s_oriTitles:
            i = s_oriTitles.index(x)
            v = float(values[i])
            if v < 100000000:
                w = v / 10000
                new_v = u"%.2f万" % w
            else:
                y = v / 100000000
                new_v = u"%.2f亿" % y
            values[i] = new_v
    for x in s_valueIsPercentage:
        if x in s_oriTitles:
            i = s_oriTitles.index(x)
            new_v = values[i] + u"%"
            values[i] = new_v
    return values


def get_us_stock_details(name):
    url = 'http://hq.sinajs.cn/?list=gb_' + name

    infos = []

    try:
        stock_json = urllib.urlopen(url)
    except IOError:
        print 'IOError when access: %s. Retry!' % url
        time.sleep(0.1)
        try:
            stock_json = urllib.urlopen(url)
            time.sleep(0.02)
        except IOError:
            print 'Still got an error! Quit!'
            return infos

    for line in stock_json:
        matches = re.findall(r'.+ hq_str_gb_(.+)=\"(.+)\";', line)
        if len(matches) == 1:
            stk_symbol, stk_others = matches[0]
            item_values = re.split(',', stk_others)
            if len(s_oriTitles) == len(item_values):
                item_values = [x.decode('GBK') for x in item_values]
                item_values = simplify_us_values(item_values)
                item_dict = dict(zip(s_oriTitles, item_values))
                item_dict[u"代码"] = stk_symbol.upper()
                infos.append(s_keptInfoFormat.format(**item_dict))
    return infos


def get_us_stk_info(symbol):
    stk_info_msg = list()
    titles = get_us_info_titles().split()
    infos = get_us_stock_details(symbol)
    for info in infos:
        items = info.split()
        title_info = [u"%s: %s" % (t, i) for (t, i) in zip(titles, items)]
        stk_info_msg.append(u"\n".join(title_info))
    return u"\n".join(stk_info_msg)


if __name__ == '__main__':
    test_stk = 'jd'
#    print get_us_stk_info(test_stks)
    print get_us_stk_info(test_stk)