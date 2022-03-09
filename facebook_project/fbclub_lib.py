import numpy as np
import pyautogui
import win32gui
import win32con
import win32com.client
import sys,os,re,json,time
import pytesseract
import jieba,joblib
from cv2 import cv2
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PIL import ImageGrab,Image,ImageEnhance
from sklearn.preprocessing import  PolynomialFeatures
from transformers import BertTokenizer, BertConfig, BertForQuestionAnswering
import torch
import textwrap

def click_image(image,pos,  action, timestamp,offset=40):       #自動點擊目標圖片
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + offset, pos[1], timestamp)
    pyautogui.click(button=action)

def imagesearch(image, precision=0.8):      #尋找特定圖片座標
    im = pyautogui.screenshot()
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [300,500]
    return max_loc #返回圖片座標

def is_number(s):       #判斷是否是數字
    try:  
        float(s)
        return True
    except ValueError:
        pass 
    try:
        import unicodedata 
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
    
def check_valid_nlp_value_num(usr_dict,target_nums):    #檢查數值有沒有都取得到
    count=0
    for key ,value in usr_dict.items():
        if value =='null' or value == '':
            count+=1
    if count > 0:
        usr_dict.clear()

def predict(data,room):         #房價預測

    l1 = joblib.load('./house_model/label_location')
    l2 = joblib.load('./house_model/label_car')
    c = joblib.load('./house_model/columntransformer')
    s = joblib.load('./house_model/standardscaler')
    model = joblib.load('./house_model/house_predict_model')

    test = [[data['location'],data['age'],data['size'],room,data['car']]]
    test = np.array(test)
    test[:,0] = l1.transform(test[:,0])
    test[:,4] = l2.transform(test[:,4])

    test = test.tolist()
    test = [list(map(float,test[0]))]
    test = c.transform(test).toarray()

    test = s.transform(test)

    poly_reg =PolynomialFeatures(degree=2)
    test =poly_reg.fit_transform(test)
    pred_cost = model.predict(test)

    return int(pred_cost)

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
        jieba.initialize()
        jieba.load_userdict("./jieba/district.txt")

    def web_screenshot(self):            #web截圖
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)
        img = ImageGrab.grab()
        img.save("temporary.jpg")

    def divid(self):      #切割成特定範圍的圖片
        img = Image.open("temporary.jpg")
        self.new_mg = img.crop((self.left,self.up,self.right,self.down))
        self.new_mg.save(self.filename+".jpg")
        image_contrasted = cv2.cvtColor(np.float32(self.new_mg),cv2.COLOR_RGB2GRAY)     #灰階
        image_contrasted = cv2.threshold(image_contrasted,180,255,cv2.THRESH_BINARY)[1] #二值化
        cv2.imwrite("ocr.jpg",image_contrasted)
        os.remove("temporary.jpg")

    def ocr(self):                           #ocr影像辨識
        test_img = Image.open("ocr.jpg")
        ocrtext = pytesseract.image_to_string(test_img, lang='chi_tra')  #ocr
        fixed_text = ocrtext.strip()
        self.text=fixed_text
        os.remove("ocr.jpg")

    def jsons_nlp(self):            #閱讀理解
        temporary='./text_file/temporary.txt'
        def strQ2B(s):
            rstring = ""
            for uchar in s:
                u_code = ord(uchar)
                if u_code == 12288:  # 全形空格直接轉換
                    u_code = 32
                elif 65281 <= u_code <= 65374:  # 全形字元（除空格）根據關係轉化
                    u_code -= 65248
                rstring += chr(u_code)
            return rstring
        wrapper = textwrap.TextWrapper(width=80) 
        start_time = time.time()
        tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
        config = BertConfig.from_pretrained("./comprehension_model/main_model/config.json")     #通用閱讀理解模型
        model = BertForQuestionAnswering.from_pretrained("./comprehension_model/main_model/pytorch_model.bin", config=config)
        with open(temporary,'w',encoding='utf-8') as t:       #temporary檔寫入ocr檔案
            t.writelines(self.text.replace(" ",""))
        with open (temporary,"r",encoding="utf-8") as f:
            context=f.read()
            context=strQ2B(context)
            context=context.replace("\n",",")
        form={
                    "price":["價格","開價","售價:","總價","下殺?","只賣?"],
                    "size":["建坪?","坪數?","總建?","總建坪?"],
                    "age":["屋齡?"],
                    "format":["格局?"],	
        }
        questions = ['format','age','size','price']
        self.localdic= dict()
        self.format_number = 0
        for question in questions:
            flag=0
            for ques in form[question]:

                inputs = tokenizer(ques, context, add_special_tokens=True, return_tensors="pt")        #資料編碼
                input_ids = inputs["input_ids"].tolist()[0]

                context_tokens = tokenizer.convert_ids_to_tokens(input_ids)
                logits = model(**inputs,return_dict=True)
                answer_start_scores = logits['start_logits'] 
                answer_end_scores = logits['end_logits']
                answer_start = torch.argmax(answer_start_scores)
                answer_end = torch.argmax(answer_end_scores) + 1
                answer = tokenizer.convert_tokens_to_string(context_tokens[answer_start:answer_end])

                if "[CLS]" not in answer:
                    if question!="format":
                        numbers = [str(temp)for temp in answer.split() if temp.isdigit()]
                        if len(numbers) == 0:
                            continue
                        self.localdic[question]= ".".join(numbers)
                        if question == "age" and self.localdic[question] == '':
                            self.localdic["age"] = '0'
                    if question=="format":
                        numbers = [int(temp)for temp in answer.split() if temp.isdigit()]
                        string_room = [str(int) for int in numbers]
                        string_room = "/".join(string_room)
                        self.format_number=sum(numbers)
                        self.localdic[question]= string_room
                    flag=1
            if flag == 0:
                self.localdic[question]="null"
        config_2 = BertConfig.from_pretrained("./comprehension_model/address_model/config.json")    #專門取得地址的模型
        model_2 = BertForQuestionAnswering.from_pretrained("./comprehension_model/address_model/pytorch_model.bin", config=config_2)
        flag=0
        for ques in ["地址是什麼?","住址是什麼?","地點是什麼?","位於?"]:
            inputs = tokenizer(ques, context, add_special_tokens=True, return_tensors="pt")
            input_ids = inputs["input_ids"].tolist()[0]

            context_tokens = tokenizer.convert_ids_to_tokens(input_ids)
            logits = model_2(**inputs,return_dict=True)
            answer_start_scores = logits['start_logits'] 
            answer_end_scores = logits['end_logits']
            answer_start = torch.argmax(answer_start_scores)
            answer_end = torch.argmax(answer_end_scores) + 1
            answer = tokenizer.convert_tokens_to_string(context_tokens[answer_start:answer_end])
            if "[CLS]" not in answer:
                address=jieba.lcut(answer.replace(" ",""))
                locate = []
                with open('./jieba/district.txt','r',encoding='utf-8') as d:
                    for i in d.readlines():
                        locate.append(i.strip())
                for text in address:
                    if text in locate:
                        self.localdic["location"]=str(text)
                        break
                    else:
                        self.localdic["location"]='null'
                flag=1
        if flag == 0:
            self.localdic["location"]="null"
        if "車位" in context:
            self.localdic["car"]="有"
        else:
            self.localdic["car"]="無"
        print(self.localdic)
        check_valid_nlp_value_num(self.localdic,6)

    def judge(self,index,index1,index2,num1,num2):  #房價預測+判斷
        temporary='./text_file/temporary.txt'
        if self.localdic != {}:
            index.append(self.localdic)
            pred = predict(self.localdic,self.format_number)
            print(pred,self.localdic['price'])
            if int(self.localdic['price']) < pred*4:      #價格低於預測*4，放入第一優先index
                index1.append(self.localdic)
                self.new_mg.save('../house_web/static/screenshot/'+self.filename+'1-'+str(num1+len(index1))+'.jpg')   #儲存圖片連結
            elif int(self.localdic['price']) < pred*8:    #價格低於預測*8，放入第二優先index
                index2.append(self.localdic)
                self.new_mg.save('../house_web/static/screenshot/'+self.filename+'2-'+str(num2+len(index2))+'.jpg')   #儲存圖片連結
            else:
                self.localdic = {}
        os.remove(self.filename+".jpg")
        os.remove(temporary)
   
    def makefile(self,index,index1,index2):        #將txt轉成另存成json
        goal = self.path+self.filename+".txt" 
        jsonfile1 = '../house_web/static/data/'+self.filename+'1.json'
        jsonfile2 = '../house_web/static/data/'+self.filename+'2.json'
        with open(goal,'a',encoding='utf-8') as g:
            json.dump(index,g,indent=4,ensure_ascii=False)
        if os.path.isfile(jsonfile1):               #第一優先json檔
            with open(jsonfile1,'r',encoding='utf-8') as j:
                jslist1 = json.load(j)
                for i in index1:
                    jslist1.append(i)
            with open(jsonfile1,"w",encoding='utf-8') as j:
                json.dump(jslist1,j,indent=4,ensure_ascii=False)
        else:
            with open(jsonfile1,"w",encoding='utf-8') as j:
                json.dump(index1,j,indent=4,ensure_ascii=False)
        if os.path.isfile(jsonfile2):               #第二優先json檔
            with open(jsonfile2,'r',encoding='utf-8') as j:
                jslist2 = json.load(j)
                for i in index2:
                    jslist2.append(i)
            with open(jsonfile2,"w",encoding='utf-8') as j:
                json.dump(jslist2,j,indent=4,ensure_ascii=False)
        else:
            with open(jsonfile2,"w",encoding='utf-8') as j:
                json.dump(index2,j,indent=4,ensure_ascii=False)
