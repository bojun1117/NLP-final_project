import win32gui
import win32com.client
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import sys,os
import pytesseract
class project :
    def __init__(self,hwnd,filename,left,up,right,down,path):
        self.hwnd=hwnd
        self.filename=filename
        self.left=left
        self.up=up
        self.right=right
        self.down=down
        newpath=str(path)+"/"
        self.path=newpath

    def autofetch(self):
        ipclass = win32gui.GetClassName(self.hwnd)
        if ipclass=="Chrome_WidgetWin_1":       #判斷是網頁還是應用程式
            self.web_screenshot()
        else:
            self.app_screenshot()
        self.divid()
        self.ocr()

    def web_screenshot(self):            #網路截圖 圖名稱temporary
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)     #將視窗提至最前
        img = ImageGrab.grab()
        img.save("./screenshot/temporary.jpg")

    def app_screenshot(self):            #應用程式截圖 圖名稱temporary
        app = QApplication(sys.argv)
        screen = QApplication.primaryScreen()
        img = screen.grabWindow(self.hwnd).toImage()
        img.save("./screenshot/temporary.jpg")

    def divid(self):      #切割成特定範圍的圖片
        img = Image.open("./screenshot/temporary.jpg")
        new_mg = img.crop((self.left,self.up,self.right,self.down))
        enh_con = ImageEnhance.Contrast(new_mg)
        contrast=2
        image_contrasted = enh_con.enhance(contrast)
        image_contrasted.save("./screenshot/"+self.filename+".jpg")     #切割後圖片 圖名為GUI檔案名
        os.remove("./screenshot/temporary.jpg")

    def ocr(self):          #OCR影像辨識
        test_img = Image.open("./screenshot/"+self.filename+".jpg")
        newtext = pytesseract.image_to_string(test_img, lang='chi_tra+eng')     #OCR程式碼 lang為中文+英文
        fixed_text = newtext.strip()
        self.text=fixed_text
        print(self.text)