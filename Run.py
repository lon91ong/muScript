from time import sleep, time
from datetime import datetime, timedelta
from muMod import boss_alive, common_Play as play
from wins import reHwnd
import cv2

# 几个boolean值判断状态, linesw:切线与否; vvip:特权卡状态; angel:续天使否; fen:分解与否
# yivi1: 遗址1; ugyu:圣域; annyL:安宁池左; byud1:冰霜1
opts = {'yivi1':{"bol":'1010', "ltC":[1, 0, 0], "bound":[2,3,1,0], "Role":1, "Boss":4, "coords":[(0.39,0.274), (0.666,0.652), (0.639,0.56), (0.68,0.459), (0.583,0.364)],"tsleep":[18,6.5,5,8.5]},
		'vip':{"bol":'1001', "ltC":[2, 0, 0], "black_coords":[], "black_len": 0, "bound":[1,19], "Boss":19,
			"coords":[(0.641, 0.301), (0.588, 0.34), (0.578, 0.412),(0.547, 0.316), (0.538, 0.23), (0.489, 0.314), (0.46, 0.363), (0.442, 0.466), (0.427, 0.41), (0.519, 0.464), (0.583, 0.577), (0.609, 0.472), (0.647, 0.472), (0.665, 0.53), (0.714, 0.541), (0.665, 0.628), (0.638, 0.679), (0.643, 0.81), (0.745, 0.632), (0.793, 0.572)]},
		'ugyu':{"bol":'1001', "ltC":[2, 0, 0], "Boss":15, "Level":1, "bound":[1,16],
			#"bol":'0001', "ltC":[], "Boss":1, "Level":2, "bound":[2,3,1,0],
			"coords":[(0.768, 0.671),(0.709, 0.62),(0.68, 0.483), (0.607, 0.434),(0.579, 0.301),(0.501, 0.254),(0.436, 0.282),(0.487, 0.372),(0.436, 0.282),(0.421, 0.4),(0.447, 0.532), (0.522, 0.585),(0.552, 0.716),(0.625, 0.767),(0.692, 0.739),(0.644, 0.652),(0.692, 0.739)] #圣域回环
			#"tsleep":[23,7,6,6], "coords":[(0.768, 0.671), (0.608, 0.432), (0.647, 0.427), (0.611, 0.368), (0.576, 0.306)] #圣域1
			#"tsleep":[12,6,6,6], "coords":[(0.768, 0.671), (0.708, 0.619), (0.674, 0.557), (0.64, 0.496), (0.606, 0.434)] #圣域2
			},
		'annyL':{"annyDoor":"left", "ltC":[2, 1, 0], "Boss":2, "bound":[0,1], "tsleep":[9, 9, 6], "coords":[(0.404,0.547), (0.411,0.479), (0.394,0.506)]},
		'annyR':{"annyDoor":"right", "ltC":[3, 1, 0], "bound":[0,1], "tsleep":[12,12,16], "coords":[(0.716,0.486), (0.7,0.565), (0.741,0.527)]},
		'annyT':{"annyDoor":"top", "ltC":[2, 1, 0], "Boss":2, "bound":[0,1], "tsleep":[9,8,7], "coords":[(0.57,0.29), (0.585,0.243), (0.571,0.193)]},
		'byud1':{"bol":'0001', "ltC":[2, 1, 0], "bound":[1,2], "tsleep":[22,12,12], "coords":[(0.712,0.465), (0.624,0.307), (0.58,0.191)]}}

if __name__ == "__main__":
	from sys import argv
	if argv[-1] == 'XY': #浏览器
			hwnd, browser = reHwnd(XY = True)
	else: #小程序
			hwnd, browser = reHwnd()
	# 下面map后的引号中填入挂机地图，如安宁池右：annyR
  opt={"hWnd":hwnd, "browser":browser, "map":"ugyu", "count":0, "Boss":0, "top":0, "id":0, "buff":False, "follow":False, 
	   "bufT":datetime.now()-timedelta(minutes=2), "last_coord":[0.6, 0.51], "last_time":time() - 45, "hour":24}
  opt.update(opts[opt['map']])
  opt.update(dict(zip( 'linesw vvip angel fen'.split(), map(bool, map(int, opt["bol"])) )))
  #boss_alive = cv2.imread('./Pics/MU_boss_anny.png') # MU_boss_anny 安宁池左特例
  opt.update({'buff':2}) # 奶
	while True:
		play(opt)
