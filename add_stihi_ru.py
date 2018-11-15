
# coding: utf-8

# In[3]:

# Импортируем необходимые библиотеки:
import random
import time
import requests # http-запросы,
import os
import re # регулярные выражения,
from bs4 import BeautifulSoup # удаление тегов html,
from tqdm import tqdm # красотуля для анализа прогресса.
import unify


# In[29]:

genre_dic = {'любовная лирика': 'лирика', 'гражданская лирика': 'лирика лирика', 'пейзажная лирика': 'лирика','городская лирика': 'лирика','религиозная лирика': 'лирика','философская лирика': 'лирика','мистика и эзотерика': 'лирика',            'циклы стихов': 'Крупные формы', 'поэмы': 'Крупные формы','пьесы': 'Крупные формы','запад: сонеты, канцоны, рондо':'Твердые формы','без рубрики':'Стихи без рубрики',            'восток: рубаи, хокку, танка':'Твердые формы', 'акростихи':'Твердые формы', 'верлибр':'Свободные формы и проза',            'белый и вольный стих':'Свободные формы и проза', 'cтихотворения в прозе':'Свободные формы и проза',            'прозаические миниатюры':'Свободные формы и проза','эссе и статьи':'Свободные формы и проза', 'афоризмы':'Свободные формы и проза',            'пародии':'Пародии и юмор','подражания':'Пародии и юмор','шуточные стихи':'Пародии и юмор','иронические стихи':'Пародии и юмор','сатирические стихи':'Пародии и юмор','басни':'Пародии и юмор',            'стихи для детей':'Детские разделы','детское творчество':'Детские разделы','авторская песня':'Музыкальное творчество',            'эстрадная песня':'Музыкальное творчество','русский рок':'Музыкальное творчество','либретто':'Музыкальное творчество','шансон':'Музыкальное творчество',            'переводы песен':'Музыкальное творчество','переделки песен':'Музыкальное творчество','поэтические переводы':'Переводы и стихи на других языках',            'стихи на других языках':'Переводы и стихи на других языках','переводы песен':'Переводы и стихи на других языках','без рубрики':'Стихи без рубрики'}


# In[30]:

rubrics = {"01":"любовная лирика",\
"14":"гражданская лирика",\
"02":"пейзажная лирика",\
"08":"городская лирика",\
"19":"религиозная лирика",\
"17":"философская лирика",\
"13":"мистика и эзотерика",\
"04":"циклы стихов",\
"46":"поэмы",\
"47":"пьесы",\
"22":"запад: сонеты, канцоны, рондо",\
"18":"восток: рубаи, хокку, танка",\
"44":"акростихи",\
"32":"верлибр",\
"15":"белый и вольный стих",\
"39":"cтихотворения в прозе",\
"05":"прозаические миниатюры",\
"40":"эссе и статьи",\
"06":"афоризмы",\
"12":"пародии",\
"21":"подражания",\
"11":"шуточные стихи",\
"16":"иронические стихи",\
"34":"сатирические стихи",\
"41":"басни",\
"10":"стихи для детей",\
"50":"детское творчество",\
"23":"авторская песня",\
"24":"эстрадная песня",\
"25":"русский рок",\
"26":"либретто",\
"37":"шансон",\
"43":"переводы песен",\
"33":"переделки песен",\
"20":"поэтические переводы",\
"36":"стихи на других языках",\
"43":"переводы песен",\
"03":"без рубрики"}


# In[31]:

#задаем хэдеры - они понадобятся еще много раз
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'
headers = { 'User-Agent' : user_agent }


# In[32]:

def ensure_dir(directory):
    
    if not os.path.exists(directory):
        os.makedirs(directory, mode=0o777, exist_ok=True)
    return directory


# In[25]:

def make_daily_link(year, month, day, topic='all'):
    return 'http://www.stihi.ru/poems/list.html?day='+str(day)+'&month='+str(month)+'&year='+str(year)+'&topic='+str(topic)


# In[33]:

def get_number_poems(link):
    r = requests.get(link, headers=headers)
    
    num = int(re.split(' по', re.split('<p>Произведения в обратном порядке с ', r.text)[1])[0])
    return num


# In[74]:

