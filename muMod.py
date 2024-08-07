from sys import exc_info
import cv2, numpy as np
from zipfile import ZipFile
from traceback import print_tb
from time import sleep, time, localtime, strftime
from datetime import datetime
from findimage import find_template, find_all_template
from wins import WIDTH_WIN, delta_X, delta_Y, bkg_click, dxcamCap as loc_capture #screezeCap or dxcamCap 二选一 

logLevel = 1
scaR = WIDTH_WIN/1600; scaR2 = WIDTH_WIN/865
HEIGHT_WIN = int(0.5625*WIDTH_WIN)
# 特殊作用坐标
coords_spec={"map":(0.876,0.111), "close_map":(0.118,0.109), "dragP":(0.8778, 0.71), "dragP1":(0.8778, 0.66), "checkin":[0.52, 0.803], "hand":(0.97,0.457), "pack":(0.973,0.36), "off":(0.98,0.037), "recycle1":(0.875, 0.918), "recycle2":(0.85, 0.877), "red":(0.452, 0.053), "linesw":(0.95,0.967), "bless":(0.805,0.878)}
def line_switch(hWnd, line):
	bkg_click(hWnd, coords_spec["linesw"])
	sleep(0.5)
	if line < 5:
		bkg_click(hWnd, (0.62, 0.67), (0, 120)) #向上拖动
	else:
		bkg_click(hWnd, (0.62, 0.32), (0, -120)) # 向下拖动
	sleep(0.5)
	line = (line -3) if line > 4 else (line - 1)
	bkg_click(hWnd, (0.59, 0.27 + 0.152*line)) #175 + 74 * (line -1)
	sleep(0.5)
	bkg_click(hWnd, (0.49, 0.79))
	sleep(0.5)

piZ = ZipFile('Pics.zip', 'r')
player_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_player.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
#player_img = cv2.resize(cv2.imread('./Pics/MU_player.png'), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
def getPlayer(image, coord = None):
	global player_img
	# 获取玩家坐标
	thresh1 = np.array([90, 180, 85], dtype = "uint8")  # 目标颜色阈值
	thresh2 = np.array([100, 200, 105], dtype = "uint8") 
	img_mask = cv2.inRange(image, thresh1, thresh2)
	player_mask = cv2.inRange(player_img, thresh1, thresh2)
	w, h = player_img.shape[:-1]
	for rota in range(0,360,45):
		M = cv2.getRotationMatrix2D((w/2,h/2),rota,1)
		player_loc = cv2.warpAffine(player_mask,M,(w,h))
		player_des = find_template(img_mask, player_loc)
		if player_des and player_des["confidence"] >0.7:
			break
	if player_des is not None and coord is not None:
		if coord[0] < 1:
			x, y = coord[0]*WIDTH_WIN, coord[1]*HEIGHT_WIN + delta_Y
			ts = np.sqrt(np.linalg.norm(np.array((x, y)) - np.array(player_des["result"]), ord=1))
		else:
			ts = np.sqrt(np.linalg.norm(np.array(coord) - np.array(player_des["result"]), ord=1))
		player_des.update({"ts":ts})
#	print(player_des["confidence"])
	return player_des

hand_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_hand.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
act_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_act.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
qiang_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_qiang.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
def handAct(hWnd, top = False): # 打怪状态判断
	# 返回值(怪, 抢, 手)
	global hand_img, act_img
	image = loc_capture(hWnd, top)
	hand_status = find_template(image[(int(0.459*HEIGHT_WIN)+delta_Y):(int(0.492*HEIGHT_WIN)+delta_Y), (int(0.96*WIDTH_WIN)+delta_X):(int(0.975*WIDTH_WIN)+delta_X)], hand_img)
	act_status = find_template(image[(delta_Y + 1):(int(0.065*HEIGHT_WIN)+delta_Y), (int(0.39*WIDTH_WIN)+delta_X):(int(0.451*WIDTH_WIN)+delta_X)], act_img)
	qiang_status = find_template(image, qiang_img) # 抢归属判断
	# Firefox:[195, 20, 20], Other:[20, 20, 195]
	#if logLevel: print("Red array:", image[(int(0.053*HEIGHT_WIN)+delta_Y), (int(0.453*WIDTH_WIN)+delta_X)])
	red_dis = np.linalg.norm(np.array([22,22,195]) - image[(int(0.053*HEIGHT_WIN)+delta_Y), (int(0.453*WIDTH_WIN)+delta_X)], ord=1)
	if logLevel: print(f'Act:{"None" if act_status is None else format(act_status["confidence"], ".5f")}, Red:{format(red_dis, ".3f")}, Qiang:{(qiang_status is not None) and qiang_status["confidence"]>0.7}, Hand:{("None" if (hand_status is None) else format(hand_status["confidence"], ".5f"))}')
	return ((((act_status is not None) and act_status["confidence"]>0.7) or red_dis < 10 ), ((qiang_status is not None) and qiang_status["confidence"]>0.7), ((hand_status is None) or hand_status["confidence"]<0.7))

