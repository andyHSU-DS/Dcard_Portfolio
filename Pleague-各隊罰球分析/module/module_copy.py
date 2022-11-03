import pandas as pd
import requests
import bs4

import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'notebook'
from plotly.subplots import make_subplots

import re

class PLG:
    #定義隊名跟url
    def __init__(self,team_name,target_team):
        self.name             = team_name
        self.target_team      = target_team
        if '勇士' in self.name:
            self.url = 'https://pleagueofficial.com/team/1'
        elif '攻城獅' in self.name:
            self.url = 'https://pleagueofficial.com/team/3'
        elif '鋼鐵人' in self.name:
            self.url = 'https://pleagueofficial.com/team/5'
        elif '國王' in self.name:
            self.url = 'https://pleagueofficial.com/team/6'
        elif '領航猿' in self.name:
            self.url = 'https://pleagueofficial.com/team/2'
        else:
            self.url = 'https://pleagueofficial.com/team/4'
    #得到資訊
    def get_team_info(self):
        all_data          = []
        table_titles_list = []
        table_datas_list  = []
        if self.url != None:
            team_info_web_obj = requests.get(self.url)
            team_info_soup    = bs4.BeautifulSoup(team_info_web_obj.text,'lxml')
            #大表
            table_record      = team_info_soup.find('table',class_='table fs12 col-md-12 bg-light table-hover')
            #表頭
            table_titles      = table_record.find('tr').find_all('th')
            for table_title in table_titles:
                table_titles_list.append(table_title.text)
            
            #表內資料，table_datas是每一行（每場）
            table_datas       = table_record.find('tbody').find_all('tr')
            for table_data in table_datas:
                each_matchup_data = []
                #每場的每筆資料
                for matchup_detail in table_data.find_all('td'):
                    each_matchup_data.append(matchup_detail.text)
                if each_matchup_data[2] == '':
                    pass
                else:
                    table_datas_list.append(each_matchup_data)
        else:
            pass
        
        all_data.extend(table_datas_list)
        return pd.DataFrame(all_data,columns = table_titles_list)

    #全聯盟的對戰內容
    def matchup_and_host_info(self,url = 'https://pleagueofficial.com/schedule-regular-season'):
        path   = r'/Users/andyhsu/Documents/GitHub/Andy-Portfolio/Pleague-各隊罰球分析/chromedriver'

        日程 = []
        客隊 = []
        主隊 = []
        driver = webdriver.Chrome(path)

        driver.get('https://pleagueofficial.com/schedule-regular-season')
        #即將開打取消
        driver.find_element_by_xpath('/html/body/section[3]/div/div[1]/h1/label/input').click()

        url = driver.page_source
        url_解析 = bs4.BeautifulSoup(url,'lxml')
        目標container = url_解析.find_all('div',class_='container')[1]
        全部對戰組合 = 目標container.find('div',class_='bg-white text-dark border-bottom border-top matches')
        每個對戰組合 = 全部對戰組合.find_all('div',class_ = re.compile('row justify-content-center pt-3 pb-0 pt-md-3 pb-md-3 match_row mx-0'))

        for num in 每個對戰組合:
            日期 = num.find('div',class_='col-lg-1 col-12 text-center align-self-center match_row_datetime').find('h5').text
            日程.append(日期)
            主客隊資訊 = num.find_all('div',class_=re.compile('col-lg-3 col-2 align-self-center'))
            for info in 主客隊資訊:
                主客隊文字資訊 = info.find_all('div',class_='text-center mt-md-2')
                for 文字資訊 in 主客隊文字資訊:
                    if 文字資訊.find('h6',class_='fs12 mb-2 PC_only').text == '客隊':
                        客隊.append(文字資訊.find('span',class_='PC_only fs14').text)
                    elif 文字資訊.find('h6',class_='fs12 mb-2 PC_only').text == '主隊':
                        主隊.append(文字資訊.find('span',class_='PC_only fs14').text)

        driver.close()
        賽程資訊 = pd.DataFrame({'客隊':客隊, '主隊':主隊},index=日程)
        return 賽程資訊

    #input是該隊賽程資料，對戰組合資料及我要看的球隊
    def match資訊(self,team_dataframe, match_up_dataframe):
        specific_match_up_dataframe       = match_up_dataframe[(match_up_dataframe['主隊'] == self.name) | (match_up_dataframe['客隊'] == self.name)]
        team_dataframe['比賽日期'] = team_dataframe['比賽日期'].apply(lambda x:x.replace('-','/')[5:])
        整理後資料 = team_dataframe.merge(specific_match_up_dataframe,left_on='比賽日期',right_index=True)
        return 整理後資料

    #將match資訊的return放入得到我要的資料
    def 資料處理(self,df):
        #定義對手球隊的主場 
        target_team_主場 = self.target_team + '主場'
        df[target_team_主場] = df['主隊'].apply(lambda x: 'Y' if x == self.target_team else 'N')
        df['罰球(進)']   = df['罰球'].apply(lambda x: int(x.split('-')[0]))
        df['罰球(出手)']   = df['罰球'].apply(lambda x: int(x.split('-')[1]))
        return df

    #將各隊在不同主場的表現統整，輸入為資料處理的output
    def 資料彙整(self,df):
        data_frame_list = []
        target_team_主場 = self.target_team + '主場'
        target_Home = df[df[target_team_主場] == 'Y']
        敵對主場_FT = round((target_Home['罰球(進)'].sum()/target_Home['罰球(出手)'].sum())*100,2)
        data_frame_list.append([self.name,target_team_主場,敵對主場_FT])
        N_target_Home = df[df[target_team_主場] == 'N']
        N_target_Home['罰球(進)'].sum()/N_target_Home['罰球(出手)'].sum()
        非敵對主場_FT = round((N_target_Home['罰球(進)'].sum()/N_target_Home['罰球(出手)'].sum())*100,2)
        data_frame_list.append([self.name,'非'+target_team_主場,非敵對主場_FT])
        return pd.DataFrame(data_frame_list)


