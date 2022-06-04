#export FLASK_APP=aap 環境変数にappを追加．app.pyがflaskのアプリケーションであると明示できた
#export FLASK_ENV=development デベロップモード起動
from xml.etree.ElementInclude import default_loader
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


app = Flask(__name__)#インスタンス化，アプリケーション生成
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'#パスの作成
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))



@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    posts = Post.query.all()#全てのデータをリスト型で取得
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])#デフォルトではGETのみ受付
def create():
  if request.method == 'POST':
    title = request.form.get('title')
    body = request.form.get('body')

    post = Post(title=title, body=body)#インスタンス化，左側の変数はdbのもの，右側の変数は上記で設定したもの

    db.session.add(post)#dbに追加
    db.session.commit()#これでようやく反映
    return redirect('/')
  
  else:#GETの場合，つまり単純にアクセスする場合
    return render_template('create.html')


@app.route('/<int:id>/update', methods=['GET', 'POST'])#デフォルトではGETのみ受付
def update(id):
  post = Post.query.get(id)
  if request.method == 'GET':
    return render_template('update.html', post=post)
  else:#POSTで送信される場合
    post.title = request.form.get('title')#フォームの中の内容をそのまま入れる
    post.body = request.form.get('body')#フォームの中の内容をそのまま入れる

    db.session.commit()#更新の場合は，commitだけでおけ
    return redirect('/')
  

@app.route('/<int:id>/delete', methods=['GET'])#GETのみ
def delete(id):
  post = Post.query.get(id)
  
  db.session.delete(post)#削除
  db.session.commit()#変更を反映
  return redirect('/')