close_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_close.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
def close_all(hWnd):
	image = loc_capture(hWnd)
	close_status = find_template(image[(delta_Y + 1):(int(0.146*HEIGHT_WIN)+delta_Y), int(0.093*WIDTH_WIN):(WIDTH_WIN -1)], close_img)
	#print("delta:", np.array([int(0.093*WIDTH_WIN)+delta_X, (delta_Y + 1)]) + np.array(close_status["result"]))
	if (close_status is not None) and (close_status["confidence"]>0.7):
		#print(close_status, np.array([80, 45]) + np.array(close_status["result"]))
		#print(f'Close all diag with {close_status["confidence"]}')
		bkg_click(hWnd, tuple(np.array([(int(0.093*WIDTH_WIN)+delta_X), (delta_Y + 1)]) + np.array(close_status["result"])))

mapls = 'vippysvexmzsbyfgdixwuilohldiuamoyblntmksfzxuyivibyudannysifgfuuiysgefzyaxisianvkjcuegodutmthlmyuufyrhvlhufmcmohwmiwumoyryihwufvkhzxw'
ugyu_img = cv2.imdecode(np.frombuffer(piZ.read('MU_ugyu.png'), np.uint8), 1)
mapPanl = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MapPanl.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
#for amap in mapls:
#	exec(f'{amap}_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read("MU_{amap}.png"), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)')

def map_check(image):
	map_result = ''
	conf = 0.5
	#if logLevel: cv2.imwrite(f'map_{delta_Y}.png', image[(int(0.099*HEIGHT_WIN)+delta_Y):(int(0.132*HEIGHT_WIN)+delta_Y), int(0.297*WIDTH_WIN):int(0.36*WIDTH_WIN)])
	map_status = find_template(image[(int(0.09*HEIGHT_WIN)+delta_Y):(int(0.14*HEIGHT_WIN)+delta_Y), int(0.29*WIDTH_WIN):int(0.35*WIDTH_WIN)], ugyu_img)
	if map_status is not None and map_status["confidence"] > conf:
		if logLevel: print(f'map:ugyu, confidence:{format(map_status["confidence"], ".5f")}')
		map_result = 'ugyu'
	else:
		thresh1 = np.array([110, 110, 110], dtype = "uint8")  # 目标颜色阈值
		thresh2 = np.array([255, 255, 255], dtype = "uint8") 
		amap_mask = cv2.inRange(image[(int(0.099*HEIGHT_WIN)+delta_Y):(int(0.132*HEIGHT_WIN)+delta_Y), int(0.297*WIDTH_WIN):int(0.344*WIDTH_WIN)], thresh1, thresh2) #三字宽
		bmap_mask = cv2.inRange(image[(int(0.099*HEIGHT_WIN)+delta_Y):(int(0.132*HEIGHT_WIN)+delta_Y), int(0.297*WIDTH_WIN):int(0.36*WIDTH_WIN)], thresh1, thresh2) #四字宽
		mapl_mask = cv2.inRange(mapPanl, thresh1, thresh2)
		match_results = find_all_template(mapl_mask, amap_mask, 0.4, 2)	#先找三字
		if len(match_results) == 1:
			y_d = int(np.floor(match_results[0]['result'][1]/scaR/59))
		elif len(match_results) > 1:
			match_result = find_template(mapl_mask, bmap_mask)	#再找四字
			if match_result is None:
				y_d = int(np.floor(match_results[1]['result'][1]/scaR/59))
			else:
				y_d = int(np.floor(match_result['result'][1]/scaR/59))
		else: # fail
			y_d = 0 #vipp
		map_result = mapls[y_d*4:(y_d+1)*4]
	return map_result

Y_list = list(range(int(30*scaR), int(1980*scaR), int(60*scaR)))
map_cls = {'vipp':0, 'ysve':1, 'xmzs':2, 'byfg':3, 'dixw1':(4, 1), 'godu':21, 'yivi1':(11, 1), 'uamo1':(7, 1), 'byud1':(12, 1), 'anny':13, 'ufyr':24, 'moyr':29, 'yihw':30}
def map_switch(hWnd, amap, browser, level = 1):
	if amap != 'ugyu':
		map_y = Y_list[map_cls[amap][0]] if type(map_cls[amap]) is list else Y_list[map_cls[amap]]
		n = 6; dis = HEIGHT_WIN
		while n:=n-1 :
			image = loc_capture(hWnd)[int(0.163*HEIGHT_WIN + delta_Y):int(0.715*HEIGHT_WIN + delta_Y), int(0.112*WIDTH_WIN + delta_X):int(0.216*WIDTH_WIN + delta_X)]
			#cv2.imwrite(f'capturePart{n}.png', image)
			match_result = find_template(mapPanl, image)
			if match_result is None:
				#bkg_click(hWnd, coords_spec["map"]) # 打开地图
				if logLevel: print('None')
				continue
			else:
				dis = int(match_result['result'][1]) - map_y
				#print(n, match_result['result'][1], dis, round(abs(dis)/HEIGHT_WIN, 3))
				if abs(dis)/HEIGHT_WIN > 0.9:
					dragDelta = int(0.139*HEIGHT_WIN) if dis > 0 else int(-0.139*HEIGHT_WIN)
				else:
					dragDelta = int(0.12*HEIGHT_WIN) if dis > 0 else int(-0.12*HEIGHT_WIN)
				if abs(dis) > 0.25 * HEIGHT_WIN:
					bkg_click(hWnd, (0.192, 0.445), (0, dragDelta)); sleep(2)
				else:
					break
		bkg_click(hWnd, (0.192, 0.445 - dis/HEIGHT_WIN)); sleep(0.5)
		if type(map_cls[amap]) is list:
			bkg_click(hWnd, (0.192,0.445+(0.05 * map_cls[amap][1]) - dis/HEIGHT_WIN)); sleep(0.5)
		if amap == 'vipp':
			sleep(9)
			bkg_click(hWnd, coords_spec["checkin"])
	else:
		map_switch(hWnd, 'godu', browser)
		sleep(2)
		bkg_click(hWnd, coords_spec["map"]); sleep(0.5) # 打开地图
		bkg_click(hWnd, coords_spec["dragP"], (0, -1*int(0.4*HEIGHT_WIN))); sleep(0.5) # 放大
		if browser in ['vxx', 'Chrome']:	#vxx:小程序
			bkg_click(hWnd, (0.575,0.51))
			bkg_click(hWnd, coords_spec["close_map"]) # 关闭地图
			sleep(3)
			bkg_click(hWnd, (0.665,0.41)) # 圣域传送员
		elif browser in ['Firefox', 'Edge']:
			bkg_click(hWnd, (0.57,0.512))
			bkg_click(hWnd, coords_spec["close_map"]) # 关闭地图
			sleep(3)
			bkg_click(hWnd, (0.6,0.35)) # 圣域传送员
		sleep(1)
		bkg_click(hWnd, (0.376,0.32+0.064*(level-2))) # 圣域2, 等差0.064
		sleep(0.5)
		bkg_click(hWnd, (0.521,0.805)) # 进入
	sleep(1)

def buff(opt):
	bkg_click(opt["hWnd"], coords_spec["hand"]); sleep(0.5) # 点击手动
	bkg_click(opt['hWnd'], coords_spec["bless"]); sleep(0.5) #bless
	clickLs = [(0.813,0.724), (0.87,0.615),(0.02,0.25),(0.09,0.18),(0.313,0.415),(0.813,0.724), (0.87,0.615)]
	for coord in clickLs:
		bkg_click(opt['hWnd'], coord)
		sleep(0.5)
	opt.update({'bufT':datetime.now()})
	bkg_click(opt["hWnd"], coords_spec["hand"])  # 点击手动

def buff2(opt):
	map_switch(opt['hWnd'], 'ufyr', opt["browser"]) #深渊
	sleep(2)
	clickLs = [(0.02,0.25), (0.136,0.19), (0.775,0.31), (0.565,0.615), (0.112,0.127)] #入队
	for coord in clickLs:
		bkg_click(opt['hWnd'], coord)
		sleep(0.5)
	sleep(3.5)
	opt.update({'bufT':datetime.now()})
	if 0 <= localtime(time()).tm_hour < 10 or 12 <= localtime(time()).tm_hour < 17:
		if opt['Level'] == 4:
			bkg_click(opt["hWnd"], (0.567,0.938)) #天使
		opt.update({'Level':5})
	else:
		if opt['Level'] == 5:
			bkg_click(opt["hWnd"], (0.567,0.938)) #恶魔
		opt.update({'Level':4})
	clickLs = [(0.02,0.25), (0.192,0.333), (0.832,0.823), (0.112,0.127)] #退队
	for coord in clickLs:
		bkg_click(opt['hWnd'], coord)
		sleep(0.5)
	if opt['turn'] > 0: opt['turn']-=1
	bkg_click(opt["hWnd"], coords_spec["map"]); sleep(0.5) # 打开地图
	map_switch(opt["hWnd"], opt["map"], opt["browser"], opt["Level"]); sleep(0.5)
	line_switch(opt["hWnd"], opt['line']); sleep(0.5)

tNai_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_tNai.png'), np.uint8), 1), None, fx=scaR2, fy=scaR2, interpolation=cv2.INTER_AREA)
def buff3(opt):
	er = 'naLan' if opt['buff'] == 3 else 'jiuXin'
	nai = {'naLan':[-65, (0.192, 0.412), 1, (0.696, 0.47), 27], 'jiuXin':[-92, (0.192, 0.637), 3, (0.628, 0.619), 13]} # ['naLan', 'jiuXin']
	bkg_click(opt['hWnd'], coords_spec["map"]); sleep(0.5) # 打开地图
	bkg_click(opt['hWnd'], (0.192, 0.5), (0, nai[er][0])) # Chrome 65
	sleep(2)
	bkg_click(opt['hWnd'], nai[er][1]); sleep(1)
	line_switch(opt['hWnd'], nai[er][2]); sleep(0.5)
	bkg_click(opt['hWnd'], coords_spec["map"]); sleep(0.5) # 打开地图
	bkg_click(opt['hWnd'], nai[er][3])
	sleep(nai[er][4])
	bkg_click(opt["hWnd"], coords_spec["close_map"]); sleep(0.5) # 关闭地图
	clickLs = [(0.02,0.25), (0.136,0.25), (0.085, 0.335), (0.775,0.31), (0.565,0.615), (0.112,0.139)] #入队
	for coord in clickLs:
		bkg_click(opt['hWnd'], coord)
		sleep(0.5)
	sleep(10)
	opt.update({'bufT':datetime.now()})
	bkg_click(opt['hWnd'], (0.12,0.182)); sleep(1)
	tNai_status = find_template(loc_capture(opt['hWnd']), tNai_img)
	#print(tNai_status)
	if tNai_status is None:
		opt.update({'Level':4})
	else:
		if 0 <= localtime(time()).tm_hour < 10: opt.update({'Level':5})
		bkg_click(opt['hWnd'], tNai_status['result']); sleep(0.5) #(0.31,0.45)
	sleep(1)
	bkg_click(opt["hWnd"], coords_spec["map"]); sleep(0.5) # 打开地图
	map_switch(opt["hWnd"], opt["map"], opt["browser"], opt["Level"]); sleep(0.5)
	line_switch(opt["hWnd"], opt['line']); sleep(0.5)

trans_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_trans.png'), np.uint8), 1), None, fx=scaR2, fy=scaR2, interpolation=cv2.INTER_AREA)
def buyYao(opt, red):
	bkg_click(opt['hWnd'], ((0.405 if red else 0.463), 0.938))
	sleep(1)
	if opt['vvip']:
		image = loc_capture(opt['hWnd'], opt['top'])
		trans_status = find_template(image, trans_img)
		opt['vvip'] = (trans_status is None)
	if not opt['vvip']:
		bkg_click(opt['hWnd'], (0.424, 0.609)) # 传送
		sleep(3)
	sleep(2)
	bkg_click(opt['hWnd'], (0.926, (0.352 if red else 0.599)), count = (20 if opt['vvip'] else 30) + (0 if red else 10))

login_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_login.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
start_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_start.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
relive_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_relive.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
yao_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_yao.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
#map_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_map.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
#bag_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_bag.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
forge_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_forge.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
#yaoCheck_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_yaoCheck.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
team_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_team.png'), np.uint8), 1), None, fx=scaR2, fy=scaR2, interpolation=cv2.INTER_AREA)
boss_alive = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_boss.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)
drag_img = cv2.resize(cv2.imdecode(np.frombuffer(piZ.read('MU_drag.png'), np.uint8), 1), None, fx=scaR, fy=scaR, interpolation=cv2.INTER_AREA)

def diagClose(opt):
	#from PIL import Image
	global close_img, vip_img, login_img, yao_img
	#cv2.namedWindow('image', 0)
	#cv2.imshow('image',image[43:140, 729:863])
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	image = loc_capture(opt['hWnd'], opt['top'])
	#Image.fromarray(image[(delta_Y + 1):(int(0.146*HEIGHT_WIN)+delta_Y), int(0.093*WIDTH_WIN):(WIDTH_WIN -1)]).show()
	close_status = find_template(image[(delta_Y + 1):(int(0.146*HEIGHT_WIN)+delta_Y), int(0.093*WIDTH_WIN):(WIDTH_WIN -1)], close_img)
	login_status = find_template(image, login_img)
	start_status = find_template(image, start_img)
	relive_status = find_template(image, relive_img)
	team_status = find_template(image, team_img)
	yao_status = find_template(image[(int(0.897*HEIGHT_WIN)+delta_Y):(int(0.98*HEIGHT_WIN)+delta_Y), int(0.37*WIDTH_WIN):int(0.486*WIDTH_WIN)], yao_img)
	if (relive_status is not None) and (relive_status["confidence"]>0.7):
		print(strftime("%m-%d %H:%M", localtime()), "Dialog relive_status!")
		bkg_click(opt['hWnd'], (0.419,0.593)) #免费复活
		sleep(2)
		bkg_click(opt['hWnd'], (0.405,0.568))
		sleep(2)
		if opt['buff'] == 2:
			bkg_click(opt['hWnd'], coords_spec["map"]) # 打开地图
			buff2(opt)
		elif opt['buff'] > 2:
			buff3(opt)
	if opt['buff']== 1 and (team_status is not None) and (team_status["confidence"]>0.7) and team_status["result"][1]/(HEIGHT_WIN+delta_Y) > 0.8: # 入队申请
		print("team request...\n", team_status["result"], team_status["confidence"])
		bkg_click(opt['hWnd'], team_status["result"])
		sleep(1)
		bkg_click(opt['hWnd'], (0.839,0.825)) # 一键同意
		sleep(1)
		bkg_click(opt['hWnd'], (0.112,0.137)) # 关闭
		sleep(0.5)
		bkg_click(opt['hWnd'], coords_spec["bless"]) #(0.511,0.509))
		sleep(2)
		buff(opt)
	if (login_status is not None) and (login_status["confidence"]>0.6): # 重新登录
		if not opt['fen'] and opt['buff']<2 and localtime(time()).tm_hour in [6, 7, 21, 22, 23]: opt['fen'] = 1
		print(strftime("%m-%d %H:%M", localtime()), "relogin after 90s ...")
		sleep(2)
		bkg_click(opt['hWnd'], (0.36, 0.346))
		sleep(90)
		bkg_click(opt['hWnd'], (0.517, 0.718))
		sleep(6)
		bkg_click(opt['hWnd'], (0.282+0.144*opt.get('Role', 0), 0.568)) # 多角色情况选第一个
		sleep(1)
		bkg_click(opt['hWnd'], (0.497, 0.86))
		sleep(20)	#资源加载较慢
		bkg_click(opt['hWnd'], (0.103, 0.126))
		sleep(2)
		bkg_click(opt['hWnd'], coords_spec["hand"])
		sleep(2)
	if (start_status is not None) and (start_status["confidence"]>0.7):
		print("Dialog Start_status!")
		bkg_click(opt['hWnd'], start_status["result"])
		sleep(10)
		bkg_click(opt['hWnd'], (0.103, 0.126))
		sleep(2)
		bkg_click(opt['hWnd'], coords_spec["hand"])
		sleep(2)
	if (close_status is not None) and (close_status["confidence"]>0.7):
		#print("Dialog close_all!")
		close_all(opt['hWnd'])
		image = loc_capture(opt['hWnd'], opt['top']) #关闭后刷新截图
	if (yao_status is not None) and (yao_status["confidence"]>0.7):
