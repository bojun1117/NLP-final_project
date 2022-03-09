from flask import Flask
from flask import render_template
from flask import request
import webbrowser,json,os

def webrun():
    app = Flask(__name__)
    @app.route('/index',methods=['GET','POST'])
    def index():
        if request.method == 'POST':
            filename = request.form['filename']
            data1 = filename+"1"
            data2 = filename+"2"
            return render_template('index.html',data1=data1,data2=data2)
        return render_template('index.html')

    @app.route('/')
    def search():
        return render_template('search.html')

    webbrowser.open('http://127.0.0.1:5000')
    app.run()

webrun()