#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import xmltodict
import csv
import re
import calendar
import datetime


# Source: https://www.cnblogs.com/P--K/p/9723050.html
class FormatError(ValueError):
    pass


class Date(object):
    @classmethod
    def date_range(cls, start=None, end=None, periods=None, freq=None, input_format=None, out_format=None):
        """
        生成时间序列
        :param start: 序列开始时间
        :param end: 序列结束时间, 给定start时, 结束时间不包含end
        :param periods: int, 生成的时间序列长度
        :param freq: 要生成时间序列的时间间隔
        :param out_format: 是否输出格式化后的字符串, 若要输出可指定输出格式. "%Y-%m-%d %H:%M:%S"
        :param input_format: 若start或end是字符串且无法自动推断时间格式则需指定格式
        :return: [date or date_str]
        """
        start = cls.str_to_date(start, input_format)
        end = cls.str_to_date(end, input_format)
        out = []
        if start is None and end and periods:
            for i in range(periods-1):
                old, end = cls.date_replace(end, cls._freq(freq), mod="-")
                if i == 0:
                    out.append(old)
                out = [end] + out
        elif end is None and start and periods:
            for i in range(periods-1):
                old, start = cls.date_replace(start, cls._freq(freq), mod="+")
                if i == 0:
                    out.append(old)
                out.append(start)
        elif periods is None and start and end:
            i = 0
            while True:
                old, start = cls.date_replace(start, cls._freq(freq), mod="+")
                if i == 0:
                    out.append(old)
                    i += 1
                if start < end:
                    out.append(start)
                else:
                    break
        else:
            raise ValueError("start, end, periods 须且只能指定其中两个")
        if out_format is True:
            out = [str(i) for i in out]
        elif out_format is not None:
            out = [i.strftime(out_format) for i in out]
        return out

    @staticmethod
    def date_replace(date, freq=(0, )*6, mod="+"):
        timedelta = datetime.timedelta(
            days=freq[2], hours=freq[3], minutes=freq[4], seconds=freq[5])
        if mod == "+":
            if sum(freq[:2]) == 0:
                old = date
                date = date + timedelta
            elif sum(freq[2:]) == 0:
                y = date.year + freq[0] + (date.month + freq[1] - 1) // 12
                m = (date.month + freq[1] - 1) % 12 + 1
                old = date.replace(day=calendar.monthrange(
                    date.year, date.month)[1])
                date = date.replace(
                    year=y, month=m, day=calendar.monthrange(y, m)[1])
            else:
                raise ValueError(" '年月' 不能同时和 '日时分秒' 作为间隔")
        elif mod == "-":
            if sum(freq[:2]) == 0:
                old = date
                date = date - timedelta
            elif sum(freq[2:]) == 0:
                y = date.year - freq[0] + (date.month - freq[1] - 1) // 12
                m = (date.month - freq[1] - 1) % 12 + 1
                old = date.replace(day=calendar.monthrange(
                    date.year, date.month)[1])
                date = date.replace(
                    year=y, month=m, day=calendar.monthrange(y, m)[1])
            else:
                raise ValueError(" '年月' 不能同时和 '日时分秒' 作为间隔")
        else:
            raise ValueError("mod值只能是 '+' 或 '-' ")
        return old, date

    @staticmethod
    def _freq(freq=None):
        """
        设置时间间隔
        :param freq: "Y2m3d4H5M6S" 表示间隔 1年2月3日4时5分6秒
        :return: [年, 月, 日, 时, 分, 秒]
        """
        freq_ = [0] * 6
        if freq is None:
            freq_[2] = 1
            return freq_
        for n, i in enumerate(["Y", "m", "d", "H", "M", "S"]):
            r = f'((\d*){i})'
            s = re.search(r, freq)
            if s:
                freq_[n] = int(s.group(2)) if s.group(2) else 1
        return freq_

    @staticmethod
    def str_to_date(string, format_=None):
        """
        字符串转时间, 默认自动推断格式
        :param string: 时间字符串
        :param format_: 格式
        :return: 对应的时间类型, 输入非字符串则原值输出
        """
        if not isinstance(string, str):
            return string
        if format_:
            return datetime.datetime.strptime(string, format_)
        s = re.match(
            r'(\d{4})\D+(\d{1,2})\D+(\d{1,2})(?:\D+(\d{1,2}))?(?:\D+(\d{1,2}))?(?:\D+(\d{1,2}))?\D*$', string)
        if s:
            result = [int(i) for i in s.groups() if i]
            return datetime.datetime(*result)
        s = re.match(
            r'(\d{4})\D*(\d{2})\D*(\d{2})\D*(\d{2})?\D*(\d{2})?\D*(\d{2})?\D*$', string)
        if s:
            result = [int(i) for i in s.groups() if i]
            return datetime.datetime(*result)
        else:
            raise FormatError("自动推断失败, 请指定format_")


dates = Date.date_range('20150726', '20191208', freq="m1", out_format="%Y-%m-%d")

# Replace below with your own cookie data
headers = {
    'Cookie': "_uuid=24702CD3-828D-962F-6E11-1403A37C952770904infoc; buvid3=BD5D1EB6-C08D-49A1-A635-1D2048592245155814infoc; LIVE_BUVID=AUTO6115708953712608; CURRENT_FNVAL=16; stardustvideo=1; rpdid=|(kJ|~u)JYJl0J'ul~|)mlJmu; laboratory=1-1; DedeUserID=5082433; DedeUserID__ckMd5=60cee8d8fbf416c3; SESSDATA=9d6e951c%2C1578238544%2Cb65100c1; bili_jct=185da28761ce36dbb89c74b2b0bd3e18; INTVER=1; sid=9q42dtav; finger=3f3919d0; im_notify_type_5082433=0; stardustpgcv=0606"
}

base_url = "http://api.bilibili.com/x/v2/dm/history?type=1&oid=4109139&date=%s"

res = {}

for date in dates:
    url = base_url % date
    print(url)
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    p = xmltodict.parse(r.text)
    for item in p["i"]["d"]:
        info = item["@p"].split(",")
        timestamp = float(info[0])
        id = info[7]
        text = item["#text"]
        res[id] = (timestamp, text)
    print("length: " + str(len(res)))

d = []

for k,v in res.items():
    d.append({'id': k, 'timestamp': v[0], 'text': v[1]})

csv_headers = ['id', 'timestamp', 'text']

with open("res.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
    for row in d:
        writer.writerow(row)