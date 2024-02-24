#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import pandas as pd 
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

if __name__=='__main__':
    if len(sys.argv)==1:
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files('ivanchvez/causes-of-death-our-world-in-data', unzip=True)
        data=pd.read_csv('20220327 annual-number-of-deaths-by-cause.csv')
        mean_death=[]
        conti=['Africa','Asia','Australia','Europe','North America']
        for i in conti:
            d=data[data['Entity']==i]
            dd=d['Deaths - Diabetes mellitus - Sex: Both - Age: All Ages (Number)']
            l=[]
            for j in dd:
                l.append(j)
            a=sum(l)/len(l)
            mean_death.append(a)
            year=list(range(1990, 2020))
            plt.plot(year,l,label=i)
    
        # The number of people dead from diabetas for South America is called Latin america here
        conti.append('South America')
        s=data[data['Entity']=='Latin America & Caribbean - World Bank region']
        ss=s['Deaths - Diabetes mellitus - Sex: Both - Age: All Ages (Number)']
        ll=[]
        for i in ss:
            ll.append(i)
        plt.plot(year,ll,label='South America')
        plt.legend()
        plt.title('Death Number Trend in Each Continent')
        plt.show()
        mean_death.append(sum(ll)/len(ll))
        dic={'Continents':conti,'Avg_death_number':mean_death}
        data1=pd.DataFrame(data=dic)
         # Scraping for ingredents
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

        response=requests.get('https://www.topinspired.com/top-10-best-recipes-from-each-continent/',headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        # For dishs name
        c=soup.find_all('h4')
        c_name=[]
        new=[]
        for i in c:
            c_name.append(i.text.strip())
        for i in c_name:
            if i=='':
                pass
            elif '\xa0' in i:
                j=i.replace('\xa0',' ')
                new.append(j)
            else:
                new.append(i)
        # For recipes 
        ing=soup.find('div',class_=["entry-content","jpibfi_container"])
        all_str=[]
        p_h4=[]
        only_p=[]
        reci=[]
        recipe=[]
        cnt=0
        for i in ing:
            all_str.append(str(i))
        for i in all_str:
            if i.startswith('<p>') or i.startswith('<h4'):  
                p_h4.append(i)
        p_h4=p_h4[3:]
        for i in p_h4:
            if i.startswith('<h4'):
                cnt=0
            elif i.startswith('<p>'):
                cnt+=1
            if cnt==3:
                only_p.append(i)
            elif i.startswith('<p>Meat') or i.startswith('<p><strong>Meat'):
                only_p.append(i)
        for i in only_p:
            z=re.findall(r'(?:</?[a-z]+>)',i) ## Remove the tags in the sentence
            for j in z:
                i=i.replace(j,'')
            reci.append(i)
        for i in reci:
            if '\xa0' in i:
                j=i.replace('\xa0',' ')
                recipe.append(j)
            else:
                recipe.append(i)
        ## Patch dishes and recipes
        g={'Dishes':new,'Recipes': recipe}
        df=pd.DataFrame(data=g)
        ## Substitude ingrendients
        pq=[]
        kl=[]
        api_key='L2NFsoG3YLESF7jOOQyDkOcZkYlUyHQQbebI8Gko'
        base_url='https://api.nal.usda.gov/fdc/v1/foods/search?query='
        for m in df['Recipes']:
            mm=re.findall(r'(?:[\.,;!()])',m)
            for j in mm:
                m=m.replace(j,'')
            kl.append([m])
        for k in kl:
            pp=[]
            for m in k:
                gg=m.split(' ')
                for v in gg:
                    url=f'{base_url}{v}&requireAllWords=True&api_key={api_key}'
                    r=requests.get(url)
                    j=r.json()
                    ss=j.get('totalHits')
                    if ss!=0:
                        try:
                            qq=j.get('foods')[0].get('foodNutrients')[3].get('nutrientNumber')
                            pp.append(float(qq))
                        except:
                            pass
                    else:
                        pass
            avg=sum(pp)/len(pp)
            pq.append(avg)
        di_cal={'Dishes':new,'Calories':pq}
        df2=pd.DataFrame(data=di_cal)
        df3=pd.merge(df,df2,on='Dishes')
        ttl_cal=[]
        c_nt=0
        for i in range(len(pq)):
            if i%10==0 and i<=50:
                total_cal=sum(pq[i:i+9])
                ttl_cal.append(total_cal)
                i+=10
        df3=pd.merge(df,df2,on='Dishes')
        ttl_cal=[]
        c_nt=0
        for i in range(len(pq)):
            if i%10==0 and i<=50:
                total_cal=sum(pq[i:i+9])
                ttl_cal.append(total_cal)
                i+=10
        con_cal={'Continents':conti,'Calories':ttl_cal}
        df4=pd.DataFrame(data=con_cal)
        df5=pd.merge(data1,df4,on='Continents')
        print('Correlation table is:')
        print(df5.corr())
        r,p=stats.pearsonr(df5.Avg_death_number,df5.Calories)
        print('correlation is ',round(r,4))
        print('p-value is ',round(p,4))
        
    elif len(sys.argv)==2:
        if sys.argv[1]=='--static':
            d1=pd.read_csv('./datasets/Death_number.csv')
            d2=pd.read_csv('./datasets/Dishes_Calories.csv')
            d3=pd.read_csv('./datasets/Dishes_Recipes.csv')
            # Visualizied the death number in different continents
            mean_death=[]
            conti=['Africa','Asia','Australia','Europe','North America']
            for i in conti:
                d=d1[d1['Entity']==i]
                dd=d['Deaths - Diabetes mellitus - Sex: Both - Age: All Ages (Number)']
                l=[]
                for j in dd:
                    l.append(j)
                a=sum(l)/len(l)
                mean_death.append(a)
                year=list(range(1990, 2020))
                plt.plot(year,l,label=i)
    
            # The number of people dead from diabetas for South America is called Latin america here
            conti.append('South America')
            s=d1[d1['Entity']=='Latin America & Caribbean - World Bank region']
            ss=s['Deaths - Diabetes mellitus - Sex: Both - Age: All Ages (Number)']
            ll=[]
            for i in ss:
                ll.append(i)
            plt.plot(year,ll,label='South America')
            plt.legend()
            plt.title('Death Number Trend in Each Continent')
            plt.show()
            # Analysis
            d4=pd.read_csv('./datasets/combined_data.csv')
            print('Correlation table is:')
            print(d4.corr())
            r,p=stats.pearsonr(d4.Avg_death_number,d4.Calories)
            print('correlation is ',round(r,4))
            print('p-value is ',round(p,4))
            print(d1)
            print(d2)
            print(d3)


# In[ ]:




