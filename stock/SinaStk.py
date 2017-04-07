# -*- coding: UTF-8 -*-

import urllib
import re
import time
from collections import OrderedDict


# 从object继承以避免可能的兼容问题
class SinaStkInfo(object):
    s_InfoTitles = {
        'us': [
            'name', 'price', 'change', 'query_date_time', 'change_ratio', 'open_price', 'day_high', 'day_low',
            'w52_high', 'w52_low', 'volume', 'd10_avg_volume', 'market_cap', 'eps', 'pe', 'unknown1',
            'beta', 'dividend', 'dividend_ratio', 'total_share', 'unknown2', 'ah_price', 'ah_change_ratio', 'ah_change',
            'ah_query_time', 'unknown3', 'last_day_close_price', 'ah_volume'
        ],
        'us_i': [
            'market_type', 'industry', 'issue_price', 'us_i_4'
        ],
        'cn': [
            'name', 'open_price', 'close_price', 'price', 'day_high', 'day_low',
            'buy_price', 'sell_price', 'volume', 'volume_cap',
            'buy_1_vol', 'buy_1_price', 'buy_2_vol', 'buy_2_price', 'buy_3_vol', 'buy_3_price', 'buy_4_vol',
            'buy_4_price',
            'sell_1_vol', 'sel_1_price', 'sell_2_vol', 'sel_2_price', 'sell_3_vol', 'sel_3_price', 'sell_4_vol',
            'sel_4_price',
            'query_date', 'query_time', 'trading_status'
        ],
        'cn_i': [
            'category', 'symbol_pinyin', 'eps', 'recent_4q_eps',
            'current_year_eps', 'net_asset_value_per_share', 'recent_5d_avg_volume_5m',
            'total_share_in_w', 'trading_share_in_w', 'trading_share_a_in_w', 'trading_share_b_in_w',
            'unit', 'annual_net_profit', 'q4_profit_sum',
            'issue_price',
            'trading_status',  # [0-无该记录 1-上市正常交易 2-未上市 3-退市]
            'recent_roe',
            'recent_revenue',
            'net_profit'
        ],
        's_cn': [
            'name', 'price', 'change', 'change_ratio', 'volume', 'volume_cap'
        ],
        'hk': [
            'english_name', 'name', 'open', 'yesterday_close', 'day_high', 'day_low',
            'price', 'change', 'change_ratio', 'sell_price', 'buy_price',
            'volume_cap', 'volume', 'pe', 'yield_ratio',
            'w52_high', 'w52_low',
            'query_date', 'query_time'
        ],
        'hk_i': [
            'hk_i_1', 'market_type', 'w52_high_bad', 'w52_low_bad',
            'hk_i_5', 'hk_i_6', 'hk_i_7', 'trading_share_hk',
            'hk_i_9', 'total_share', 'weekly_yeild_ratio',
            'hk_i_12', 'hk_i_13', 'hk_i_14',
            'trading_status',
            'hk_i_16', 'hk_i_17'
        ]
    }

    s_valueNeedToSimplify = ['market_cap', 'volume', 'volume_cap']

    s_valueIsPercentage = ['change_ratio']

    s_infoFormat = u"{symbol},{name},{price}({change_ratio}),{market_cap},{eps},{pe},{w52_low}-{w52_high},{volume}股"

    s_userTitles = [u"代码", u"名称", u"现价", u"市值", u"EPS", u"PE", u"52周变化", u"成交量"]

    def __init__(self, mkt, symbol):
        self.mkt = mkt
        self.empty_value = '0.0'
        self.symbol = symbol
        self.name = self.empty_value
        self.price = self.empty_value
        self.change_ratio = self.empty_value
        self.market_cap = self.empty_value
        self.eps = self.empty_value
        self.pe = self.empty_value
        self.w52_low = self.empty_value
        self.w52_high = self.empty_value
        self.volume = self.empty_value
        self.volume_cap = self.empty_value
        self.total_share = self.empty_value
        self.total_share_in_w = self.empty_value

    def add_info(self, info_type, info_string):
        if info_type not in self.s_InfoTitles.keys():
            return
        item_values = re.split(',', info_string)
        if len(self.s_InfoTitles[info_type]) == len(item_values):
            new_dict = {k: v for k, v in zip(self.s_InfoTitles[info_type], item_values)}
            self.__dict__.update(new_dict)
        else:
            print 'info type %s does not match expectation' % info_type

    # simplify
    def process(self):
        if self.total_share == self.empty_value and self.total_share_in_w != self.empty_value:
            self.total_share = float(self.total_share_in_w) * 10000

        if self.market_cap == self.empty_value:
            market_cap = float(self.price) * float(self.total_share)
            self.market_cap = u"%f" % market_cap

        if self.pe == self.empty_value:
            eps = float(self.eps)
            if eps > 0:
                pe = float(self.price) / eps
                self.pe = u"%.2f" % pe
            else:
                self.pe = self.empty_value

        for x in self.s_valueNeedToSimplify:
            v = float(getattr(self, x))
            if v < 100000000:
                w = v / 10000
                new_v = u"%.2f万" % w
            else:
                y = v / 100000000
                new_v = u"%.2f亿" % y
            setattr(self, x, new_v)

        for x in self.s_valueIsPercentage:
            v = float(getattr(self, x))
            new_v = u"%+.2f%%" % v
            setattr(self, x, new_v)

    def get_string(self):
        lines = []

        line = self.s_infoFormat.format(**self.__dict__)
        items = line.split(',')

        if len(items) == len(self.s_userTitles):
            lines = []
            for i in range(0, len(self.s_userTitles)):
                lines.append(u"%s: %s" % (self.s_userTitles[i], items[i].strip()))
        else:
            print 'Invalid items count. Want %d. Got %d' % (len(self.s_userTitles), len(items))
            print line

        return u"\n".join(lines)


