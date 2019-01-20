# -*- coding: utf-8 -*-

from nonebot import on_command, CommandSession
from urllib import request
import json
from threading import Timer
import time
import math
import random
import os

# 循环
def timerLoop(inc, updateJson):
    t = Timer(inc, updateJson)
    t.start()

# 载入词库
def loadDict():
    path = os.path.dirname(os.path.realpath(__file__))
    file = open(path + "\worldDATA.txt", "r", encoding='UTF-8')
    itemDirc = [{},{}]
    for lines in file.readlines():
        lines = lines.rstrip("﻿")
        lines = lines.rstrip("\n")
        linebar = lines.split('=')
        itemDirc[0][linebar[0]] = linebar[1]
        itemDirc[1][linebar[1]] = linebar[0]
    file.close()
    return itemDirc

# 载入紫卡词库
def loadRiven():
    path = os.path.dirname(os.path.realpath(__file__))
    rivenDict = {}
    with open(path + "\data_riven.json", "r", encoding='UTF-8') as F:
        rivenDict["\data_riven.json"] = json.loads(F.read())
    return rivenDict

# 获取JSON
def updateJson():
    url = 'http://content.warframe.com/dynamic/worldState.php'
    req = request.Request(url)
    data = request.urlopen(req).read()
    data = json.loads(data)
    del(data['Date'])
    del(data['WorldSeed'])
    del(data['Version'])
    del(data['MobileVersion'])
    del(data['BuildLabel'])
    del(data['Events'])
    del(data['Goals'])
    del(data['GlobalUpgrades'])
    del(data['FlashSales'])
    del(data['HubEvents'])
    del(data['NodeOverrides'])
    del(data['BadlandNodes'])
    del(data['PrimeAccessAvailability'])
    del(data['PrimeVaultAvailabilities'])
    del(data['LibraryInfo'])
    del(data['PVPChallengeInstances'])
    del(data['PersistentEnemies'])
    del(data['PVPAlternativeModes'])
    del(data['PVPActiveTournaments'])
    del(data['ProjectPct'])
    del(data['ConstructionProjects'])
    del(data['TwitchPromos'])
    '''
    剩余八个参数：
    Time              > 时间
    Alerts            > 警报
    Sorties           > 突击
    SyndicateMissions > 集团任务
    ActiveMissions    > 裂隙
    Invasions         > 入侵
    VoidTraders       > 虚空商人
    DailyDeals        > 每日折扣
    '''
    global worldData
    global warList
    global lastAlerts
    global thisAlerts
    # 存储上一次警报
    try:
        lastAlerts = worldData['Alerts']
    except:
        lastAlerts = []
    # 存储worldstate数据
    worldData = data
    # 存储本次警报
    thisAlerts = data['Alerts']
    timerLoop(30, updateJson)

def TimeConversion(seconds):
	if seconds <= 0:
		return 'N/A'
	d = 0
	if seconds >= 86400:
		d = math.floor(seconds / 86400)
	seconds = seconds % 86400
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	if d > 0:
		return '%d 天 %02d 时 %02d 分 %02d 秒' % (d, h, m, s)
	if h > 0:
		return '%d 时 %02d 分 %02d 秒' % (h, m, s)
	else:
		return '%02d 分 %02d 秒' % (m, s)

@on_command('sortie', aliases=('突击', '每日'))
# 突击
async def Sorties(session: CommandSession):
    updateJson()
    output = str(worldDict[0][worldData['Sorties'][0]['Boss']]) + ''
    for i in worldData['Sorties'][0]['Variants']:
        try:
            output = output + '\n\n地点: ' + worldDict[0][i['node']]
        except:
            output = output + '\n\n地点: ' + i['node']
        output = output + '\n任务: ' + worldDict[0][i['missionType']]
        output = output + '\n状态: ' + worldDict[0][i['modifierType']]
    await session.send(output)

