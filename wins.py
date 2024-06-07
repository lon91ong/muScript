#from ctypes import byref #,windll
#from ctypes.wintypes import RECT
from time import sleep
#from ctypes import WinDLL
#windll.user32.LockSetForegroundWindow(1) 
#user32 = WinDLL('user32', use_last_error=True)
#user32.LockSetForegroundWindow(1) # 禁止抢焦点

# 规定窗口宽度，高度为宽度的9/16 + 44
WIDTH_WIN = 832
delta_X = 0
delta_Y	= 44
def reSize(x = 0, y = 44, width = WIDTH_WIN, hwnd = 0):
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
def bkg_click(hWnd, coord, drag = False, delta = 0, count = 1):
	from win32.win32gui import PostMessage, GetParent, GetClassName #, GetForegroundWindow, SetForegroundWindow #, SendMessage, FindWindowEx
#	foreWnd = user32.GetForegroundWindow()
#	print("ForegroundWindowHandle:", foreWnd)
#	user32.LockSetForegroundWindow(1) # 禁止抢焦点
	if coord[0] < 1: # 坐标相对窗口比例
		x, y = int(coord[0]*WIDTH_WIN) + delta_X, int(coord[1]*(WIDTH_WIN*9/16)) + delta_Y # 坐标换算
	else: # 窗口内坐标
		x, y = int(coord[0]), int(coord[1])
#	child_hWnd = FindWindowEx(hWnd,None,'Chrome_RenderWidgetHostHWND', None)
	if GetClassName(hWnd) == 'Intermediate D3D Window': #无法接收鼠标事件
		hWnd = GetParent(hWnd)
		#print(f'x:{x}, y:{y}')
		if x==479 and y==326: x -= 2 #圣域传送员修正
	while count > 0:
		lParam = x | y <<16
#		SendMessage(child_hWnd, MOUSE_LEFTDOWN, MK_LBUTTON, lParam)
		PostMessage(hWnd, MOUSE_LEFTDOWN, MK_LBUTTON, lParam)
		if drag:
			lParam = x | (y + delta) <<16
#			SendMessage(child_hWnd,MOUSE_MOVE, MK_LBUTTON, lParam)
			PostMessage(hWnd,MOUSE_MOVE, MK_LBUTTON, lParam)
#		SendMessage(child_hWnd, MOUSE_LEFTUP, MK_LBUTTON, lParam)
		PostMessage(hWnd, MOUSE_LEFTUP, MK_LBUTTON, lParam)
#		user32.ShowWindow(foreWnd,1)
#		user32.SetForegroundWindow(foreWnd) # 归还焦点
		sleep((300 if count > 1 else 100)/1000)
		count -= 1

from win32print import GetDeviceCaps
from win32gui import SetWindowPos, GetWindowRect, GetDC
prime_screen_width = GetDeviceCaps(GetDC(0),118) #主屏横向分辨率
prime_screen_height = GetDeviceCaps(GetDC(0),117) #主屏纵向分辨率
def get_windows(XY=False):
	from win32gui import GetWindowText,  EnumWindows, FindWindowEx #, SetWindowLong
#	from win32con import GWL_EXSTYLE, WS_EX_NOACTIVATE
	
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
					SetWindowPos(hwnd, 1, prime_screen_width-8, (768 - int(WIDTH_WIN*9/16) - delta_Y - 40), WIDTH_WIN+8*2, int(WIDTH_WIN*9/16) + delta_Y + 8, 16 | 64) #副屏左下角, Edge
					hwnd = FindWindowEx(hwnd, None, 'Intermediate D3D Window', None)
				elif 'Google' in title:
					reSize(1, 88); browser = 'Chrome'
					SetWindowPos(hwnd, 1, prime_screen_width-8, (768 - int(WIDTH_WIN*9/16) - delta_Y - 40), WIDTH_WIN+8*2, int(WIDTH_WIN*9/16) + delta_Y + 8, 16 | 64) #副屏左下角, Chrome
					hwnd = FindWindowEx(hwnd, None, 'Intermediate D3D Window', None)
				elif 'Mozilla' in title:
					reSize(5, 29); browser = 'Firefox'
					SetWindowPos(hwnd, 1, 0, (prime_screen_height - int(WIDTH_WIN*9/16) - delta_Y - 38), WIDTH_WIN + (delta_X)*2, int(WIDTH_WIN*9/16) + delta_Y + delta_X, 16 | 64) #主屏左下角, Firefox
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

def reHwnd(left = True, XY=False) ->int:
	# 获取所有窗口句柄
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
#uflag = 1 | 2 | 4 | 16 | 64
import numpy as np
def screezeCap(hWnd, top = False):
	from pyscreeze import screenshot # pyscreeze只能对主屏幕窗口截图，优点在于系统适配好
	rect = dict(zip('left top right bottom'.split(), GetWindowRect(hWnd)))
	# 窗口截图
	if top: # 置顶
		SetWindowPos(hWnd, 0, 0, 0, 0, 0, 16 | 64) 
		sleep(0.5)
	image = None; n = 3 # 有失败可能，三次尝试
	while image is None and n > 0: 
		image = np.asarray(screenshot(region=[rect['left'], rect['top'], rect['right'] - rect['left'], rect['bottom'] - rect['top']]))
		n -= 1
	if top: # 置顶
		SetWindowPos(hWnd, -2, 0, 0, 0, 0, 16 | 64) # 下沉窗口
	return image

def dxcamCap(hWnd, top = False):
	import dxcam # dxcam截图支持多个屏幕, 速度快, 兼容性欠佳
	#from PIL import Image
	global prime_screen_width
	rect = dict(zip('left top right bottom'.split(), GetWindowRect(hWnd)))
	# 窗口截图
#	SetWindowPos(hWnd, (0 if top else -2), 0, 0, 0, 0, 1 | 2 | 16 | 64 | 512) # 置顶
#	sleep(0.3)
	camera = dxcam.create(output_idx=(0 if rect['right'] <= prime_screen_width else 1), output_color="BGR")
	image = None # 有失败可能，三次尝试
	while image is None and (n:=3) > 0:
		if rect['right'] <= prime_screen_width: #主屏
			image = camera.grab(region=(rect['left'],rect['top'], rect['right'], rect['bottom'])) #第二屏修正
		else: #第二屏
			#print("Rect info:", rect['left']-prime_screen_width,rect['top'],rect['right']-prime_screen_width,rect['bottom'])
			image = camera.grab(region=(rect['left']-prime_screen_width,rect['top'],rect['right']-prime_screen_width,rect['bottom'])) #第二屏修正
			#image = image[:, :, ::-1] #反转色彩通道
		n -= 1
	#Image.fromarray(image).show()
#	if top: # 置顶
#		SetWindowPos(hWnd, -2, 0, 0, 0, 0, 1 | 2 | 16 | 64 | 512) # 下沉窗口
	return image

if __name__ == "__main__":
	from sys import argv
	if argv[-1] == 'XY':
		wins = get_windows(XY=True)
	else:
		wins = get_windows()
	for w in wins:
		print(f'Window[{wins.index(w)}]: 	HWND:{w["hWnd"]}, 	LEFT:{w["rect"]["left"]}')
