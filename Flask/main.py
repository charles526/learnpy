from flask import Flask, request, jsonify, url_for,render_template, flash, redirect
import pymysql
import paho.mqtt.client as mqtt
import threading
import sys
import os
import json
import time
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import timedelta
import genconf #aqara

#from blinker import Namespace
#my_signals = Namespace()
#model_saved = my_signals.signal('model-saved')

app = Flask(__name__)

#app.config['SECRET_KEY'] = 'hard to guess string'


#get_param_from_json('config','jn5189_pins')
def get_param_from_json(manu_1, manu_2):
    param_path= os.path.join(os.getcwd(), 'conf.json')
    try:
        f =open(param_path, encoding='utf-8')
    except Exception as e:
        print(e)
        print(param_path)
    return json.load(f)[manu_1][manu_2]


app.config['SECRET_KEY'] = get_param_from_json('flask','secret_key')
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

#@model_saved.connect_via(app)
#def on_model_saved():
    # do something ...
#    print ("do somthing ...")
global sys_status
sys_status={"stop":1 ,"compile":"start"}
def set_sys_status(key="", value=""):
     global sys_status
     sys_status[key]=value
     
def get_sys_status(key=""):
     global sys_status
     return sys_status[key]

class Login(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired(),Length(3, 8, 'should be between 3 and 8')])
    submit = SubmitField('Login')
    #agree = BooleanField('记住密码')

@app.route('/')
def index():
    desc= desc_sql('user3')
    print(desc)
    return 'Hello World %s'%str(desc)

@app.route('/login_mq')
def user_login_mq():
    print("mqtt")
    mqtt_send_msg("login from flask!")
    flash('超时错误',category="error")

    #return user_sql_db('user3')
    return 'Hello World Login'



def dict_to_json(record, ioType="NONE", peripheral="NONE", init_1="NONE", init_2="NONE", bus_set="NONE"):
    dict = {}
    dict['one'] = record[2] # edit placeholder
    dict['two'] = record[3]
    dict['three'] = record[4]
    dict['four'] = record[5]
    dict['five'] = record[6]
    dict['init_1'] = init_1 #selector
    dict['init_2'] = init_2 #selector
    dict['init_3'] = record[9]
    dict['init_4'] = record[10]
    dict['init_5'] = bus_set #selector
    dict['io_type'] = ioType
    dict['peripheral'] = peripheral

    dict['init_tb1'] = record[7] #selector
    dict['init_tb2'] = record[8] #selector

    print(dict)  
    j = json.dumps(dict)
    print(type(j))
    print(j) 
    return j

@app.route('/ajax_iotype')
def user_ajax_iotype():
    print("ajax: ")
    if request.args.get('state') == "init":
       io=req_sql(origin=r"SELECT name FROM placeholder;")
       p=req_sql(origin=r"SELECT name FROM peripheral;")
       ret=req_sql( id= 1, table_name="placeholder")
       t1=req_sql(origin=r"SELECT name FROM %s;"%ret[0][7])
       return dict_to_json(ret[0], ioType=io, peripheral=p, init_1=t1)
    else:
       option = request.args.get('io_type')
       print(option)
       ret=req_sql(origin=r'SELECT * FROM placeholder WHERE name="%s";'%option)
       print(ret[0])
       t1="NONE"
       t2="NONE"
       driver="NONE"
       if ret[0][7] != "NONE":
           t1=req_sql(origin=r"SELECT name FROM %s;"%ret[0][7])
       if ret[0][8] != "NONE":
           t2=req_sql(origin=r"SELECT name FROM %s;"%ret[0][8])
       if ret[0][11] != "NONE":
           origin=r'SELECT name FROM busdriver WHERE name LIKE "'+ option+ '%'+'";'
          # print(origin)
           driver=req_sql(origin=origin)
       return dict_to_json(ret[0], init_1=t1, init_2=t2, bus_set=driver)

