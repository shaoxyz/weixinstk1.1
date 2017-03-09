# -*- coding: UTF-8 -*-
#
# 腾讯实时股票行情数据接口获取港股数据


import urllib
import re
import time


hk_oriTitles = [
    u'未知1', u'名称', u'港股代码', u'现价1', u'昨收', u'今开', u'成交量（股）1', u'未知2', u'未知3',
    u'现价2', u'未知4', u'未知5', u'未知6', u'未知7', u'未知8', u'未知9', u'未知10', u'未知11',
    u'未知12', u'现价3', u'未知13', u'未知14', u'未知15', u'未知16', u'未知17', u'未知18', u'未知19',
    u'未知20', u'未知21', u'成交量（股）2', u'日期时间', u'涨跌额', u'涨跌幅', u'最高', u'最低',
    u'现价4', u'成交量（股）3', u'成交额（元）', u'未知23', u'市盈率', u'未知24', u'未知25', u'未知26',
    u'振幅', u'市值1', u'市值2', u'英文名', u'未知29', u'52周最高', u'52周最低', u'未知30', u'未知31'
]

hk_valuesNeedToSimplify = [
    u'成交量（股）1', u'成交额（元）'
]

hk_keptInfoFormat = u'{代码},{名称},{现价1}({涨跌幅}),{成交量（股）1}股,{成交额（元）},{市盈率},{市值1}亿,{52周最低}-{52周最高}'

valuesArePercentage = [
    u'涨跌比', u'换手率', u'涨跌幅'
]


def get_hk_info_titles():
        return u'代码 名称 现价 成交量 成交额 市盈率PE 市值 52周变化'


def simplify_hk_values(values):
    for x in hk_valuesNeedToSimplify:
        if x in hk_oriTitles:
            i = hk_oriTitles.index(x)
            v = float(values[i])
            if v < 100000000:
                w = v / 10000
                new_v = u'%.2f万' % w
            else:
                w = v / 100000000
                new_v = u'%.2f亿' % w
            values[i] = new_v
    for x in valuesArePercentage:
        if x in hk_oriTitles:
            i = hk_oriTitles.index(x)
            new_v = values[i] + u"%"
            values[i] = new_v
    return values


def get_hk_stock_details(name):
    url = 'http://qt.gtimg.cn/q=r_' + name

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
        matches = re.findall(r'(\d+)=\"(.+)\";', line)
        if len(matches) == 1:
            stk_symbol, stk_others = matches[0]
            item_values = re.split('~', stk_others)
            if len(hk_oriTitles) == len(item_values):
                item_values = [x.decode('GBK') for x in item_values]
                item_values = simplify_hk_values(item_values)
                item_dict = dict(zip(hk_oriTitles, item_values))
                item_dict[u"代码"] = stk_symbol
                infos.append(hk_keptInfoFormat.format(**item_dict))
    return infos


def get_hk_stk_info(symbol):
    stk_info_msg = list()
    infos = get_hk_stock_details(symbol)
    titles = get_hk_info_titles().split()
    for info in infos:
        items = info.split(',')
        title_info = [u"%s: %s" % (t, i) for (t, i) in zip(titles, items)]
        stk_info_msg.append(u"\n".join(title_info))
    return u"\n".join(stk_info_msg)


if __name__ == '__main__':
    test_stk = 'hk00700'
#    print get_stk_info(test_stks)
    print get_hk_stk_info(test_stk)