#繼承PLG        
class PLG_Graph(PLG):
    def __init__(self,df,team_name,target_team):
        super().__init__(team_name,target_team)
        self.df  = df
        
    def 視覺化(self):
        #使用pivot_table將資料整理成可以視覺化的格式
        target_team_主場 = self.target_team + '主場'
        非target_team_主場 = '非'+self.target_team + '主場'
        df = self.df.pivot_table(index=0,columns=1,values=2).reset_index()

        color_dictionary  = {
            '鋼鐵人' : '#1c8cf2',
            '攻城獅' : '#2b185c',
            '夢想家' : '#8ee06b',
            '國王'   : '#edc754',
            '領航猿' : '#d57715',
            '勇士'   : '#0d5992'
        }

        df['color'] = df[0].map(color_dictionary)
        df['差距'] = df[target_team_主場] - df[非target_team_主場]
        df['差距'] = df['差距'].apply(lambda x:abs(x) if abs(x) >1 else 1)
        print(df['差距'])


        fig = go.Figure()
        fig.add_trace(go.Scatter(
                    x = df[target_team_主場],
                    y = df[非target_team_主場],
                    mode = 'markers',
                    marker=dict(
                        color = df['color'],
                        opacity=0.5,
                        size = df['差距']*5
                    ),
                    text = df[0],
                    hovertemplate = 非target_team_主場 + ': %{y}'+'<br>' + target_team_主場 + ': %{x}'+'<br>球隊: %{text}'
                ))
        fig.update_layout(
                    title = target_team_主場+'各隊罰球命中率比較',
                    xaxis=dict(
                        title= target_team_主場,
                        showgrid = False
                    ),
                    yaxis=dict(
                        title= 非target_team_主場,
                        showgrid = False
                    ),
                    paper_bgcolor='rgb(243, 243, 233)',
                    plot_bgcolor='rgb(243, 243, 233)',
                )
        fig.show()