def get_poem_links(link):
    #ссылка на текст, заголовок, имя автора, ссылка на автора, дата и время
    r = requests.get(link, headers=headers)
    allinks = re.split('"textlink nounline', re.split('опубликовать произведение', r.text)[1])[0].split('</ul>')
    textinfo = []
    
    for part in allinks:
        
        if 'Авторские анонсы' not in part:
            for l in part.split('\n'):
                
                if "poemlink" in l:
                    poemlink = 'http://www.stihi.ru'+re.split('" ', re.split('<li><a href="', l)[1])[0]
                    title = re.split('</a>', re.split('class="poemlink">', l)[1])[0]
                    author = re.split('</a>', re.split('class="authorlink">', l)[1])[0]
                    authorlink = 'http://www.stihi.ru/avtor/'+re.split('" class="authorlink', re.split('href="/avtor/', l)[1])[0]
                    datetime = re.split('</small></li>', re.split('<small>- ', l)[1])[0]
                    date = datetime.split()[0]
                    time = datetime.split()[1]
                    textinfo.append([poemlink, title, author, authorlink,date,time])
    return textinfo


# In[76]:

def get_poem_links_by_date(daily_link):
    r = requests.get(daily_link, headers=headers)
    text_info = []
    
    lines = r.text.split('\n')
    starts = ['http://www.stihi.ru'+re.split('">', re.split('<a href="', l)[1])[0] for l in lines if daily_link.strip('http://www.stihi.ru')+'&start=' in l]
    text_info = get_poem_links(daily_link)
    for i in starts:
        text_info += get_poem_links(i)
    return text_info


# In[6]:

def make_poem_link(year, month, day, textid):
    
    if year<2008 and int(month) < 10:
        try:
            textlink = 'http://www.stihi.ru/'+str(year) + '/' + str(month) + '/' + str(day) +'-' + str(textid)
        except:
            textlink = 'http://www.stihi.ru/'+str(year) + '/' + str(month) + '/' + str(day) +'/' + str(textid)
    else:
        textlink = 'http://www.stihi.ru/'+str(year) + '/' + str(month) + '/' + str(day) +'/' + str(textid)
    return textlink


# In[8]:

# Функия принимает адрес статьи на nplus1.ru и возвращает текст статьи и метаинформацию по ней.
def getTextStihi(textlink):
    r = requests.get(textlink,headers=headers)  
    text = re.split("</div>", re.split('<div class="text">', r.text)[1])[0]
# "Откусываем" оставшиеся теги.
    beaux_text=BeautifulSoup(text, "lxml")
    n_text = beaux_text.get_text() 
    n_text = re.sub('\xa0', '', n_text)
    n_text = unify.unify_sym(n_text)
    return(n_text)


# In[77]:

#Теперь список авторов нам нужно превратить с список данных автора и ссылки на его тексты:
def getAuthorInfo(authorlink):
    r = requests.get(authorlink, headers=headers)
    
    try:
        
        author_items = re.split("</b>", re.split("Произведений: <b>", r.text)[1])[0]
        author_readeres = re.split("</b>", re.split("Читателей</a>: <b>", r.text)[1])[0]
        return author_items, author_readeres

    except:
        return '', ''


# In[12]:

WDIR = ensure_dir(r'/home/tsha/stihi_ru/texts')


# In[ ]:

for year in range(2005,2016)[::-1]:
    metatable_texts = open(ensure_dir(r'/home/tsha/stihi_ru/meta/'+str(year))+'/metatable_texts.txt', 'a', encoding='utf8')
    metatable_texts.write('textid\tURL\ttitle\tauthor\tauthorlink\tdate\ttime\tpath\tauthor_readers\tauthor_poems\ttopic\tgenre\n')
    #textid, poemlink, title, author, authorlink,date,time, path, author_readers,author_poems,topic,genre
    for month in range(1,13)[::-1]:
        if month < 10:
            month = "0" + str(month)
        path = ensure_dir(WDIR + "/"+str(year)+"/"+str(month))
        for day in range(1, 32)[::-1]:
            if day < 10:
                day = "0" + str(day)
            if year==2015 and int(month)==12 :
                pass
            elif year==2015 and int(month)==11 and int(day)>=11:
                pass
            else:
                for topic in rubrics:
                    print(year, month, day,rubrics[topic] )
                    link = make_daily_link(year, month, day, topic)
                    text_info = get_poem_links_by_date(link)
                    
                    #вот здесь по-другому
                    for i in tqdm(range(len(text_info))):
                        textid = str(year)+str(month)+str(day)+str(i)+str(topic)
                        textlink = text_info[i][0]
                        
                
                        try:
                            text = getTextStihi(textlink)
                            textfile = open(os.path.join(path, textid+'.txt'), 'w', encoding='utf8')
                            textfile.write(text)
                            textfile.close()
                            author_poems, author_readers  = getAuthorInfo(text_info[i][3])
                            genre = genre_dic[rubrics[topic]]
                            textfeats = [textid]+text_info[i] + [os.path.join(path, textid+'.txt'),author_poems, author_readers, topic, genre]
                            metatable_texts.write("\t".join(textfeats)+'\n')
                        except:
                            continue
                            print(textlink)
        metatable_texts.close()


# In[ ]:



