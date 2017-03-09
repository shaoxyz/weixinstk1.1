# -*- coding: UTF-8 -*-
#
# 腾讯实时股票行情数据接口获取深沪数据


import urllib
import re
import time

cn_oriTitles = [
    u'未知', u'名称', u'代码', u'现价', u'昨收', u'今开', u'成交量1', u'外盘', u'内盘', u'买一',
    u'买一量', u'买二', u'买二量', u'买三', u'买三量', u'买四', u'买四量', u'买五', u'买五量', u'卖一',
    u'卖一量', u'卖二', u'卖二量', u'卖三', u'卖三量', u'卖四', u'卖四量', u'卖五', u'卖五量',
    u'最近逐笔成交', u'时间', u'涨跌', u'涨跌比', u'最高', u'最低', u'价格-成交量-成交额', u'成交量2',
    u'成交额', u'换手率', u'市盈率', u'未知2', u'最高', u'最低', u'振幅', u'流通市值', u'总市值',
    u'市净率', u'涨停价', u'跌停价', u'未知3'
]

cn_valueNeedToConvert_1 = [
    u'成交量1',
]

cn_valueNeedToConvert_2 = [
    u'成交额'
]

cn_valueIsPercentage = [
    u'涨跌比', u'换手率'
]

cn_keptInfoFormat = u'{代码},{名称},{现价}({涨跌比}),{成交量1},{成交额},{总市值}亿,{市盈率},{市净率},{换手率}'


def get_cn_info_titles():
    return u'代码 名称 现价 成交量 成交额 市值 市盈率PE 市净率PB 换手率'


def simplify_cn_values(values):
    for x in cn_valueNeedToConvert_1:
        if x in cn_oriTitles:
            i = cn_oriTitles.index(x)
            v = float(values[i])
            if v > 10000:
                w = v / 10000
                new_v = u"%.2f万手" % w
            else:
                new_v = u"%.2f手" % v
            values[i] = new_v
    for x in cn_valueNeedToConvert_2:
        if x in cn_oriTitles:
            i = cn_oriTitles.index(x)
            v = float(values[i])
            if v > 10000:
                w = v / 10000
                new_v = u"%.2f亿" % w
            else:
                new_v = u"%.2f万" % v
            values[i] = new_v
    for x in cn_valueIsPercentage:
        if x in cn_oriTitles:
            i = cn_oriTitles.index(x)
            new_v = values[i] + u"%"
            values[i] = new_v
    return values


def get_cn_stock_details(name):
    url = 'http://qt.gtimg.cn/q=' + name

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
        matches = re.findall(r'(\d*)=\"(.+)\";', line)
        if len(matches) == 1: 
            stk_symbol, stk_others = matches[0]
            item_values = re.split('~', stk_others)
            if len(cn_oriTitles) == len(item_values):
                item_values = [x.decode('GBK') for x in item_values]
                item_values = simplify_cn_values(item_values)
                item_dict = dict(zip(cn_oriTitles, item_values))
                item_dict[u"代码"] = stk_symbol
                infos.append(cn_keptInfoFormat.format(**item_dict))
    return infos


def get_cn_stk_info(symbol):
    stk_info_msg = list()
    titles = get_cn_info_titles().split()
    infos = get_cn_stock_details(symbol)
    for info in infos:
        items = info.split(',')
        title_info = [u"%s: %s" % (t, i) for (t, i) in zip(titles, items)]
        stk_info_msg.append(u"\n".join(title_info))
    return u"\n".join(stk_info_msg)


if __name__ == '__main__':
    test_stks = 'sz000002'
    print get_cn_stk_info(test_stks)
