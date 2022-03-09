from tkinter import *
from tkinter import messagebox
from PIL import ImageTk , Image,ImageGrab
import win32gui
import win32con
from ocr_lib import *
from tkinter.filedialog import askdirectory
from cv2 import cv2 as cv
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
class MainPage(object):
	def __init__(self, master=None):
		self.root = master #定義內部變數root
		self.createPage()

	def createPage(self):
		self.inputPage = InputFrame(self.root) # 建立不同Frame
		self.inputPage.pack() #預設顯示資料錄入介面
class InputFrame(Frame): # 繼承Frame類
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.root = master #定義內部變數root
		self.root.geometry('%dx%d' % (700, 430)) #設定視窗大小
		self.root.minsize(700,400)
		self.root.maxsize(700,450)
		self.hwnd = StringVar()
		self.top = StringVar()
		self.left = StringVar()
		self.bottom = StringVar()
		self.right = StringVar()
		self.path=StringVar()
		self.interval=StringVar()
		self.filename=StringVar()
		self.run=True
		self.createPage()
	
	def createPage(self):
		img_1 = Image.open("./picture/eye.gif")     #按鈕圖標
		img_1 = img_1.resize((30,30))
		self.photoImg_1 =  ImageTk.PhotoImage(img_1)	
		b=Button(self,image=self.photoImg_1,cursor="tcross")
		b.grid(row=0,pady=20)
		b.bind("<ButtonRelease-1>",self.func)
		hwndlabel=Label(self, text = '視窗代碼',fg='red',font=24)
		hwndlabel.grid(row=0, column=1,stick=W,padx=20)
		hwnd_var=Entry(self, textvariable=self.hwnd,width=17,justify=CENTER)
		hwnd_var.grid(row=0, column=2,columnspan=3,stick=W, pady=10,padx=20)
		hwnd_var.insert(0,"HWND")
		describtion=Button(self,text="說明",command=self.popdescribtion,bg='Ivory')
		describtion.grid(row=0,column=5,pady=20)
		Button(self,text="顯示截圖",command=self.test_showimg,width=15,height=4,bg='LightCyan').grid(row=0,column=6,columnspan=3,rowspan=2,stick=W,padx=30)
		
		img_2 = Image.open("./picture/pull.gif")     #按鈕圖標
		img_2 = img_2.resize((30,30))
		self.photoImg_2 =  ImageTk.PhotoImage(img_2)
		b=Button(self,image=self.photoImg_2,command=self.createscreenshot)
		b.grid(row=1,pady=20)
		poslabel=Label(self, text = '位置',font=24)
		poslabel.grid(row=1, column=1,stick=W,padx=20)
		pos_var1=Entry(self, textvariable=self.left,width=5,justify=CENTER)
		pos_var1.insert(0,"左")
		pos_var1.grid(row=1, column=2,stick=W)
		pos_var2=Entry(self, textvariable=self.top,width=5,justify=CENTER)
		pos_var2.insert(0,"上")
		pos_var2.grid(row=1, column=3,stick=W)
		pos_var3=Entry(self, textvariable=self.right,width=5,justify=CENTER)
		pos_var3.insert(0,"右")
		pos_var3.grid(row=1, column=4,stick=W)
		pos_var4=Entry(self, textvariable=self.bottom,width=5,justify=CENTER)
		pos_var4.insert(0,"下")
		pos_var4.grid(row=1, column=5,stick=W)
		
		Label(self,text = "儲存路徑",font=24).grid(row = 2, column = 0,pady=20,padx=10)
		pathentry=Entry(self, textvariable =self.path,width=36,justify=CENTER)
		pathentry.insert(0,"路徑")
		pathentry.grid(row = 2, column = 1,columnspan=5,stick=W,padx=20)
		Button(self, text = "選擇路徑", command = self.selectPath,bg='Ivory').grid(row = 2, column = 6,columnspan=2)

		Label(self,text="檔名",font=24).grid(row=3,column=0,pady=20)
		file_local=Entry(self, textvariable=self.filename,width=36,justify=CENTER)
		file_local.insert(0,"default is ocr_text")
		file_local.grid(row=3,column=1,stick=W,columnspan=5,padx=20)
		
		Label(self,text="間隔",font=24).grid(row=4,column=0,padx=20,pady=20)
		interval=Entry(self, textvariable=self.interval,width=20,justify=CENTER)
		interval.insert(0,"default is 5 sec")
		interval.grid(row=4,column=1,columnspan=4,stick=W,padx=20)
		Button(self,text="開始",command=self.buttonstart,width=8,height=2,fg='DarkBlue',bg='Ivory').grid(row=5,column=6,columnspan=2,rowspan=2,stick=E,padx=20)
		Button(self,text="停止",command=self.loopstop,width=8,height=2,fg='red',bg='Ivory').grid(row=5,column=8,columnspan=2,rowspan=2,stick=W)
	def popdescribtion(self):
		messagebox.showinfo("提醒", "請拖曳圖標至視窗取得視窗代碼(準確拖曳至視窗上方邊框正中心)")
	def test_showimg(self):		#預覽圖片
		def divid():
			img = Image.open("./screenshot/test.jpg")
			new_mg = img.crop((int(self.left.get()),int(self.top.get()),int(self.right.get()),int(self.bottom.get())))
			new_mg.save("./screenshot/testshow.jpg")
			os.remove("./screenshot/test.jpg")
		ipclass = win32gui.GetClassName(self.localhwnd)
		if ipclass == "Chrome_WidgetWin_1":
			shell = win32com.client.Dispatch("WScript.Shell")
			shell.SendKeys('%')
			win32gui.SetForegroundWindow(self.localhwnd)
			img = ImageGrab.grab()
			img.save("./screenshot/test.jpg")
			divid()
		else:
			app = QApplication(sys.argv)
			screen = QApplication.primaryScreen()
			img = screen.grabWindow(self.localhwnd).toImage()
			img.save("./screenshot/test.jpg")
			divid()
		src = cv.imread("./screenshot/testshow.jpg") # 這四行能在一個新視窗開啟照片
		cv.imshow("test image", src)
		cv.waitKey(0)
		cv.destroyAllWindows()
		os.remove("./screenshot/testshow.jpg")
	def selectPath(self):
		pathing = askdirectory()
		pathing=pathing.replace("\\",'//')
		self.path.set(str(pathing))
	
	def createscreenshot(self):       #建造一個top-level的視窗
		if self.hwnd.get() == 'HWND':
			messagebox.showinfo("missing input", "請拖曳圖標至視窗取得視窗代碼(準確拖曳至視窗上方邊框正中心)")
			return
		win32gui.SetForegroundWindow(self.localhwnd)
		win32gui.ShowWindow (self.localhwnd,win32con.SW_MAXIMIZE )
		top = Toplevel()
		top.overrideredirect(True)  
		top.attributes("-alpha", 0.3)    #透明度，讓他有灰灰的感覺
		top.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight())) #跟螢幕一樣大
		top.configure(bg="black")
		root.withdraw()     #暫時隱藏root(主畫面)，不是top-level哦
		cv = Canvas(top) #可以圈出框框的畫布
		win32gui.SetForegroundWindow(top.winfo_id())
		def button_1(event):    
			global x, y ,xstart,ystart
			global rec
			x, y = event.x, event.y
			xstart,ystart = event.x, event.y
			self.top.set(ystart)      #紀錄點下去那個點
			self.left.set(xstart)    #紀錄點下去那個點
			cv.configure(height=1)
			cv.configure(width=1)
			cv.config(highlightthickness=0) # 無邊框
			cv.place(x=event.x, y=event.y)
			rec = cv.create_rectangle(0,0,0,0,outline='red',width=2,dash=(4,4))

		def b1_Motion(event):
			global x, y,xstart,ystart
			x, y = event.x, event.y
			cv.configure(height = event.y - ystart)
			cv.configure(width = event.x - xstart)
			cv.coords(rec,0,0,event.x-xstart,event.y-ystart)

		def buttonRelease_1(event):
			global xend,yend
			xend, yend = event.x, event.y
			self.bottom.set(yend)  #紀錄釋放的那個點
			self.right.set(xend) #紀錄釋放的那個點
			top.destroy()   #把top-level刪除掉
			root.deiconify()    #恢復root(主視窗)
			
		top.bind("<Button-1>", button_1)  # 滑鼠左鍵點選->顯示子視窗 
		top.bind("<B1-Motion>", b1_Motion)# 滑鼠左鍵移動->改變子視窗大小
		top.bind("<ButtonRelease-1>", buttonRelease_1) # 滑鼠左鍵釋放->記錄最後遊標的位置
	def func(self,event):
		pos =win32gui.GetCursorPos()      
		self.localhwnd=win32gui.WindowFromPoint(pos) #取得hwnd
		self.hwnd.set(hex(self.localhwnd))  #標籤顯示hwnd
		print(hex(int(self.hwnd.get(),16)))
	def mainloop(self):
		self.test.autofetch()
		self.tkafter=root.after(self.interval_variable*1000,self.mainloop)      #按間格重複執行
	def loopstop(self):
		root.after_cancel(self.tkafter)	
	def buttonstart(self):
		if self.hwnd.get() == 'hwnd' or self.top.get() == '上' or self.path.get()=='路徑':
			if self.hwnd.get() == 'hwnd':
				messagebox.showinfo("missing input", "請拖曳圖標至視窗取得視窗代碼")
			if self.top.get() == '上':
				messagebox.showinfo("missing input", "請選擇範圍")
			if self.path.get() == '路徑':
				messagebox.showinfo("missing input", "請選擇路徑")
		else:			
			if self.interval.get()=="default is 5 sec":
				self.interval_variable = 5
			else:
				self.interval_variable=int(self.interval.get())
			if self.filename.get()=="default is ocr_text":
				file_localname="ocr_text"
			else:
				file_localname=self.filename.get()
			if self.path.get()=="路徑":
				localpath="D:/"
			else:
				localpath=self.path.get()
			self.test=project(self.localhwnd,file_localname,int(self.left.get()),int(self.top.get()),int(self.right.get()),int(self.bottom.get()),localpath)
			self.mainloop()
root = Tk()
root.title('OCR')
MainPage(root)
root.mainloop()