#		print('YAO:', yao_status["confidence"], yao_status["result"][0])
		if 10 < yao_status["result"][0] <100:
			buyYao(opt, yao_status["result"][0] < 50)
			bkg_click(opt['hWnd'], (0.701, 0.033)) # 关闭药店
		close_all(opt['hWnd'])
		if not opt['vvip']:
			bkg_click(opt['hWnd'], coords_spec["map"]); sleep(0.5) # 打开地图
			if opt['map'] == 'ugyu':
				map_switch(opt["hWnd"], opt["map"], opt["browser"], opt["Level"])
			else:
				map_switch(opt["hWnd"], opt["map"], opt["browser"])
			sleep(1)
			line_switch(opt['hWnd'], opt['line']) #切回原来线路
			if opt["map"] == 'vipp' and opt["turn"] > 0:
				bkg_click(opt["hWnd"], coords_spec["map"]); sleep(0.5) # 打开地图
				bkg_click(opt["hWnd"], opt["coords"][opt["turn"]])
				sleep(30)
				bkg_click(opt["hWnd"], coords_spec["close_map"]); sleep(0.3)# 关闭地图
		if opt['turn']>0:
			opt['turn']-=1
		sleep(1)

def recyFen(hWnd, count, fen=False, freq = (2, 4)):
#	image = loc_capture(hWnd)
#	bag_status = find_template(image[(delta_Y + 1):(int(0.61*HEIGHT_WIN)+delta_Y), int(0.95*WIDTH_WIN):(WIDTH_WIN -3)], bag_img)
#	print('Bag:', bag_status)
	if count % freq[0] == 0: # 回收, 每2怪
		bkg_click(hWnd, coords_spec["pack"]); sleep(2)
#		bkg_click(hWnd, (0.943,0.907)); sleep(1) # 整理
		bkg_click(hWnd, coords_spec["recycle1"]); sleep(2)
		bkg_click(hWnd, (0.865, 0.231)); sleep(0.5) # 技能书
		bkg_click(hWnd, coords_spec["recycle2"]); sleep(0.5)
		bkg_click(hWnd, coords_spec["recycle2"]); sleep(0.5)
		bkg_click(hWnd, (0.705,0.032))
		sleep(2)
	if fen and (count < 1 or count % freq[1] == 0): # 分解, 每5怪
		bkg_click(hWnd, (0.975,0.25)); sleep(1)
		image = loc_capture(hWnd)
		forge_status = find_template(image[(delta_Y + 1):(int(0.61*HEIGHT_WIN)+delta_Y), int(0.95*WIDTH_WIN):(WIDTH_WIN -3)], forge_img)
		if forge_status is not None and forge_status['confidence'] > 0.5:
			bkg_click(hWnd, (0.975,0.56)); sleep(2)	#锻造
			bkg_click(hWnd, (0.975,0.56)); sleep(1) #分解
			for fx in range(405,610,65):
				bkg_click(hWnd, (fx/1000, 0.412))
				sleep(0.5)
			if count < 6: sleep(5) # 后悔缓冲
			bkg_click(hWnd, (0.8,0.918)); sleep(0.5) #分解
			bkg_click(hWnd, (0.8,0.918)); sleep(0.5)
			bkg_click(hWnd, (0.653,0.032))
			sleep(2)

