from time import sleep

# 规定窗口宽度，高度为宽度的9/16 + 44(标题栏高度)
WIDTH_WIN = 1600
second_screen_width = 1920
second_screen_height = 1080
delta_X = 0
delta_Y	= 44 #小程序高44
def reSize(x = 0, y = 44, width = WIDTH_WIN, hwnd = 0):
	# 外部修改窗口参数接口
	global delta_X, delta_Y, WIDTH_WIN
	WIDTH_WIN = max(width, 450)
	delta_X = x
	delta_Y = y
	if hwnd > 0:
		SetWindowPos(hwnd, 1, 0, 0, WIDTH_WIN + (delta_X)*2, int(WIDTH_WIN*9/16) + delta_Y + delta_X, 2 | 16 | 64) #改大小，位置不动

# 定义鼠标事件的参数
MK_LBUTTON = 1 # 鼠标左键, 右键为2
MOUSE_MOVE = 512 #0x0001  # 鼠标移动
MOUSE_LEFTDOWN = 513 #0x0002  # 左键按下
MOUSE_LEFTUP = 514 #0x0004  # 左键释放
def bkg_click(hWnd, coord, drag = 0, delta = 0, count = 1):
	# coord:点击相对坐标元组,(x,y)
	# drag:拖动标识, 1:纵向, 2:横向
	# count:连续点击次数
	from win32.win32gui import PostMessage, GetParent, GetClassName
	if coord[0] < 1: # 坐标相对窗口比例
		x, y = int(coord[0]*WIDTH_WIN) + delta_X, int(coord[1]*(WIDTH_WIN*9/16)) + delta_Y # 坐标换算
	else: # 窗口内坐标
		x, y = int(coord[0]), int(coord[1])
	if GetClassName(hWnd) == 'Intermediate D3D Window': #无法接收鼠标事件
		hWnd = GetParent(hWnd)
		if x==479 and y==326: x -= 2 #圣域传送员修正
	while count > 0:
		lParam = x | y <<16
		PostMessage(hWnd, MOUSE_LEFTDOWN, MK_LBUTTON, lParam)
		if drag and count == 1:
			if int(drag)==1: #纵向
				lParam = x | (y + delta) <<16
			if drag==2: #横向
				lParam = (x + delta) | y <<16
			PostMessage(hWnd,MOUSE_MOVE, MK_LBUTTON, lParam)
		PostMessage(hWnd, MOUSE_LEFTUP, MK_LBUTTON, lParam)
		sleep((300 if count > 1 else 100)/1000)
		count -= 1

from win32print import GetDeviceCaps
from win32gui import SetWindowPos, GetWindowRect, GetDC
prime_screen_width = GetDeviceCaps(GetDC(0),118) #主屏横向分辨率
prime_screen_height = GetDeviceCaps(GetDC(0),117) #主屏纵向分辨率
def get_windows(XY=False):
	# 取得窗口句柄, XY为True找浏览器窗口, 否则找小程序窗口
	from win32gui import GetWindowText,  EnumWindows, FindWindowEx
	"""获取所有窗口句柄"""
	windows = []
	def enum_callback(hwnd, param):
		nonlocal windows
		title = GetWindowText(hwnd)
		if XY:
			browser = ''
			if 'XY游戏' in title:
				winInfo = {'pHwnd':hwnd, 'title':title}
				if 'Microsoft' in title:
					reSize(5, 79); browser = 'Edge'
					SetWindowPos(hwnd, 1, 0, 0, WIDTH_WIN + (delta_X+1)*2, int(WIDTH_WIN*9/16) + delta_Y + delta_X+1, 2 | 16 | 64) #改大小，位置不动
					hwnd = FindWindowEx(hwnd, None, 'Intermediate D3D Window', None)
				elif 'Google' in title:
					reSize(1, 88); browser = 'Chrome'
					SetWindowPos(hwnd, 1, 0, 0, WIDTH_WIN + (delta_X)*2, int(WIDTH_WIN*9/16) + delta_Y + delta_X, 2 | 16 | 64) #改大小，位置不动
					hwnd = FindWindowEx(hwnd, None, 'Intermediate D3D Window', None)
				elif 'Mozilla' in title:
					reSize(5, 29); browser = 'Firefox'
					SetWindowPos(hwnd, 1, 0, 0, WIDTH_WIN + (delta_X+1)*2+1, int(WIDTH_WIN*9/16) + delta_Y + delta_X+2, 2 | 16 | 64) #改大小，位置不动
				print(f'Hwnd: {hwnd}, {browser} Mode!')
				#print("Title:", title, "\nSize info:", WIDTH_WIN+delta_X*2, int(WIDTH_WIN*9/16) + delta_Y + delta_X)
				rect = dict(zip( 'left top right bottom'.split(), GetWindowRect(hwnd)))
				#rect['left']+=2*delta_X; rect['right']-=delta_X; rect['bottom']-=2*delta_X
				winInfo.update({'hWnd':hwnd, 'rect':rect, 'browser':browser})
				windows.append(winInfo)
		else:
			if title in ["龙鳞", "永恒之巅"]:
				#SetWindowLong(hwnd, GWL_EXSTYLE, WS_EX_NOACTIVATE)	# 使窗口无法获取焦点, 会使窗口无法接收键盘输入
				rect = dict(zip( 'left top right bottom'.split(), GetWindowRect(hwnd)))
				if rect['left'] < (prime_screen_width - rect['right'] + rect['left'])/2:
					windows.append({'hWnd':hwnd, 'id':0, 'title':title, 'rect':rect})
					if rect['left'] != 0:
						SetWindowPos(hwnd, 0, 0, 350, WIDTH_WIN , int(WIDTH_WIN*9/16) + delta_Y, 16 | 64) #左下角, 顶层
				elif rect['right'] <= prime_screen_width: #右上角
					windows.append({'hWnd':hwnd, 'id':1, 'title':title, 'rect':rect})
					if rect['right'] != prime_screen_width:
						SetWindowPos(hwnd, 1, prime_screen_width - rect['right'] + rect['left'], 0, WIDTH_WIN, int(WIDTH_WIN*9/16) + delta_Y, 16 | 64) #右上角
				elif rect['right'] > prime_screen_width:
					windows.append({'hWnd':hwnd, 'id':2, 'title':title, 'rect':rect})
					SetWindowPos(hwnd, 1, prime_screen_width, 0, WIDTH_WIN, int(WIDTH_WIN*9/16) + delta_Y, 16 | 64) #副屏左上角
		return True
	# EnumWindows函数枚举所有顶级窗口，并调用enum_callback函数
	EnumWindows(enum_callback, None)
	return windows