@on_command('alert', aliases=('警报', '目前警报'))
# 警报
async def Alerts(session: CommandSession):
    updateJson()
    output = '现在有警报 ' + str(len(worldData['Alerts'])) + ' 个：'
    for i in worldData['Alerts']:
        try: 
            output = output + '\n\n' + worldDict[0][i['MissionInfo']['location']] + ' 等级 ' + str(i['MissionInfo']['minEnemyLevel']) + '-' + str(i['MissionInfo']['maxEnemyLevel'])
        except:
            output = output + '\n\n' + i['MissionInfo']['location'] + ' 等级 ' + str(i['MissionInfo']['minEnemyLevel']) + '-' + str(i['MissionInfo']['maxEnemyLevel'])
        output = output + '\n任务: ' + worldDict[0][i['MissionInfo']['missionType']] + ' - ' + worldDict[0][i['MissionInfo']['faction']]
        if 'countedItems' in i['MissionInfo']['missionReward']:
            item = i['MissionInfo']['missionReward']['countedItems'][0]['ItemType'].split('/')
            try: 
                item = worldDict[0][item[len(item)-1]]
            except:
                item = item[len(item)-1]
            item = item + str(i['MissionInfo']['missionReward']['countedItems'][0]['ItemCount']) + ' + 现金 ' + str(i['MissionInfo']['missionReward']['credits'])
        elif 'items' in i['MissionInfo']['missionReward']:
            item = i['MissionInfo']['missionReward']['items'][0].split('/')
            try: 
                item = worldDict[0][item[len(item)-1]]
            except:
                item = item[len(item)-1]
            item = item + ' + 现金 ' + str(i['MissionInfo']['missionReward']['credits'])
        else:
            item = '现金 ' + str(i['MissionInfo']['missionReward']['credits'])
        output = output + '\n奖励: ' + item
        timeLeft = int(int(i['Expiry']['$date']['$numberLong'])/1000) - time.time()
        minute = int(timeLeft/60)
        sec = int(timeLeft - minute*60)
        output = output + '\n剩余时间: ' + str(minute) + ' 分钟 ' + str(sec) + ' 秒 '
    await session.send(output)

@on_command('js', aliases=('奸商', '虚空商人'))
# 虚空商人
async def VoidTraders(session: CommandSession):
    updateJson()
    timeLeft = int(worldData['VoidTraders'][0]['Activation']['$date']['$numberLong'])/1000 - int(worldData['Time'])
    if timeLeft > 0:
        day = int(timeLeft/86400)
        hour = int(timeLeft/3600 - day*24)
        minute = int(timeLeft/60 - hour*60 - day*1440)
        output = '龙玉涛翻了翻生死簿\n奸商还剩：\n' + str(day) + ' 天 ' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 就要来杀你妈啦！'
    else:
        timeLeft = int(worldData['VoidTraders'][0]['Expiry']['$date']['$numberLong'])/1000 - int(worldData['Time'])
        day = int(timeLeft/86400)
        hour = int(timeLeft/3600 - day*24)
        minute = int(timeLeft/60 - hour*60 - day*1440)
        output = '龙玉涛翻了翻生死簿\n奸商还剩：\n' + str(day) + ' 天 ' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 就要跑啦！'
    await session.send(output)