@app.route('/ajax_add')
def user_ajax_add():
    print("ajax:add ")
 #   values=request.args.get('data')
 #   print(values)
    num=req_sql(origin=r"SELECT count(*) FROM lumi_demofile;")
    print(num[0][0])
    values=str(num[0][0]+1) + request.args.get('data')
    print(values)
    ret= add_sql(values=values, table_name="lumi_demofile")
    print(ret)
   # ret=req_sql( 0, table_name="lumi_demofile")
    return "ok";

@app.route('/ajax_del')
def user_ajax_del():
    print("ajax:del ")
    values=request.args.get('id')
    print(values)
    delete_sql(user_id=values, table_name="lumi_demofile")
    print(ret)
   # ret=req_sql( 0, table_name="lumi_demofile")
    return "ok";

@app.route('/ajax_query')
def user_ajax_query():
    print("ajax:query ")
    values=request.args.get('query')
    print(values)
    return get_sys_status(key=values)
   

@app.route('/ajax_genbin')
def user_ajax_genbin():
    print("ajax:genbin ")
    values=request.args.get('state')
    print(values)
    table_name=request.args.get('table_name')
    print(table_name)
    ret=req_sql( 0, table_name=table_name)
    print(type(ret))
    print(ret)
    #generate config file
    genconf.start_gen_file(ret)
    #git push to repo

    set_sys_status(key="compile", value="start")
    time.sleep( 5 )

    #send msg to compile service
    mqtt_send_msg("compile")
    return str(ret);

@app.route('/user/<user_id>')
def user_info(user_id):
    #mqtt_send_msg("login from flask!")
    return 'hello %s' % user_id 


@app.route('/delete/<user_id>')
def delete_info(user_id):
    delete_sql(user_id=int(user_id), table_name="lumi_demofile")
    print(type(user_id))
    print(user_id)
    return redirect(url_for('user_config', table_name='lumi_demofile'))

 
# 路由传递参数[限定数据类型]
@app.route('/user_id/<int:user_id>')
def user_info_id(user_id):
    return 'hello int --> %d' % user_id
 
@app.route('/sql/<table_name>', methods=['get','post'])
def user_sql_db(table_name):
    if request.method == 'POST':
        sql_info = request.form.to_dict()
        sql = sql_info.get("sql")
        print("sql submit")
        print(sql)
        rr= cli_sql(sql)
        print(type(rr))
       # return sql+str(rr)
    ret=req_sql( 0,table_name)
    print(type(ret))
    heads=desc_sql(table_name)
   
   # for records in ret:
   #     print (type(records))
   #     for item in records:
   #         print(item)
  
    global sys_status
    return render_template('sql.html', heads=heads,records=ret, sys_status=sys_status, title='demo sql')

@app.route('/config/<table_name>', methods=['get', 'post'])
def user_config(table_name):
#    form = Login()
    if request.method == 'POST':
        print("22222222222222222222222")
        user_info = request.values.to_dict()
        print(user_info)
    heads=desc_sql(table_name)
    ret=req_sql(0, table_name)
    return render_template('config.html',  heads=heads,records=ret,  title='configuration')



@app.route('/login/', methods=['get', 'post'])
def user_login():
    form = Login()
    if request.method == 'POST':
        # 验证表单
        if form.validate_on_submit():
            # 获取表单方式1
            username = form.username.data
            password = form.password.data
            print("11111111111111111111111111111")
            print(username)
            print(password)
            if username=="admin" and password=="admin":
                return redirect(url_for('user_config', table_name='lumi_demofile'))
            else:
                print("22222222222222222222222")
                print(type(form.data))
                print(form.data)
        else:
            # 验证失败
            print(form.errors)
            error_msg = form.errors
            for k, v in error_msg.items():
                print(k, v[0])
            #return "failed"
  
    return render_template('login.html', form=form,  title='login')



