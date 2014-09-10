#!/usr/bin/python
#coding:utf-8
import time
import datetime
import re

import requests
import bs4
import urllib

import xlsxwriter

s = requests.Session()
# set headers
s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
s.headers['Accept-Encoding'] = 'gzip,deflate,sdch'
s.headers['Accept-Language'] = 'zh-CN,zh;q=0.8'
s.headers['Cache-Control'] = 'max-age=0'
s.headers['Connection'] = 'keep-alive'
s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'

# GET to get hidAccessKey
r = s.get('http://ehire.51job.com/MainLogin.aspx')

s.headers['Origin'] = 'http://ehire.51job.com'
s.headers['Referer'] = 'http://ehire.51job.com/MainLogin.aspx'

ctmName = urllib.quote('深圳华为技术', safe='~()*!.\'')
userName = urllib.quote('SHPT01', safe='~()*!.\'')
password = urllib.quote('zhaopin@hw', safe='~()*!.\'')
soup = bs4.BeautifulSoup(r.text)
hidAccessKey = soup.find(id='hidAccessKey')['value']

# POST to login
# post scheme: post_to_url(loginPath + "Member/UserLogin.aspx", { ctmName: encodeURIComponent(trim(MemberName)), userName: encodeURIComponent(trim(UserName)), password: encodeURIComponent(trim(Password)), checkCode: trim(checkCode), oldAccessKey: accessKey, langtype: langType, isRememberMe: isRememberMe.checked });
payload = {'ctmName': ctmName, 'userName':userName, 'password':password, 'checkcode':'', 'oldAccessKey':hidAccessKey, 'langtype':'Lang=&Flag=1', 'isRememberMe':'false'}
ra = s.post('https://ehirelogin.51job.com/Member/UserLogin.aspx', data=payload)

# print(ra.text.encode('utf-8'))
time.sleep(1)

# if need kick out
kickOutMesgPattern = re.compile('KickOut')

if kickOutMesgPattern.search(ra.text) :
	soup = bs4.BeautifulSoup(ra.text)
	postUrl = soup.find(id='form1')['action']
	eventTarget = 'gvOnLineUser'
	eventArgument = 'KickOut$0'
	viewState = soup.find(id='__VIEWSTATE')['value']
	payload = {'__EVENTTARGET': eventTarget, '__EVENTARGUMENT': eventArgument, '__VIEWSTATE': viewState}
	# POST to kickout
	ra = s.post('http://ehire.51job.com/Member/'+postUrl, data=payload)
	pass

# resume search
ra = s.get('http://ehire.51job.com/Candidate/SearchResumeIndex.aspx')

soup = bs4.BeautifulSoup(ra.text)
viewState = soup.find(id='__VIEWSTATE')['value']
payload = {
	'MainMenuNew1$CurMenuID':'MainMenuNew1_imgResume|sub4',
	'txtUserID':'--多个ID号用空格隔开--',
	'DpSearchList':'',
	'WORKFUN1$Text':'最多只允许选择3个项目',
	'WORKFUN1$Value':'',
	'KEYWORD':'展讯 博通 玛维尔 思科 联通 移动 电信 中兴 贝尔 朗讯',
	'chkKeyWord':'on',
	'AREA$Value':'',
	'WorkYearFrom':'4',
	'WorkYearTo':'99',
	'TopDegreeFrom':'6',
	'TopDegreeTo':'8',
	'LASTMODIFYSEL':'1',
	'WORKINDUSTRY1$Text':'最多只允许选择3个项目',
	'WORKINDUSTRY1$Value':'',
	'AgeFrom':'25',
	'AgeTo':'39',
	'EXPECTJOBAREA$Value':'020000',
	'hidSearchID':'2,3,6,23,5,1,4,7,24,2,3,6,23,2,3,6,23,2,3,6,23',
	'hidWhere':'00#0#0#0|99|20140830|20140906|25|39|4|99|99|000000|000000|99|99|99|0000|6|8|99|00|0000|99|99|99|0000|99|99|00|99|99|99|99|99|99|99|99|99|020000|0|0|0000#%BeginPage%#%EndPage%#展讯 or 博通 or 玛维尔 or 思科 or 联通 or 移动 or 电信 or 中兴 or 贝尔 or 朗讯',
	'hidValue':'KEYWORDTYPE#0*LASTMODIFYSEL#1*AGE#25|39*WORKYEAR#4|99*AREA#*TOPDEGREE#6|8*WORKINDUSTRY1#*WORKFUN1#*EXPECTJOBAREA#020000*KEYWORD#展讯 or 博通 or 玛维尔 or 思科 or 联通 or 移动 or 电信 or 中兴 or 贝尔 or 朗讯',
	'hidTable':'',
	'hidSearchNameID':'',
	'hidPostBackFunType':'',
	'hidChkedRelFunType':'',
	'hidChkedExpectJobArea':'0',
	'hidChkedKeyWordType':'0',
	'hidNeedRecommendFunType':'',
	'hidIsFirstLoadJobDiv':'1',
	'txtSearchName':'',
	'ddlSendCycle':'1',
	'ddlEndDate':'7',
	'ddlSendNum':'10',
	'txtSendEmail':'',
	'COID':'',
	'DIVID':'',
	'txtJobName':'',
	'__EVENTTARGET':'',
	'__EVENTARGUMENT':'',
	'__LASTFOCUS':'',
	'__VIEWSTATE':viewState,
}