def reHwnd(left = True, XY=False):
	# 获取所有窗口句柄和浏览器标识
	wins = get_windows(XY)
	browser = ''
	if len(wins) == 1: # 窗口唯一
		winHwnd = wins[0]['hWnd']
		browser = wins[0].get('browser', 'vxx')
	elif left:
		winHwnd = list(filter(lambda x: x['rect']['left'] < (prime_screen_width - WIDTH_WIN)/2, wins))[0]['hWnd']
	else:
		winHwnd = [item for item in wins if item['rect']['left'] > (prime_screen_width - WIDTH_WIN)/2][0]['hWnd']
	return winHwnd, browser

# 窗口截图相关
import numpy as np
def screezeCap(hWnd, top = False):
	# pyscreeze只能对主屏幕窗口截图，优点在于系统适配好
	from pyscreeze import screenshot
	rect = dict(zip('left top right bottom'.split(), GetWindowRect(hWnd)))
	# 窗口截图
	if top: # 置顶
		SetWindowPos(hWnd, 0, 0, 0, 0, 0, 16 | 64) 
		sleep(0.5)
	image = None; n = 4 # 有失败可能，三次尝试
	while image is None and (n:=n-1) > 0: 
		image = np.asarray(screenshot(region=[rect['left'], rect['top'], rect['right'] - rect['left'], rect['bottom'] - rect['top']]))
	if top: # 置顶
		SetWindowPos(hWnd, -2, 0, 0, 0, 0, 16 | 64) # 下沉窗口
	return image

def dxcamCap(hWnd, top = False):
	# dxcam截图支持多个屏幕, 速度快, 兼容性欠佳
	import dxcam
	global prime_screen_width
	rect = dict(zip('left top right bottom'.split(), GetWindowRect(hWnd)))
	# 窗口截图
	camera = dxcam.create(output_idx=(0 if rect['right'] <= prime_screen_width else 1), output_color="BGR")
	image = None; n = 4 # 有失败可能，三次尝试
	while image is None and (n:=n-1) > 0:
		if rect['right'] <= prime_screen_width: #主屏
			image = camera.grab(region=(rect['left'],rect['top'], rect['right'], rect['bottom'])) #第二屏修正
		else: #第二屏
			image = camera.grab(region=(rect['left']-prime_screen_width,rect['top'],rect['right']-prime_screen_width,rect['bottom'])) #第二屏修正
			#image = image[:, :, ::-1] #反转色彩通道
	return image

if __name__ == "__main__":
	from sys import argv
	if argv[-1] == 'XY':
		wins = get_windows(XY=True)
	else:
		wins = get_windows()
	for w in wins:
		print(f'Window[{wins.index(w)}]:\tHWND:{w["hWnd"]},\tLEFT:{w["rect"]["left"]}')