# the following is about the database
sql_ip = get_param_from_json('sql','remote_ip')#"192.168.116.130"
sql_user=get_param_from_json('sql','user') #"root"
sql_pw = get_param_from_json('sql','password')
sql_db = get_param_from_json('sql','db_name')#"db_learn"
sql_tb_default = get_param_from_json('sql','tb_name_default')#"user3"
print("ip:%s user:%s pw:%s db:%s tb:%s" %(sql_ip, sql_user ,sql_pw ,sql_db ,sql_tb_default) )

def desc_sql(table_name=sql_tb_default, db_name=sql_db, column=0):
    db = pymysql.connect(sql_ip, sql_user,sql_pw, db_name )
    cursor = db.cursor()
    sql="DESC %s"%table_name
    ret=[]
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        print(type(results))
        print(results)
        for items in results:
           ret.append(items[column])
    except:
        traceback.print_exc()
    db.close()
    return ret  # tuple

def req_sql(id=0, table_name=sql_tb_default, db_name=sql_db, like="",column="*", name="name", origin=""):
    db = pymysql.connect(sql_ip, sql_user,sql_pw, db_name )
    cursor = db.cursor()
    if origin == "":
        if like == "":
            if id == 0:
                sql="SELECT * FROM %s"%table_name
            else:
                sql="SELECT * FROM %s WHERE id=%d" %(table_name,id)
        else:
            sql=r'SELECT %s FROM %s WHERE %s LIKE "%s"' %(column, table_name,name, like)
    else:
        sql=origin
    try:
        print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        print(type(results))
  #      print(results)
    except:
        traceback.print_exc()
    db.close()
    return results  # tuple

def add_sql(values, table_name=sql_tb_default, db_name=sql_db):
    db =  pymysql.connect(sql_ip, sql_user,sql_pw, db_name )
    cursor = db.cursor()

    sql="INSERT INTO %s VALUES(%s)"%(table_name ,values)  
    print(sql) 

    try:
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        print(type(results))
        print(results)
    except:
        traceback.print_exc()
    db.close()
    return results  # tuple


def delete_sql(user_id, table_name=sql_tb_default, db_name=sql_db):
    db =  pymysql.connect(sql_ip, sql_user,sql_pw, db_name )
    cursor = db.cursor()

    sql="DELETE FROM %s WHERE id=%d" %(table_name ,user_id)
    try:
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        print(type(results))
        print(results)
    except:
        traceback.print_exc()
    db.close()
    return results  # tuple

def cli_sql(sql, db_name=sql_db):
    db =  pymysql.connect(sql_ip, sql_user,sql_pw, db_name )
    cursor = db.cursor()
    print(type(sql))
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        print(type(results))
        print(results)
    except:
        traceback.print_exc()
    db.close()
    return results  # tuple


# the following is about the MQTT
HOST = get_param_from_json('mqtt', 'host')# "192.168.116.130"
PORT = get_param_from_json('mqtt', 'port') #1883
TOPIC = get_param_from_json('mqtt', 'topic')#"config_mcu_io"
mqtt_client = mqtt.Client()
def mqtt_send_msg(msg):
    mqtt_client.publish(TOPIC, msg, 1)

def on_message_callback(client, userdata, message):
    rx_msg=message.topic+" --> " + str(message.payload)
#    rx_msg=message.topic+" " + ":" + str(message.payload.decode('utf-8'))
    print(rx_msg)
    pt = rx_msg.find(':')
    if pt > 0:
        print(rx_msg[(pt+1):-1])
  #  dict = json.loads(payload)
    set_sys_status(key="compile", value="ok")
    set_sys_status(key="time_stamp", value=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    #flash("mqtt rx_msg",category="error")
   
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(TOPIC)
    mqtt_send_msg("mqtt connected success!!")

def startMqtt():
 #  mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message_callback
    mqtt_client.connect(HOST, PORT, 60)
    #mqtt_client.loop_forever()
    mqtt_client.loop_start()


if __name__ == '__main__':

    startMqtt()
    print("MQTT IS STARTING!")
    app.run(debug=True,host="0.0.0.0", port=5000)