@on_command('voidtrader', aliases=('虚空', 'baro'))
# 虚空商人
async def get_voidtrader(session: CommandSession):
    updateJson()
    output = ''
    if float(worldData['VoidTraders'][0]['Activation']['$date']['$numberLong'])/1000 - time.time() < 0 and float(worldData['VoidTraders'][0]['Expiry']['$date']['$numberLong'])/1000 - time.time() > 0:
        inventory = worldData['VoidTraders'][0]['Manifest']
        output = '奸商已到达 {}，还有 {} 就要离开了。\n本次携带的物品是：'.format(worldDict[0][worldData['VoidTraders'][0]['Node']], TimeConversion(float(worldData['VoidTraders'][0]['Expiry']['$date']['$numberLong'])/1000 - time.time()))
        for item in inventory:
            try:
                output = output + '\n物品：{} 虚空币：{} 现金：{}'.format(worldDict[0][item['ItemType']], item['PrimePrice'], item['RegularPrice'])
            except:
                output = output + '\n物品：{} 虚空币：{} 现金：{}'.format(item['ItemType'], item['PrimePrice'], item['RegularPrice'])
    else:
        output = '奸商还在路上，将于 {} 后到达 {}。'.format(TimeConversion(float(worldData['VoidTraders'][0]['Activation']['$date']['$numberLong'])/1000 - time.time()), worldDict[0][worldData['VoidTraders'][0]['Node']])
    await session.send(output)


@on_command('cetus', aliases=('地球平原', '平原时间', '希图斯'))
# 地球平原时间
async def CetusTime(session: CommandSession):
    updateJson()
    timeNow = int(time.time() - 1513450500)
    timeNow = timeNow - int(timeNow/9000)*9000
    if timeNow - 6000 < 0 : 
        timeLeft = int(6000 - timeNow)
        hour = int(timeLeft/3600)
        minute = int(timeLeft/60 - hour * 60)
        sec = int(timeLeft - minute*60 - hour * 3600)
        output = '现在是平原的白天\n\n还剩 ' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 ' + str(sec) + ' 秒 Boss就要出来了'
    elif timeNow - 3000 >= 0 : 
        timeLeft = int(9000 - timeNow)
        hour = int(timeLeft/3600)
        minute = int(timeLeft/60 - hour*60)
        sec = int(timeLeft - minute*60 - hour * 3600)
        output = '晚上啦，该去打Boss啦\n\n还剩 ' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 ' + str(sec) + ' 秒 天就要亮了'
    await session.send(output)

@on_command('Fortuna', aliases=('平原天气', '金星平原'))
# 金星平原天气
async def FortunaTime(session: CommandSession):
	weather_cycle = ''
	# 1541837628 and a 36 sec delay
	cycle_remaining = 1600 - ((time.time() - 1541837628 - 36) % 1600)
	if cycle_remaining > 1200:
		weather_cycle = '奥布山谷当前天气温暖，将在' + \
			TimeConversion(cycle_remaining - 1200) + '后转为寒冷。'
	elif cycle_remaining > 800:
		weather_cycle = '奥布山谷当前天气寒冷，将在' + \
			TimeConversion(cycle_remaining - 800) + '后转为刺骨，' + \
			TimeConversion(cycle_remaining) + '后转为温暖。'
	elif cycle_remaining > 333:
		weather_cycle = '奥布山谷当前天气刺骨，将在' + \
			TimeConversion(cycle_remaining - 333) + '后转为寒冷，' + \
			TimeConversion(cycle_remaining) + '后转为温暖。'
	else:
		weather_cycle = '奥布山谷当前天气寒冷，将在' + TimeConversion(cycle_remaining) + '后转为温暖。'
	await session.send(weather_cycle)