def get_mkt_and_symbol(name):
    name = name.strip()
    mkt = ''
    symbol = name
    if name.isdigit():
        if len(name) == 5:
            mkt = 'hk'
        elif len(name) == 6:
            if name[0] == '3' or name[0] == '0':
                mkt = 'sz'
            elif name[0] == '6':
                mkt = 'sh'
    elif name[0:2].lower() in ['hk', 'sz', 'sh'] and name[2:].isdigit():
        mkt = name[0:2].lower()
        symbol = name[2:]
    else:
        mkt = 'us'
        symbol = name.lower()
    return mkt, symbol


def get_stock_details(name_list):
    info_strings = list()
    query_names = list()
    for x in name_list:
        mkt, symbol = get_mkt_and_symbol(x)
        if mkt in ['sz', 'sh']:
            query_names.append('s_%s%s' % (mkt, symbol))
            query_names.append('%s%s_i' % (mkt, symbol))
        elif mkt == 'hk':
            query_names.append('%s%s' % (mkt, symbol))
            query_names.append('%s%s_i' % (mkt, symbol))
        elif mkt == 'us':
            query_names.append('gb_%s' % symbol)
            query_names.append('gb_%s_i' % symbol)
    url = 'http://hq.sinajs.cn/?list=' + ','.join(query_names)

    # check API
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
            return info_strings

    # 有序字典
    all_stk_dict = OrderedDict()
    for line in stock_json:
        line = line.decode('GBK')
        matches = re.findall(r'.+ hq_str_(.+)=\"(.+)\";', line)
        if len(matches) != 1:
            continue

        symbol, info = matches[0]
        if len(symbol) < 3:
            continue
        # add prefix
        prefix = ''
        postfix = ''
        if symbol[0:3] == 'gb_':
            mkt = 'us'
            symbol = symbol[3:]
            if len(symbol) > 2 and symbol[-2:] == '_i':
                postfix = '_i'
                symbol = symbol[0:len(symbol) - 2]
        else:
            if symbol[0:2] == 's_':
                prefix = 's_'
                symbol = symbol[2:]
            elif len(symbol) > 2 and symbol[-2:] == '_i':
                postfix = '_i'
                symbol = symbol[0:len(symbol) - 2]

            if symbol[0:2] == 'hk':
                mkt = 'hk'
            elif symbol[0:2] in ['sz', 'sh']:
                mkt = 'cn'
            else:
                continue
        # get information
        if symbol not in all_stk_dict:
            all_stk_dict[symbol] = SinaStkInfo(mkt, symbol.upper())

        all_stk_dict[symbol].add_info(prefix + mkt + postfix, info)

    for x in all_stk_dict:
        all_stk_dict[x].process()
        info_strings.append(all_stk_dict[x].get_string())

    return u"\n------------\n".join(info_strings) if len(info_strings) > 0 else u"无信息"


handler = ['g', u"股票"]


def reply_msg(words):
    if len(words) == 0:
        return u'请输入正确的格式 g/股票（空格）股票代码'
    else:
        return get_stock_details(words)


if __name__ == '__main__':
    test = ['BABA']
    print get_stock_details(test)