time.sleep(1)
ra = s.post('http://ehire.51job.com/Candidate/SearchResume.aspx',data=payload)
soup = bs4.BeautifulSoup(ra.text)
# print(ra.text.encode('utf-8'))
totalPages = soup.find(id='pagerTop_previousButton').find_next('strong').text
# print(totalPages)

time.sleep(1)

# parse the pages to resume

trPattern = re.compile('trBaseInfo_\d+')
resumeTrs = soup.find_all(id=trPattern)


for tr in resumeTrs:
	# no resume id means the resume is hidden
	resumeIDtd = tr.find(attrs={'class':'inbox_td22'})
	if resumeIDtd is None:
		continue
		pass
	resumeID = resumeIDtd.find('a').text
	resumeLink = resumeIDtd.find('a')['href']
	latestUpdate = tr.find_all(attrs={'class':'inbox_td4'})[9].text
	(year, month, day) = latestUpdate.split('-')
	UpdateDate = datetime.date(int(year), int(month), int(day))

	if UpdateDate == datetime.date.today() :
		rb = s.get('http://ehire.51job.com'+resumeLink)
		output = open('./resumes/'+resumeID+'.html', 'w')
		output.write(rb.text.encode('utf-8'))
		time.sleep(1)
		pass
	pass




# change pages
pageToGo = 5
soup = bs4.BeautifulSoup(ra.text)
viewState = soup.find(id='__VIEWSTATE')['value']
hidCheckUserIds = soup.find(id='hidCheckUserIds')['value']
hidCheckKey = soup.find(id='hidCheckKey')['value']
hidSearchID = soup.find(id='ctrlSerach_hidSearchID')['value']
payload = {
	'__EVENTTARGET':'',
	'__EVENTARGUMENT':'',
	'__LASTFOCUS':'',
	'__VIEWSTATE':viewState,
	'MainMenuNew1$CurMenuID':'MainMenuNew1_imgResume|sub4',
	'ctrlSerach$hidTab':'',
	'ctrlSerach$hidFlag':'',
	'ctrlSerach$ddlSearchName':'',
	'ctrlSerach$hidSearchID':hidSearchID,
	'ctrlSerach$hidChkedExpectJobArea':'0',
	'ctrlSerach$KEYWORD':'展讯 or 博通 or 玛维尔 or 思科 or 联通 or 移动 or 电信 or 中兴 or 贝尔 or 朗讯',
	'ctrlSerach$KEYWORDTYPE':'0',
	'ctrlSerach$AREA$Text':'选择/修改',
	'ctrlSerach$AREA$Value':'',
	'ctrlSerach$TopDegreeFrom':'6',
	'ctrlSerach$TopDegreeTo':'8',
	'ctrlSerach$LASTMODIFYSEL':'1',
	'ctrlSerach$WorkYearFrom':'4',
	'ctrlSerach$WorkYearTo':'99',
	'ctrlSerach$WORKFUN1$Text':'选择/修改',
	'ctrlSerach$WORKFUN1$Value':'',
	'ctrlSerach$WORKINDUSTRY1$Text':'选择/修改',
	'ctrlSerach$WORKINDUSTRY1$Value':'',
	'ctrlSerach$AgeFrom':'25',
	'ctrlSerach$AgeTo':'39',
	'ctrlSerach$EXPECTJOBAREA$Text':'上海',
	'ctrlSerach$EXPECTJOBAREA$Value':'020000',
	'ctrlSerach$txtUserID':'-多个简历ID用空格隔开-',
	'ctrlSerach$txtSearchName':'',
	'pagerBottom$txtGO':pageToGo,
	'pagerBottom$lbtnGO':'',
	'cbxColumns$0':'AGE',
	'cbxColumns$1':'WORKYEAR',
	'cbxColumns$2':'SEX',
	'cbxColumns$4':'AREA',
	'cbxColumns$9':'TOPDEGREE',
	'cbxColumns$12':'WORKINDUSTRY',
	'cbxColumns$13':'WORKFUNC',
	'cbxColumns$14':'LASTUPDATE',
	'cbxColumns$15':'TOPSCHOOL',
	'hidSearchHidden':'',
	'hidUserID':'',
	'hidCheckUserIds':hidCheckUserIds,
	'hidCheckKey':hidCheckKey,
	'hidEvents':'',
	'hidBtnType':'',
	'hidDisplayType':'0',
	'hidJobID':'',
	'hidValue':'KEYWORDTYPE#0*LASTMODIFYSEL#1*AGE#25|39*WORKYEAR#4|99*TOPDEGREE#6|8*EXPECTJOBAREA#020000*KEYWORD#展讯 or 博通 or 玛维尔 or 思科 or 联通 or 移动 or 电信 or 中兴 or 贝尔 or 朗讯',
	'hidWhere':'00#0#0#0|99|20140831|20140907|25|39|4|99|99|000000|000000|99|99|99|0000|6|8|99|00|0000|99|99|99|0000|99|99|00|99|99|99|99|99|99|99|99|99|020000|0|0|0000#%BeginPage%#%EndPage%#展讯 or 博通 or 玛维尔 or 思科 or 联通 or 移动 or 电信 or 中兴 or 贝尔 or 朗讯',
	'hidSearchNameID':'',
	'hidEhireDemo':'',
	'hidNoSearch':'',
}

ra = s.post('http://ehire.51job.com/Candidate/SearchResume.aspx',data=payload)
# print(ra.text.encode('utf-8'))