@on_command('invasions', aliases=('入侵', '入侵状况'))
# 入侵
async def Invasions(session: CommandSession):
    updateJson()
    output = '现在的入侵是：'
    for i in worldData['Invasions']:
        if i['Completed'] == 1:
            continue
        inv_vs_infestation = True if i['DefenderMissionInfo']['faction'] == 'FC_INFESTATION' else False
        goal_perc = (1 + (float(i['Count']) / float(i['Goal']))) * (100 if inv_vs_infestation else 50)
        try:
            eta_finish = (int(i['Goal']) - abs(int(i['Count']))) * ((time.time() - float(i['Activation']['$date']['$numberLong']) / 1000) / abs(int(i['Count'])))
        except:
            eta_finish = 0
        if eta_finish > 0:
            day = int(eta_finish/86400)
            hour = int(eta_finish/3600 - day*24)
            minute = int(eta_finish/60 - hour*60 - day*1440)
            
        atk_faction = i['DefenderMissionInfo']['faction']
        def_faction = i['AttackerMissionInfo']['faction']
        
        output = output + '\n' + '地点：' + worldDict[0][i['Node']] + '\n'
        output = output + '阵营：' + worldDict[0][atk_faction] + ' vs ' + worldDict[0][def_faction]
        output = output + ' (' + worldDict[0][i['LocTag']] + ') '
        output = output + '\n' + '进度：' + '%.2f%%' % goal_perc + '\n预计结束时间：' + str(day) + ' 天 ' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 '

        atk_reward = worldDict[0][i['AttackerReward']['countedItems'][0]['ItemType']] if 'countedItems' in i['AttackerReward'] else ''
        atk_reward_q = ' x ' + str(i['AttackerReward']['countedItems'][0]
                                    ['ItemCount']) if 'countedItems' in i['AttackerReward'] else ''
        def_reward = worldDict[0][i['DefenderReward']['countedItems'][0]['ItemType']] if 'countedItems' in i['DefenderReward'] else ''
        def_reward_q = ' x ' + str(i['DefenderReward']['countedItems'][0]
                                    ['ItemCount']) if 'countedItems' in i['DefenderReward'] else ''
    
        if inv_vs_infestation:
            output = output + '\n奖励：' + def_reward + def_reward_q + '\n'
        else:
            output = output + '\n奖励：' + atk_reward + atk_reward_q + ' vs ' + def_reward + def_reward_q + '\n'
    await session.send(output)

@on_command('fissures', aliases=('裂缝', '裂隙'))
# 裂缝
async def Fissures(session: CommandSession):
    updateJson()
    output = '现在的虚空裂缝有：\n'
    fissure_sorted = {
        'VoidT1': [],
        'VoidT2': [],
        'VoidT3': [],
        'VoidT4': []
    }
    for i in worldData['ActiveMissions']:
        fissure_sorted[i['Modifier']].append(i)
    for i in fissure_sorted['VoidT1']:
        eta_finish = float(i['Expiry']['$date']['$numberLong']) / 1000 - time.time()
        if eta_finish > 0:
            hour = int(eta_finish/3600)
            minute = int(eta_finish/60 - hour*60)
            seconds = int(eta_finish - minute*60 - hour*3600)
        output = output + '\n古纪(T1)：' + worldDict[0][i['Node']] + ' | ' + worldDict[0][i['MissionType']]
        output = output + '\n时限：' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 ' + str(seconds) + ' 秒 \n'

    for i in fissure_sorted['VoidT2']:
        eta_finish = float(i['Expiry']['$date']['$numberLong']) / 1000 - time.time()
        if eta_finish > 0:
            hour = int(eta_finish/3600)
            minute = int(eta_finish/60 - hour*60)
            seconds = int(eta_finish - minute*60 - hour*3600)
        output = output + '\n前纪(T2)：' + worldDict[0][i['Node']] + ' | ' + worldDict[0][i['MissionType']]
        output = output + '\n时限：' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 ' + str(seconds) + ' 秒 \n'

    for i in fissure_sorted['VoidT3']:
        eta_finish = float(i['Expiry']['$date']['$numberLong']) / 1000 - time.time()
        if eta_finish > 0:
            hour = int(eta_finish/3600)
            minute = int(eta_finish/60 - hour*60)
            seconds = int(eta_finish - minute*60 - hour*3600)
        output = output + '\n中纪(T3)：' + worldDict[0][i['Node']] + ' | ' + worldDict[0][i['MissionType']]
        output = output + '\n时限：' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 ' + str(seconds) + ' 秒 \n'

    for i in fissure_sorted['VoidT4']:
        eta_finish = float(i['Expiry']['$date']['$numberLong']) / 1000 - time.time()
        if eta_finish > 0:
            hour = int(eta_finish/3600)
            minute = int(eta_finish/60 - hour*60)
            seconds = int(eta_finish - minute*60 - hour*3600)
        output = output + '\n后纪(T4)：' + worldDict[0][i['Node']] + ' | ' + worldDict[0][i['MissionType']]
        output = output + '\n时限：' + str(hour) + ' 小时 ' + str(minute) + ' 分钟 ' + str(seconds) + ' 秒 \n'
    await session.send(output)

# 紫卡模块
# 紫卡数据
rivenDict = loadRiven()
riven_type = {
	'Melee': '近战',
	'Rifle': '步枪',
	'Pistol': '手枪',
	'Shotgun': '霰弹枪',
	'Zaw': 'Zaw',
	'Kitgun': 'Kitgun'
}
riven_data = {}
riven_weapons = {}
for k in riven_type:
    riven_data[k] = {
        'dispo': {},
        'buff': {},
        'prefix': {},
        'suffix': {},
        'curse': {}
    }
    for weapon in rivenDict["\data_riven.json"][k]['Rivens']:
        riven_data[k]['dispo'][weapon['name']] = weapon['disposition']
        riven_weapons[weapon['name']] = k
    for buff in rivenDict["\data_riven.json"][k]['Buffs']:
        riven_data[k]['buff'][buff['text']] = buff['value']
        riven_data[k]['prefix'][buff['text']] = buff['prefix']
        riven_data[k]['suffix'][buff['text']] = buff['suffix']
    for curse in rivenDict["\data_riven.json"][k]['Buffs']:
        if 'curse' in curse:
            riven_data[k]['curse'][curse['text']] = curse['value']

def riven_details(weapon, buffs, has_curse, simulate=0):
    if weapon in riven_weapons:
        curr_dispo = riven_data[riven_weapons[weapon]]['dispo']
        curr_buff = riven_data[riven_weapons[weapon]]['buff']
        curr_curse = riven_data[riven_weapons[weapon]]['curse']
        curr_prefix = riven_data[riven_weapons[weapon]]['prefix']
        curr_suffix = riven_data[riven_weapons[weapon]]['suffix']
    else:
        return ''
    riven_info = ''
    rand_coh = [0, 0, 0, 0]
    for i in range(0, 3):
        rand_coh[i] = random.random()*0.2+0.9
    rand_coh.sort(reverse=True)
    rand_coh[3] = random.random()*0.2+0.9
    if buffs == 2:
        if has_curse:
            dispo = curr_dispo[weapon] * 1.25
            dispo = dispo * 0.66 * 1.5
            buffs = random.sample(list(curr_buff), 2)
            temp_curr_curse = list(curr_curse)
            for buff in buffs:
                try:
                    temp_curr_curse.remove(buff)
                except:
                    pass
            curse = random.sample(temp_curr_curse, 1)
            riven_info = weapon + ' ' + curr_prefix[buffs[0]] + curr_suffix[buffs[1]].lower() + '\n' + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
                + buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']'\
                + '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']'\
                + '\n' + curse[0].replace('|val|', str(-1*round(rand_coh[2]*curr_curse[curse[0]]*curr_dispo[weapon]
                                                                * 1.5*0.33, 2))) + ' [' + riven_rank(round((rand_coh[2] - 1)*100, 2)) + ']'
        else:
            dispo = curr_dispo[weapon]  # 裂罅倾向
            dispo = dispo * 0.66 * 1.5  # 2buff，无负，按照0.66，1.5紫卡系数
            buffs = random.sample(list(curr_buff), 2)  # 下限系数0.9，上限系数1.1
            riven_info = weapon + ' ' + curr_prefix[buffs[0]] + curr_suffix[buffs[1]].lower() + '\n' + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
                + buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']' \
                + '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))
                                            ) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']'
    elif buffs == 3:
        if has_curse:
            dispo = curr_dispo[weapon] * 1.25
            dispo = dispo * 0.5 * 1.5
            buffs = random.sample(list(curr_buff), 3)
            temp_curr_curse = list(curr_curse)
            for buff in buffs:
                try:
                    temp_curr_curse.remove(buff)
                except:
                    pass
            curse = random.sample(temp_curr_curse, 1)
            riven_info = weapon + ' ' + curr_prefix[buffs[0]] + '-' + curr_prefix[buffs[1]].lower() + curr_suffix[buffs[2]].lower() + '\n' + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
                + buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']' \
                + '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']' \
                + '\n' + buffs[2].replace('|val|', str(round(rand_coh[2]*curr_buff[buffs[2]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[2] - 1)*100, 2)) + ']' \
                + '\n' + curse[0].replace('|val|', str(-1*round(rand_coh[3]*curr_curse[curse[0]]*curr_dispo[weapon]
                                                                * 1.5*0.5, 2))) + ' [' + riven_rank(round((rand_coh[3] - 1)*100, 2)) + ']'
        else:
            dispo = curr_dispo[weapon]
            dispo = dispo * 0.5 * 1.5
            buffs = random.sample(list(curr_buff), 3)
            riven_info = weapon + ' ' + curr_prefix[buffs[0]] + '-' + curr_prefix[buffs[1]].lower() + curr_suffix[buffs[2]].lower() + '\n' + riven_dispo_icon(curr_dispo[weapon]) + '\n' \
                + buffs[0].replace('|val|', str(round(rand_coh[0]*curr_buff[buffs[0]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[0] - 1)*100, 2)) + ']' \
                + '\n' + buffs[1].replace('|val|', str(round(rand_coh[1]*curr_buff[buffs[1]]*dispo, 2))) + ' [' + riven_rank(round((rand_coh[1] - 1)*100, 2)) + ']' \
                + '\n' + buffs[2].replace('|val|', str(round(rand_coh[2]*curr_buff[buffs[2]]*dispo, 2))
                                            ) + ' [' + riven_rank(round((rand_coh[2] - 1)*100, 2)) + ']'
    return riven_info

def riven_rank(perc):
	rank = ''
	if 9.5 < perc <= 10:
		rank = 'SSS'
	elif 9 < perc <= 9.5:
		rank = 'SS'
	elif 6 < perc <= 9:
		rank = 'S'
	elif 2 < perc <= 6:
		rank = 'A'
	elif -2 < perc <= 2:
		rank = 'B'
	elif -6 < perc <= -2:
		rank = 'C'
	elif -10 <= perc <= -6:
		rank = 'D'
	else:
		rank = '?'
	return rank

def riven_dispo_icon(dispo):
	text = ''
	if dispo > 1.3:
		text = '●●●●●'
	elif 1.1 < dispo <= 1.3:
		text = '●●●●○'
	elif 0.9 <= dispo <= 1.1:
		text = '●●●○○'
	elif 0.7 <= dispo < 0.9:
		text = '●●○○○'
	elif dispo < 0.7:
		text = '●○○○○'
	else:
		text = '?'
	return ('%s(%.2f)' % (text, dispo))

@on_command('getriven', aliases=('模拟开卡', '模拟开紫卡'))
# 紫卡函数
async def get_riven_info(session: CommandSession):
    riven_info = ''
    prefix = ''
    weapon = random.choices(
        population = ['Melee', 'Rifle', 'Pistol', 'Shotgun', 'Zaw', 'Kitgun'],
        weights = [8.14, 6.79, 7.61, 1.36, 2.0, 2.0],
        k=1
    ).pop()
    prefix = '你放弃了今日的传核，获得了一张%s裂罅Mod并开出了：\n' % (riven_type[weapon])
    riven_info = riven_details(random.sample(list(riven_data[weapon]['dispo']), 1)[0], random.randint(2, 3), random.randint(0, 1))
    output = prefix + riven_info
    await session.send(output)

worldDict = loadDict()
worldData = {}
warList = []
lastAlerts = []
thisAlerts = []
updateJson()