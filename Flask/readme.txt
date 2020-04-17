pip install virtualenv
pip install flask
pip install pymysql
pip install flask_wtf
pip install paho-mqtt -i  https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com

virtualenv -p python3 env

mqtt / json

json->str
json.dumps()
str->json
json.loads()

loads()：将json数据转化成dict数据
dumps()：将dict数据转化成json数据
load()：读取json文件数据，转成dict数据
dump()：将dict数据转化成json数据后写入json文件)

pip freeze >requirements.txt
pip install -r requirements.txt

启动脚本,append the .bashrc file called by login
service mosquitto start # for mqtt server

#login andy in .bashrc
source /home/andy/projects/mcu_config/Flask/env/bin/activate
cd /home/andy/projects/mcu_config/Flask
python main.py


忽略 /env 文件夹
.gitignore  --> env/
git rm -r --cached .
git add .
git commit -m 'update .gitignore'
