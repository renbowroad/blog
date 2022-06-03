from flask import Flask
from flask import render_template

app = Flask(__name__) #flaskのインスタンス化，お決まりのスクリプトとして考える

bullets = [
    '箇条書き',
    '箇条書き',
    '箇条書き',
    '箇条書き',
    '箇条書き',
    '箇条書き',
]

@app.route("/")
def hello():
    return render_template('hello.html', bullets=bullets)