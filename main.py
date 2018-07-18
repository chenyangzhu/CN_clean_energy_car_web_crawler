__author__ = 'Klaus'
__credits__ = 'Shiqi Hou'

'''
This Python file is intended to grab new energy cars infos.

LICENSE: under MIT license.
'''


from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import sys

orig_stdout = sys.stdout

URL = 'http://123.127.164.29:18082/CVT/Jsp/zjgl/nerds/201807.html'

def get_car_list():

    try:
        html = BeautifulSoup(urlopen(URL))
    except:
        raise ValueError('Wrong URL or Network Problem')

    print('Data Downloaded Successfully.....')
    print('##############################')

    counter = 0
    car_list = []
    for each_data in html.find_all("div",{'id':'divBody'}):
            if counter ==0 :
                counter +=1
                continue

            for ct, each_title in enumerate(each_data.find_all('strong')):
                name = each_title.get_text(strip = True)
                #print(name)

                # -----------------处理 title 信息---------------------
                if ct == 0:
                    _list = re.split(r"\xa0|、",name)
                    temp = None
                    try:
                        temp = _list[4]
                        del _list[4]
                    except:
                        pass
                    for count, word in enumerate(_list[3]):
                        if word == "纯" or word == "燃"or word == "插":
                            each_id = _list[3][:count]
                            #print(each_id)
                            _list.append(each_id)
                            each_function = _list[3][count:]
                            #print(each_function)
                            _list.append(each_function)
                            del _list[3]
                    if temp:
                        _list.append(temp)

                # ------------处理配置id--------------
                if ct == 2 or ct == 3:
                    if name[0] != '二': # 这里是因为处理到扩展车型时，会出错。
                        _list.append(name[6:])
            #print(_list)

            try:
                if _list[-3][0] == 'N' and _list[-2][0] =='N':
                    each_car_1 = {'company':_list[1],
                       'brand':_list[2],
                       'Type':_list[3],
                       'Kind':_list[4],
                       'ID':_list[-3]}
                    each_car_2 = {'company':_list[1],
                       'brand':_list[2],
                       'Type':_list[3],
                       'Kind':_list[4],
                       'ID':_list[-2]}
                    each_car_2 = {'company':_list[1],
                       'brand':_list[2],
                       'Type':_list[3],
                       'Kind':_list[4],
                       'ID':_list[-1]}
                    for each_table in each_data.find_all('table',{'class':"list-table"}):
                        for each_row in each_table.find_all('tr')[1:]:
                            #print(each_row)
                            label = each_row.find('th').get_text()[:-1]
                            data1,data2,data3 = each_row.find_all('td')
                            data1 = data1.get_text(strip = True)
                            data2 = data2.get_text(strip = True)
                            data3 = data3.get_text(strip = True)
                            each_car_1[label]= data1
                            each_car_2[label] = data2
                            each_car_3[label] = data3
                elif _list[-2][0] == 'N':
                    # ------------------针对双id进行处理----------------------
                    each_car_1 = {'company':_list[1],
                       'brand':_list[2],
                       'Type':_list[3],
                       'Kind':_list[4],
                       'ID':_list[-2]}
                    each_car_2 = {'company':_list[1],
                       'brand':_list[2],
                       'Type':_list[3],
                       'Kind':_list[4],
                       'ID':_list[-1]}
                    #print(each_car_1)
                    #print(each_car_2)
                    for each_table in each_data.find_all('table',{'class':"list-table"}):
                        for each_row in each_table.find_all('tr')[1:]:
                            #print(each_row)
                            label = each_row.find('th').get_text()[:-1]
                            data1,data2 = each_row.find_all('td')
                            data1 = data1.get_text(strip = True)
                            data2 = data2.get_text(strip = True)
                            each_car_1[label]= data1
                            each_car_2[label] = data2
                    #print(each_car_1)
                    #print(each_car_2)
                    car_list.append(each_car_1)
                    car_list.append(each_car_2)
                else:
                    pass
                    total_number = 1
                    each_car_1 = {'company':_list[1],
                                   'brand':_list[2],
                                   'Type':_list[3],
                                   'Kind':_list[4],
                                   'ID':_list[-1]}
                    #print(each_car_1)
                    # ------------------- search for cars' detail --------------------
                    for each_table in each_data.find_all('table',{'class':"list-table"}):
                        for each_row in each_table.find_all('tr')[1:]:
                            #print(each_row)
                            label = each_row.find('th').get_text()[:-1]
                            data = each_row.find('td').get_text(strip = True)
                            #print(label,data)
                            each_car_1[label] = data
                            #print("****")
                    #print(each_car_1)
                    car_list.append(each_car_1)
            except:
                print(">>>number#",_list[0],'failed. Please insert manually. Its id is',_list[3])
    return car_list

def write_to_excel(car_list):
    car_list_pd = None
    for cter, each_car in enumerate(car_list):
        each_car_pd = pd.DataFrame(data = list(each_car.values()), index = list(each_car.keys()))
        if cter == 0:
            car_list_pd = each_car_pd
        else:
            car_list_pd= pd.concat([car_list_pd, each_car_pd], axis = 1)
    car_list_pd = car_list_pd.T
    writer = pd.ExcelWriter('./output.xlsx')
    car_list_pd.to_excel(writer)

def main():
    f = open('log.txt', 'w')
    sys.stdout = f

    print('Downloading Data...')
    car_list = get_car_list()
    print(len(car_list),' Cars have been downloaded. \n\n***Attention***:\nFirst car in each section is ommited for simplicity.\nIf you want these two infos, please insert them manually.')
    write_to_excel(car_list)
    print('Done. Please find the excel in the folder where this program is located')

    sys.stdout = orig_stdout
    f.close()

if __name__ == '__main__':
    main()
