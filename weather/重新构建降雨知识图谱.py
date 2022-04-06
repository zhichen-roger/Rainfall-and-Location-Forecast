__author__ = "Huzhichen"
#coding=utf-8
import jiagu
from py2neo import Graph, Node, Relationship, NodeMatcher
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from selenium import webdriver
import webbrowser
import os
# 输入文本
char =input()
text=''
while char!="":
    text= char
    print(char)
    char=input()
print(text)
#提取时间
import re
K=re.findall(r'[0-9]+[年|月|日|时|分]',text)
time=''
for i in range(len(K)):
    if K[i].find('年')!=-1 and K[i+1].find('月')!=-1 and K[i+2].find('日')!=-1 and K[i+3].find('时')!=-1 and K[i+4].find('分')!=-1:
        time=time+K[i]+K[i+1]+K[i+2]+K[i+3]+K[i+4]
print(time)
#提取等级
jiagu.load_userdict(['暴雨蓝色预警','暴雨黄色预警','暴雨橙色预警','暴雨红色预警'])
words = jiagu.seg(text)
level=''
for i in range(len(words)):
    if text.find('暴雨蓝色预警')!=-1:
        level='暴雨蓝色预警'
        break
    if text.find('暴雨黄色预警')!=-1:
        level='暴雨黄色预警'
        break
    if text.find('暴雨橙色预警')!=-1:
        level='暴雨橙色预警'
        break
    if text.find('暴雨红色预警')!=-1:
        level='暴雨红色预警'
        break
print(level)
# 提取地点
ner = jiagu.ner(words) # 命名实体识别
loc=''
flagi=0
for i in range(len(ner)):
    if (ner[i].find('ORG')!=-1 or ner[i].find('LOC')!=-1):
        flagi=i
        loc = loc + words[flagi]
        if ner[i+1]=='O':
            break
print(loc)
# neo4j
graph = Graph("http://localhost:7474", auth=("neo4j", "admin"))
matcher = NodeMatcher(graph)
# 查询预警
blue=matcher.match('蓝色预警').where("_.name='暴雨蓝色预警'").first()
yellow=matcher.match('黄色预警').where("_.name='暴雨黄色预警'").first()
orange=matcher.match('橙色预警').where("_.name='暴雨橙色预警'").first()
red=matcher.match('红色预警').where("_.name='暴雨红色预警'").first()

time_node = Node('时间',label='time',name=time)
loc_pre=matcher.match('地址').where("_.name="+"\'"+loc+"\'").first()
if matcher.match('地址').where("_.name="+"\'"+loc+"\'").exists() == False:
    loc_node= Node('地址',label='location',name=loc)
    graph.create(loc_node)
    print("节点不存在正在创建")
else:
    loc_node=matcher.match('地址').where("_.name="+"\'"+loc+"\'").first()
    print("节点已经存在")
graph.create(time_node)
#关系
relationshipTime = Relationship(time_node,'时间'+time,loc_node)
graph.create(relationshipTime)
# 发送通知邮件
host_server = 'smtp.qq.com'  #qq邮箱smtp服务器
sender_qq = '1053962771@qq.com' #发件人邮箱
pwd = 'rawyxvrkhtvhbbfb'
receiver = ['1053962771@qq.com']#收件人邮箱
#receiver = '1053962771@qq.com@qq.com'
mail_title = '降雨预防提醒' #邮件标题
mail_content=''
if level== '暴雨蓝色预警':
    relationshipLevel = Relationship(loc_node, '灾害等级'+time, blue)
    graph.create(relationshipLevel)
    mail_content = text +'预防措施: 1.政府及相关部门按照职责做好防暴雨准备工作。 ' \
                         '2.学校、幼儿园采取适当措施，保证学生和幼儿安全。 ' \
                         '3.驾驶人员应当注意道路积水和交通阻塞，确保安全。' \
                         '4.检查城市、农田、鱼塘排水系统，做好排涝准备。'  # 邮件正文内容
elif level== '暴雨黄色预警':
    relationshipLevel = Relationship(loc_node, '灾害等级'+time, yellow)
    graph.create(relationshipLevel)
    mail_content = text+'预防措施: 1、政府及相关部门按照职责做好防暴雨工作。' \
                        '2、交通管理部门应当根据路况在强降雨路段采取交通管制措施，在积水路段实行交通引导。' \
                        '3、切断低洼地带有危险的室外电源，暂停在空旷地方的户外作业，转移危险地带人员和危房居民到安全场所避雨。' \
                        '4、检查城市、农田、鱼塘排水系统，采取必要的排涝措施。'  # 邮件正文内容
elif level== '暴雨橙色预警':
    relationshipLevel = Relationship(loc_node, '灾害等级'+time, orange)
    graph.create(relationshipLevel)
    mail_content = text+'预防措施:1、政府及相关部门按照职责做好防暴雨应急工作。' \
                        '2、切断有危险的室外电源，暂停户外作业。' \
                        '3、处于危险地带的单位应当停课、停业，采取专门措施保护已到校学生、幼儿和其他上班人员的安全。' \
                        '4、做好城市、农田的排涝，注意防范可能引发的山洪、滑坡、泥石流等灾害。'  # 邮件正文内容
elif level== '暴雨红色预警':
    relationshipLevel = Relationship(loc_node, '灾害等级'+time, red)
    graph.create(relationshipLevel)
    mail_content = text+'预防措施:1.政府及相关部门按照职责做好防暴雨应急和抢险工作;' \
                        '2、停止集会、停课、停业(除特殊行业外);' \
                        '3、做好山洪、滑坡、泥石流等灾害的防御和抢险工作。'  # 邮件正文内容


# 初始化一个邮件主体
msg = MIMEMultipart()
msg["Subject"] = Header(mail_title,'utf-8')
msg["From"] = sender_qq
# msg["To"] = Header("测试邮箱",'utf-8')
msg['To'] = ";".join(receiver)
# 邮件正文内容
msg.attach(MIMEText(mail_content,'plain','utf-8'))



smtp = SMTP_SSL(host_server) # ssl登录

# login(user,password):
# user:登录邮箱的用户名。
# password：登录邮箱的密码，像笔者用的是网易邮箱，网易邮箱一般是网页版，需要用到客户端密码，需要在网页版的网易邮箱中设置授权码，该授权码即为客户端密码。
smtp.login(sender_qq,pwd)

# sendmail(from_addr,to_addrs,msg,...):
# from_addr:邮件发送者地址
# to_addrs:邮件接收者地址。字符串列表['接收地址1','接收地址2','接收地址3',...]或'接收地址'
# msg：发送消息：邮件内容。一般是msg.as_string():as_string()是将msg(MIMEText对象或者MIMEMultipart对象)变为str。
smtp.sendmail(sender_qq,receiver,msg.as_string())

# quit():用于结束SMTP会话。
smtp.quit()

print("积水路段提醒并用地图查看:")
driver = webdriver.Chrome(r"C:\Users\lenovo\AppData\Local\Google\Chrome\Application\chromedriver.exe")
url = 'http://localhost:63342/pythonProjectWeather/weather/降雨积水路段.html'
driver.get(url)
driver.maximize_window()
