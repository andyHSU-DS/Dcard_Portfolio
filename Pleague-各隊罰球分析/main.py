import pandas as pd
import requests
import bs4
import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import re

from module.module_copy import PLG, PLG_Graph

data_frame_list = pd.DataFrame()
all_team  = ['鋼鐵人','攻城獅','領航猿','國王','勇士','夢想家']
for a_team in all_team:
    for b_team in all_team:
            team          = PLG(team_name = b_team,target_team = a_team)
            team_info     = team.get_team_info()
            matchup       = team.matchup_and_host_info()
            team_完整_info = team.match資訊(team_info, matchup)
            整理完成資料    = team.資料處理(team_完整_info)
            各隊最終資料    = team.資料彙整(整理完成資料)
            data_frame_list = data_frame_list.append(各隊最終資料)
    print(a_team)
    Graph_DF = PLG_Graph(df = data_frame_list, team_name = 'abc', target_team = a_team)
    Graph_DF.視覺化()

data_frame_list.to_csv('output/Final_Output.csv',index=False,header=True,encoding='utf-8-sig')