from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import dateparser 

app = Flask(__name__) #don't change this code

def scrap(url):
    #function for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information from the website
    table = soup.find('table',attrs={'class':'centerText newsTable2'}) 
    tr = table.find_all('tr') 

    temp = [] #initiating a tuple
        #name_of_object = row.find_all(...)[0].text
    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
        
        tanggal = row.find_all('td')[0].text
        tanggal = tanggal.strip()

        ask = row.find_all('td')[1].text
        ask = ask.strip()

        bid = row.find_all('td')[2].text
        bid = bid.strip()
       
        
        #append the needed information 
        temp.append((tanggal,ask,bid)) 
    
    
        #creating the dataframe
        df = pd.DataFrame(temp, columns = ('Date','Sell','Buy')) 
        
        #data wranggling 
        df['Buy'] = df['Buy'].apply(lambda x:x.replace(',','.'))
        df['Sell'] = df['Sell'].apply(lambda x:x.replace(',','.'))
        df[['Sell','Buy']] = df[['Sell','Buy']].astype('float64')
        df['Date'] = df['Date'].apply(dateparser.parse)
        df['Date'] = pd.to_datetime(df['Date'],format=('%d-%m%Y'))
   

    return df

@app.route("/")
def index():
    df = scrap('https://news.mifx.com/kurs-valuta-asing?kurs=JPY') 

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.set_index('Date').plot(title='Currency Exchange JPY to IDR')
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
