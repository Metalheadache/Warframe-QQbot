# -*- coding: utf-8 -*-

from nonebot import on_command, CommandSession
import os
import requests
import json

def loadDict():
    # 载入城市词库
    path = os.path.dirname(os.path.realpath(__file__))
    file = open(path + "\weatherCITY.txt", "r", encoding='UTF-8')
    itemDirc = [{},{}]
    for lines in file.readlines():
        lines = lines.rstrip("\n")
        linebar = lines.split('=')
        itemDirc[0][linebar[0]] = linebar[1]
        itemDirc[1][linebar[1]] = linebar[0]
    file.close()
    return itemDirc

# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
    # 从 Session 对象中获取城市名称（city），如果当前不存在，则询问用户
    city = session.get('city', prompt='你想查询哪个城市的天气呢？')
    # 获取城市的天气预报
    weather_report = await get_weather_of_city(city)
    # 向用户发送天气预报
    await session.send(weather_report)

@weather.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.current_key:
        session.args[session.current_key] = stripped_arg
    elif stripped_arg:
        # 如果当前没有在询问，但用户已经发送了内容，则理解为要查询的城市
        # 这种情况通常是用户直接将城市名跟在命令名后面，作为参数传入
        session.args['city'] = stripped_arg


async def get_weather_of_city(city: str) -> str:
    # 调用天气 API，并拼接成天气预报内容
    worldDict = loadDict()
    citycode = worldDict[1][city]
    url = "http://t.weather.sojson.com/api/weather/city/" + citycode
    result = requests.get(url).json()
    if result.get('status') != 200:
        print("请求出错，错误代码%d\n" % result.get('status'))
        return -1
    time = result["time"]                                    # 系统时间
    update_time = result.get("cityInfo").get("updateTime")   # 城市天气预报更新时间
    humidness = result.get("data").get("shidu")              # 获得当前湿度
    pm25 = result.get("data").get("pm25")                    # pm2.5
    pm10 = result.get("data").get("pm10")
    quality = result.get("data").get("quality")              # 空气质量
    temperature = result.get("data").get("wendu")            # 气温
    today = []                                               # 记录今天信息的列表
    today.append(time)
    today.append(update_time)
    today.append(humidness)
    today.append(pm25)
    today.append(pm10)
    today.append(quality)
    today.append(temperature)

    "天气预报更新时间：" + today[1] + "\n"
    "湿度：" + today[2] + "\n"
    "pm2.5：" + str(today[3]) + "\n"
    "pm10：" + str(today[4]) + "\n"
    "空气质量：" + today[5] + "\n"
    "气温：" + today[6]

    data = [None]*4
    sunrise = [None]*4
    high = [None]*4
    low = [None]*4
    sunset = [None]*4
    aqi = [None]*4
    fx = [None]*4
    fl = [None]*4
    type = [None]*4
    notice = [None]*4

    result_data = result["data"]["forecast"]
    dict = {}
    for i in range(0, 4):
        dict[i] = result_data[i + 1]
        data[i] = dict[i].get("data")
        sunrise[i] = dict[i].get("sunrise")
        high[i] = dict[i].get("high")
        low[i] = dict[i].get("low")
        sunset[i] = dict[i].get("sunset")
        aqi[i] = dict[i].get("aqi")
        fx[i] = dict[i].get("fx")
        fl[i] = dict[i].get("fl")
        type[i] = dict[i].get("type")
        notice[i] = dict[i].get("notice")
    
    info = []                                                 #记录未来4天信息的列表
    info.append(data)
    info.append(sunrise)
    info.append(high)
    info.append(low)
    info.append(sunset)
    info.append(aqi)
    info.append(fx)
    info.append(fl)
    info.append(type)
    info.append(notice)

    today = "\n" \
    + "天气预报更新时间：" + today[1] + "\n" + "湿度：" + today[2] + "\n" \
    + "pm2.5：" + str(today[3]) + "\n" + "pm10：" + str(today[4]) + "\n" \
    + "空气质量：" + today[5] + "\n" + "气温：" + today[6]
    
    tomorrow = "日出时间：" + str(info[1][1]) + "\n" + "最高温度：" + str(info[2][1]) + "\n" + "最低温度：" + str(info[3][1]) + "\n" + "日落时间：" + str(info[4][1]) + "\n" \
     + "空气质量指数 (AQI)：" + str(info[5][i]) + "\n" + "风向：" + str(info[6][i]) + "\n" + "风力等级：" + str(info[7][i]) + "\n" + "天气状况：" + str(info[8][i])

    return f'{city}的天气是：' + today \
    + "\n" + "\n明天的天气预测是：\n" + tomorrow