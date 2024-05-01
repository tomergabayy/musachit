from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from botocore.exceptions import ClientError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from datetime import datetime
import os, boto3, json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ikwuger435r34t3t35gf'

def get_secret():
    secret_name = "rds!db-e4011d55-c912-4476-9ef3-ab6f88d9841f"
    region_name = "eu-north-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Parse the JSON string to extract username and password
    secret = json.loads(get_secret_value_response['SecretString'])
    username = secret['username']
    password = secret['password']

    return username, password

db_host = os.getenv('RDS_HOSTNAME')
db_name = os.getenv('RDS_DB_NAME')
db_user, db_password = get_secret()

# Set up the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Garage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    last_visit = db.Column(db.String(20), nullable=False)
    brands = db.Column(db.String(200), nullable=False)
    garage_num = db.Column(db.String(20), nullable=False)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})


@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'GET':
        return render_template('index.html')
    

@app.route('/add_garage', methods=['GET', 'POST'])
@login_required
def add_garage():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contact = request.form['contact']
        phone = request.form['phone']
        brands = request.form['brands']
        garage_num = request.form['garage_num']
        garage = Garage(name=name, address=address, contact=contact, phone=phone,last_visit="עדיין לא ביקרתי",brands=brands,garage_num=garage_num)
        db.session.add(garage)
        db.session.commit()
        return render_template('index.html')
    return render_template('add_garage.html')


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        empty = False
        query = request.form['query']
        garages = Garage.query.filter(Garage.name.ilike(f'%{query}%')).all()
        if len(garages)==0:
            empty = True
        return render_template('search_results.html', garages=garages, empty=empty)
    return render_template('index.html')

@app.route('/delete/<snum>', methods=['GET', 'POST'])
@login_required
def delete(snum):
    Garage.query.filter_by(garage_num=snum).delete()
    db.session.commit()
    flash('Garage f{snum} deleted succesfully!')
    return redirect(url_for('index'))

@app.route('/visit/<snum>', methods=['GET', 'POST'])
@login_required
def visit(snum):
    Garage.query.filter_by(garage_num=snum).update({"last_visit": str(datetime.now().date())})
    db.session.commit()
    flash('Garage f{snum} marked as visited succesfully!')
    return redirect(url_for('search'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                return redirect(url_for('index'))
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(401)
def unauthorized_access(error):
    return redirect(url_for('login'))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()