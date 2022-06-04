#export FLASK_APP=aap 環境変数にappを追加．app.pyがflaskのアプリケーションであると明示できた
#export FLASK_ENV=development デベロップモード起動
from xml.etree.ElementInclude import default_loader
from enum import unique
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
import os



app = Flask(__name__)#インスタンス化，アプリケーション生成
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'#パスの作成
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()#loginの機能を備えたクラスをインスタンス化
login_manager.init_app(app)#アプリケーションの紐付け

class Post(db.Model):#db.Modelはflask_sqlalchemyを使うために必要なクラスを継承
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):#二つのクラスを継承，UserMixinでログインに必要な機能を持たせたクラスを継承している
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
  if request.method == 'GET':
    posts = Post.query.all()#全てのデータをリスト型で取得
    return render_template('index.html', posts=posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    user = User(username=username, password=generate_password_hash(password, method='sha256'))#ハッシュ化するためのmethodを指定

    db.session.add(user)
    db.session.commit()
    return redirect('/login')
  
  else:
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()#引数に合致するものをとってくる
    if check_password_hash(user.password, password):
      login_user(user)
      return redirect('/')
  
  else:
    return render_template('login.html')

@app.route('/logout')
@login_required#デコレータを追加するだけでアクセス制限を実現（つまりログインしているユーザしかここにはアクセスできない）
def logout():
    logout_user()
    return redirect('/login')


@app.route('/create', methods=['GET', 'POST'])#デフォルトではGETのみ受付
@login_required
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
@login_required
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
@login_required
def delete(id):
  post = Post.query.get(id)
  
  db.session.delete(post)#削除
  db.session.commit()#変更を反映
  return redirect('/')