anny_door = {"right":(0.606, 0.599), "left":(0.513, 0.772), "top":(0.509, 0.601), "bottom":(0.591, 0.751)}
def common_Play(opts):
	if localtime(time()).tm_hour in [6, 21] and opts['buff']<2 and opts["map"] == 'ugyu' and opts['fen']: opts['fen'] = False
	if localtime(time()).tm_hour in [0, 8] and opts['buff']<2 and opts["map"] == 'ugyu' and not opts['fen']: opts['fen'] = True
	if opts["count"] == 0: opts.update(dict(zip('line turn'.split(), opts['ltC']))) #初始化
	try:
		diagClose(opts) # 检测界面异常
		difT = (datetime.now()-opts.get('bufT', datetime.now())).total_seconds()
		if difT > 1772 and opts['buff'] > 0:
			print(f'Buff:{opts["buff"]}   Diff Time：{int(difT)}')
			if opts['buff'] == 2:
				if difT < 1785: sleep(int(difT) - 1760)
				bkg_click(opts['hWnd'], coords_spec["map"]) # 打开地图
				buff2(opts)
				return
			elif opts['buff'] == 1:
				buff(opts)
			elif opts['buff'] > 2:
				buff3(opts)
		act_stat = handAct(opts["hWnd"], opts['top'])
		if not act_stat[0]:
			opts["count"] += 1
			sleep((2 if opts['vvip'] else 5) + 2*opts['id']) #捡东西, 特权1, 无权5
			bkg_click(opts["hWnd"], coords_spec["map"]); sleep(0.5) # 打开地图
			image = loc_capture(opts["hWnd"], opts['top'])
			map_result = map_check(image)
			if logLevel: print("Map Now:", map_result)
			if map_result != opts["map"]:
				if opts['map'] == 'ugyu':
					map_switch(opts["hWnd"], opts["map"], opts["browser"], opts["Level"])
				else:
					map_switch(opts["hWnd"], opts["map"], opts["browser"])
				sleep(1)
				line_switch(opts["hWnd"], opts["line"]) #切回原来线路
				return
			if opts["map"] in ['vipp', 'ugyu']: #圣域
				#match_result = find_template(image[(int(0.682*HEIGHT_WIN)+delta_Y):(int(0.732*HEIGHT_WIN)+delta_Y), (int(0.867*WIDTH_WIN)+delta_X):(int(0.888*WIDTH_WIN)+delta_X)], drag_img)
				#if match_result is not None:
				#	coords_spec["dragP"] = (int(match_result['result'][0]+0.867*WIDTH_WIN)+delta_X, int(match_result['result'][1]+0.682*HEIGHT_WIN)+delta_Y)
				#	if logLevel: print("Drag Coords:", coords_spec["dragP"], -1*int(0.04*HEIGHT_WIN))
				#bkg_click(opts["hWnd"], coords_spec["dragP"], (0, -1*int(0.04*HEIGHT_WIN))); sleep(0.5) # 放大
				bkg_click(opts["hWnd"], coords_spec["dragP1"], count = 4); sleep(0.5) # 放大
				image = loc_capture(opts["hWnd"], opts['top'])
			player_des = getPlayer(image)
			if opts["map"] == 'anny': #安宁池特例
				if player_des is None and opts["turn"] != 0:
					bkg_click(opts["hWnd"], coords_spec["dragP"], (0, -1*int(0.4*HEIGHT_WIN))); sleep(0.5) # 放大
					image = loc_capture(opts["hWnd"], opts['top'])
					player_des = getPlayer(image)
				if player_des is None:
					bkg_click(opts["hWnd"], (0.878, 0.312), (0, int(0.4*HEIGHT_WIN))) # 缩小
					sleep(0.3)
				elif (opts["annyDoor"] != "top" and 0.49 < player_des["result"][0]/WIDTH_WIN < 0.625) or (opts["annyDoor"] == "top" and player_des["result"][1]/HEIGHT_WIN > 0.4):
					bkg_click(opts["hWnd"], coords_spec["dragP"], (0, -1*int(0.4*HEIGHT_WIN))); sleep(0.5) # 放大
					bkg_click(opts["hWnd"], anny_door[opts["annyDoor"]])
					sleep(7.5)
					bkg_click(opts["hWnd"], (0.878, 0.312), (0, int(0.4*HEIGHT_WIN))) # 缩小
					sleep(0.5)
					bkg_click(opts["hWnd"], opts["coords"][opts["turn"]])
					sleep(0.5 if opts["annyDoor"] == "right" else opts["tsleep"][opts["turn"]])
					bkg_click(opts["hWnd"], coords_spec["close_map"]); sleep(0.3)# 关闭地图
					# 开干
					bkg_click(opts["hWnd"], coords_spec["hand"])  # 点击手动
					sleep(1)
					return
			if opts["map"] not in ['anny', 'ugyu'] and player_des: #根据距离判断序号
				min_dis = 60
				for i in range(len(opts["coords"])):
					x, y = opts["coords"][i][0]*WIDTH_WIN, opts["coords"][i][1]*HEIGHT_WIN + delta_Y
					dis = np.linalg.norm(np.array((x, y)) - np.array(player_des["result"]), ord=1)
					if dis < min_dis:
						min_dis = dis
						opts["turn"] = i
			dx = int(0.05*WIDTH_WIN); dy = int(0.1*HEIGHT_WIN)
			if opts['Boss']: #红怪
				x_boss, y_boss = int(opts["coords"][opts["Boss"]][0]*WIDTH_WIN) + delta_X, int(opts["coords"][opts["Boss"]][1]*HEIGHT_WIN) + delta_Y
				match_result = find_template(image[(y_boss-dy):(y_boss+dy), (x_boss-dx):(x_boss+dx)], boss_alive)
				if logLevel: print("Pre:", opts["bound"], opts["turn"], ("None" if match_result is None else format(match_result["confidence"], '.5f')))
				if len(opts['bound']) == 4: # 4个点来回刷, 需确定opts["tsleep"]
					if opts["turn"] in [1,4] and opts["bound"][3] > 0:
						opts["bound"][3] -= 1
					if match_result is not None and match_result["confidence"] > 0.86 and opts["bound"][3] == 0:
						opts["bound"][:2] = [1,4] # 坐标序列上下限
						opts["bound"][3] = 2 # 设置Boss数量
					elif (match_result is None or match_result["confidence"] < 0.86) and opts["bound"][3] == 0:
						opts["bound"][:2] = [2,3]
						if opts['linesw']: # 切线
							bkg_click(opts["hWnd"], coords_spec["close_map"]) # 关闭地图
							sleep(0.5)
							opts["line"] = opts["line"] +1 if opts["line"] <7 else 1
							line_switch(opts["hWnd"], opts["line"])
							opts["turn"] = 0
							sleep(0.5)
							return
					if opts["turn"] == 0:
						opts["turn"] = 2
						opts["bound"][2] = (-1 if opts["bound"][3] > 0 else 1)
						bkg_click(opts["hWnd"], opts["coords"][opts["turn"]])
						ts = 6; tn = 0
						while ts > 3 and (tn:= tn+1) < 5: # 5次循环检测还没到就跳出
							player_des = getPlayer(loc_capture(opts["hWnd"], opts['top']), opts["coords"][2])
							ts = player_des.get("ts") if player_des else (ts - 2)
							sleep((ts - 2) if ts > 3 else 0.5)
					#elif opts["turn"] == 1: # 跳过2, 毒步妖攻高
					#	opts["turn"] = 2
					#	opts["bound"][2] = 1
					#	bkg_click(opts["hWnd"], opts["coords"][3])
					#	sleep(3)
					elif not opts["bound"][0] <= opts["turn"] + opts["bound"][2] <= opts["bound"][1]:
						opts["bound"][2] = opts["bound"][2]*(-1) #切换方向
				elif opts["map"] not in ['vipp', 'ugyu']: # 2+1点
					if match_result is not None and match_result["confidence"] > 0.86:
						opts["bound"][1] = opts["Boss"] # 坐标序列上下限
					elif opts['linesw'] and opts["count"] %5 == 0: # 切线
						bkg_click(opts["hWnd"], coords_spec["close_map"]) # 关闭地图
						sleep(0.5)
						opts["line"] = opts["line"] +1 if opts["line"] <7 else 1
						line_switch(opts["hWnd"], opts["line"])
						opts["turn"] = 0
						sleep(0.5)
						return
					else:
						opts["bound"][1] = (1 if opts["map"] == 'anny' else 2)
				else: # vip turn
					if opts['linesw'] and opts["turn"] == opts["bound"][1] and not opts['follow']:
						bkg_click(opts["hWnd"], coords_spec["close_map"]) # 关闭地图
						sleep(0.5)
						opts["line"] = (2 if opts["line"] == 4 else opts["line"] +1) #23
						line_switch(opts["hWnd"], opts["line"])
						sleep(2)
						opts["turn"] = 0
						opts['ltC'][:] = [opts['line'], opts['turn']]
						sleep(0.5)
						return

			if time() - opts["last_time"] > 10: # 换点间隔10s
				if len(opts['bound']) == 4:
					opts["turn"] = opts["turn"] + opts["bound"][2]
					ts_loc = opts["tsleep"][opts["turn"]-(1 if opts["bound"][2] == 1 else 0)]
				elif  len(opts['bound']) == 2:
					ts_loc = opts["tsleep"][opts["turn"]] if opts.get("tsleep") else 0
					if opts["turn"] in [0, opts["bound"][1]] and not opts['linesw']: #头尾衔接
						opts["turn"] = 1
					elif len(opts["coords"])<=3:
						opts["turn"] = (2 if opts["bound"][1] == 2 else 0)
					else:
						if not opts['follow']:
							while opts["turn"] < opts['bound'][1]:
								x_boss, y_boss = int(opts["coords"][opts["turn"]][0]*WIDTH_WIN), int(opts["coords"][opts["turn"]][1]*HEIGHT_WIN) + delta_Y
								match_result = find_template(image[(y_boss-dy):(y_boss+dy), (x_boss-dx):(x_boss+dx)], boss_alive)
								if logLevel: print(f'Follow: {opts["follow"]}, Turn: {opts["turn"]}, {"None" if match_result is None else format(match_result["confidence"], ".5f")}')
								if match_result is None or match_result["confidence"] < 0.86:
									#if match_result is not None:print("Turn:", opts["turn"], "Conf:", match_result["confidence"])
									opts["turn"] += 1
								else:
									break
							else:
								if opts['linesw']: # 切线
									bkg_click(opts["hWnd"], coords_spec["close_map"]) # 关闭地图
									sleep(0.5)
									opts["line"] = opts["line"] +1 if opts["line"] <4 else 2
									line_switch(opts["hWnd"], opts["line"]); sleep(0.5)
									opts["turn"] = 0
									opts['ltC'][:] = [opts['line'], opts['turn']]
									return
							opts['ltC'][1] = opts['turn']
						else: #follow
							opts['turn'] = opts['ltC'][1] 
							if opts['line'] != opts['ltC'][0]: # 切线
								bkg_click(opts["hWnd"], coords_spec["close_map"]); sleep(0.5) # 关闭地图
								opts['line'] = opts['ltC'][0]
								line_switch(opts["hWnd"], opts['line']); sleep(0.5)
								return
				bkg_click(opts["hWnd"], opts["coords"][opts['turn']])
				#print("turn:", opts["turn"], "ltC_t:", opts['ltC'][1])
				if ts_loc: # 固定间隔
					sleep(ts_loc)
				else: # 无固定间隔
					tn = 0
					if opts["map"] in ['vipp', 'ugyu'] and opts["turn"] > 0:
						x0, y0 = opts["last_coord"][0]*WIDTH_WIN, opts["last_coord"][1]*HEIGHT_WIN + delta_Y
						x, y = opts["coords"][opts["turn"]][0]*WIDTH_WIN, opts["coords"][opts["turn"]][1]*HEIGHT_WIN + delta_Y
						ts = max(6, np.sqrt(np.linalg.norm(np.array((x, y)) - np.array((x0, y0)), ord=1)))
					else:
						ts = 6
					while ts > 3 and (tn:= tn+1) < 5: # 5次循环检测还没到就跳出
						player_des = getPlayer(loc_capture(opts["hWnd"], opts['top']), opts["coords"][opts["turn"]])
						ts = player_des.get("ts") if player_des else (ts - 2)
						sleep((ts - 2) if ts > 3 else 0.5)
				
				opts["last_coord"] = opts["coords"][opts["turn"]]
				opts["last_time"] = time()
				if opts["turn"] == 0 and not opts["map"] in ['anny', 'vipp']:
					opts["bound"][0] = 1
			else:
				bkg_click(opts["hWnd"], coords_spec["close_map"]) # 关闭地图
				sleep(7)
				return
			bkg_click(opts["hWnd"], coords_spec["close_map"]); sleep(0.5)# 关闭地图
			
			# 开干
			bkg_click(opts["hWnd"], coords_spec["hand"])  # 点击手动
			sleep(1)
			
			if len(opts['bound']) == 4 and opts["bound"][3] > 0 and opts["turn"] in [1,4]: opts["bound"][3] -= 1
			if opts['angel']:
				bkg_click(opts["hWnd"], (0.567,0.938)) #续天使

			recyFen(opts["hWnd"], opts["count"], opts['fen'])
		elif act_stat[0] and not act_stat[2]:
			bkg_click(opts["hWnd"], coords_spec["hand"])  # 点击手动
		if act_stat[1] and opts["turn"] < opts["bound"][1] and not opts['follow'] : #抢归属
			bkg_click(opts["hWnd"], coords_spec["map"]); sleep(0.5) # 打开地图
			if opts["map"] in ['vipp', 'ugyu']: #圣域
				#bkg_click(opts["hWnd"], coords_spec["dragP"], True, -1*int(0.04*HEIGHT_WIN)) # 放大
				bkg_click(opts["hWnd"], coords_spec["dragP1"], count = 4); sleep(0.5) # 放大
			opts["turn"] += 1
			opts["last_time"] = time() - 5
			bkg_click(opts["hWnd"], opts["coords"][opts["turn"]]); sleep(0.5)
			bkg_click(opts["hWnd"], coords_spec["close_map"]) # 关闭地图
		sleep(2)

	except KeyboardInterrupt:
		print(strftime("%m-%d %H:%M", localtime()), f'sleep 30s. Count:{opts["count"] - 1}, Fen:{opts["fen"]}')
		sleep(30)
		print('...') # going on
		return
	except:
		print("Unexpected error:", exc_info()[0:2])
		print_tb(exc_info()[2])
		pass
