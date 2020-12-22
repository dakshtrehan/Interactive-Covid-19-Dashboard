from django.shortcuts import render
import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.http import HttpResponse,HttpRequest
# Create your views here.
df = pd.read_csv('cdc_qa.csv',
                 header=0,
                 names=['Questions', 'Answers'])


df3 = pd.read_json(
    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')


def indexPage(request):
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()
    barPlotData = confirmedGlobal[[
        'Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData.columns = ['Country/Region', 'values']
    barPlotData = barPlotData.sort_values(by='values', ascending=False)
    barPlotVals = barPlotData['values'].values.tolist()
    countryNames = barPlotData['Country/Region'].values.tolist()
    # print("Country Names", countryNames)
    dataForMap = mapDataCal(barPlotData, countryNames)
    dataForheatMap, dateCat = getHeatMapData(confirmedGlobal, countryNames)
    showMap = "True"
    context = {'countryNames': countryNames, 'barPlotVals': barPlotVals,
               'totalCount': totalCount, 'dataForMap': dataForMap, 'showMap': showMap, 'dataForheatMap': dataForheatMap, 'dateCat': dateCat}
    return render(request, 'index.html', context)

InputCovid = []
welcomeResponse = []

def chatBot(request):
    
    if request.method == "POST":
        x = request.POST['message']
        welcome = "Chatbot : You are welcome.."
        bye = "Chatbot : Bye!!! "
       
        if x:
            vectorizer = CountVectorizer()
            count_vec = vectorizer.fit_transform(df['Questions']).toarray()
            welcome_input = ("hello", "hi", "greetings", "sup", "what's up","hey",)
            welcome_response = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

            def COVIDbot(user_response):
                text = vectorizer.transform([user_response]).toarray()
                df['similarity'] = cosine_similarity(count_vec, text)
                return df.sort_values(['similarity'], ascending=False).iloc[0]['Answers']
            
            def welcome(user_response):
                for word in user_response.split():
                    if word.lower() in welcome_input:
                        return random.choice(welcome_response)

            user_response = x
            user_response = user_response.lower()
            InputCovid.append(user_response)
            if(user_response not in ['bye','shutdown','exit', 'quit']):
                    if(welcome(user_response)!=None):
                        wResponse  = welcome(user_response)
                        welcomeResponse.append(wResponse)
                        # print('welcomeResponse',welcomeResponse)
                    else:
                        # print("Chatbot : ",end="")
                        cResponse = COVIDbot(user_response)
                        welcomeResponse.append(cResponse)
                        # print('welcomeResponse',welcomeResponse)

            welcomeCovidResponse = zip(InputCovid,welcomeResponse)
            context = {'welcomeCovidResp':welcomeCovidResponse} 
            return render(request,'chaty.html',context) 

    return render(request,'chaty.html')    

def mapDataCal(barPlotData, countryNames):

    dataForMap = []

    for i in countryNames:
        try:
            tempdf = df3[df3['name'] == i]
            temp = {}
            temp["code3"] = list(tempdf['code3'].values)[0]
            temp["name"] = i
            temp["value"] = barPlotData[barPlotData['Country/Region']
                                        == i]['values'].sum()
            temp["code"] = list(tempdf['code'].values)[0]
            dataForMap.append(temp)
        except:
            pass
    return dataForMap


def getHeatMapData(confirmedGlobal, countryNames):
    df3 = confirmedGlobal[list(
        confirmedGlobal.columns[1:2])+list(list(confirmedGlobal.columns.values)[-6:-1])]
    dataForheatMap = []
    for i in countryNames:
        try:
            tempdf = df3[df3['Country/Region'] == i]
            temp = {}
            temp["name"] = i
            temp["data"] = [{'x': j, 'y': k} for j, k in zip(
                tempdf[tempdf.columns[1:]].sum().index, tempdf[tempdf.columns[1:]].sum().values)]
            dataForheatMap.append(temp)
        except:
            pass
    dateCat = list(list(confirmedGlobal.columns.values)[-6:-1])
    # print("dateCat",dateCat)
    # print("dataForheatMap",dataForheatMap)
    return dataForheatMap, dateCat


def singleCountry(request):
    countryName = request.POST.get('countryName')
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()
    barPlotData = confirmedGlobal[[
        'Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData.columns = ['Country/Region', 'values']
    barPlotData = barPlotData.sort_values(by='values', ascending=False)
    barPlotVals = barPlotData['values'].values.tolist()
    countryNames = barPlotData['Country/Region'].values.tolist()
    showMap = "False"
    countryDataSingle = pd.DataFrame(
        confirmedGlobal[confirmedGlobal['Country/Region'] == countryName][confirmedGlobal.columns[4:-1]].sum()).reset_index()
    countryDataSingle.columns = ['country', 'values']
    countryDataSingle['lagVal'] = countryDataSingle['values'].shift(
        1).fillna(0)
    countryDataSingle['incrementVal'] = countryDataSingle['values'] - \
        countryDataSingle['lagVal']
    countryDataSingle['rollingMean'] = countryDataSingle['incrementVal'].rolling(
        window=4).mean()
    countryDataSingle = countryDataSingle.fillna(0)
    datasetsForLine = [{'yAxisID': 'y-axis-1', 'label': 'Daily Cumulated Data', 'data': countryDataSingle['values'].values.tolist(), 'borderColor':'#03a9fc', 'backgroundColor':'#03a9fc', 'fill':'false'},
                       {'yAxisID': 'y-axis-2', 'label': 'Rolling Mean 4 days', 'data': countryDataSingle['rollingMean'].values.tolist(), 'borderColor':'#fc5203', 'backgroundColor':'#fc5203', 'fill':'false'}]
    axisValue = countryDataSingle.index.tolist()
    dataForheatMap, dateCat = getHeatMapData(confirmedGlobal, countryNames)
    context = {'countryNames': countryNames, 'axisValue': axisValue, 'countryName': countryName, 'barPlotVals': barPlotVals,
               'totalCount': totalCount, 'showMap': showMap, 'datasetsForLine': datasetsForLine, 'dataForheatMap': dataForheatMap, 'dateCat': dateCat}
    return render(request, 'index.html', context)


def prediction(request):
    selectedCountry = "Worldwide"
    imagesAppend = "/static/img/totalp.png"
    imagesAppendR = "/static/img/totalp.png"
    
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()
    barPlotData = confirmedGlobal[[
        'Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData.columns = ['Country/Region', 'values']
    barPlotData = barPlotData.sort_values(by='values', ascending=False)
    barPlotVals = barPlotData['values'].values.tolist()
    countryNames = barPlotData['Country/Region'].values.tolist()
    choosedCountry = ["india","spain","italy","uk","us","france","germany"]
    if request.method == "POST":
        
        selectedCountry = request.POST.get('drop1')
        newSelectedCountry = selectedCountry.lower()
        if newSelectedCountry not in choosedCountry:
            imagesAppend = "/static/img/spainp.png"
            imagesAppendR = "/static/img/spainr.png"
        else:
            imagesAppend = "/static/img/" + newSelectedCountry + "p.png"
            imagesAppendR = "/static/img/" + newSelectedCountry + "r.png"
        return render(request,'prediction.html',{'Country':countryNames,'selectedCountry':newSelectedCountry,'imagesAppend':imagesAppend,'imagesAppendR':imagesAppendR})

    # print("Country Names", countryNames)
    return render(request,'prediction.html',{'Country':countryNames,'selectedCountry':selectedCountry,'imagesAppend':imagesAppend,'imagesAppendR':imagesAppendR})