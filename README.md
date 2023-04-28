# NLP學期專題

### 本次專題針對臉書房屋買賣社團進行資料篩選及分析

1.利用NLP模型取出貼文中房價、坪數、地址等有用資訊

2.利用以政府資料訓練之線性迴歸模型進行價格預測

3.找出有價值之房屋並呈現於網站



### 相關技術

＊ Bert
```
!pip install transformers
from transformers import BertTokenizer, BertConfig, BertForQuestionAnswering
```
資料編碼、呼叫預訓練模型、訓練模型
* OpenCV
```
pip install opencv-python
```
圖片預處裡(灰階、二值化)
* Scikit learn
```
pip install -U scikit-learn
```
房價預測
* Flask
```
pip install Flask
```
網站製作
* OCR
```
pip install pytesseract
```
將文章圖片轉為文字檔
