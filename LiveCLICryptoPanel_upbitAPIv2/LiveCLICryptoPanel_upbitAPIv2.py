# -*- coding: utf-8 -*-

import requests
import plotext as plt
from datetime import datetime

# Retrieve minute candle minute data from Upbit API
def getCryptoCandleMinuteData(cryptoName, queryQty):
    queryURL = f"https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/1?code=CRIX.UPBIT.KRW-{cryptoName}&count={queryQty}"

    response = requests.request("GET", queryURL)
    
    return response.json()


# Analyize and process the data
def processCryptoCandleMinuteData(cryptoName, rawAPIResponseData):

    timelineKST = list()
    candleAccTradeVolume = list()

    # process the whole API response data (example)
    for sequence in range(len(rawAPIResponseData)):
        candleAccTradeVolume.append(round(rawAPIResponseData[sequence]["candleAccTradeVolume"]))
        timelineKST.append(str(rawAPIResponseData[sequence]["candleDateTimeKst"]).replace('T',' ')[:19])
        timelineKST[sequence] = datetime.strptime(timelineKST[sequence], "%Y-%m-%d %H:%M:%S").strftime('%d/%m/%Y %H:%M:%S')

        print(f"{timelineKST[sequence]} ~ {candleAccTradeVolume[sequence]}")

    # draw plotext graph
    plt.bar(timelineKST, candleAccTradeVolume)
    plt.canvas_color('none')
    plt.axes_color('none')
    plt.ticks_color('none')
    plt.xlabel("시간")
    plt.ylabel(f"거래소 암호화폐 거래량({cryptoName}/Min)")
    plt.plotsize(140, 20)
    plt.show()
    

cryptoName = "ETH"
rawAPIResponseData = getCryptoCandleMinuteData(cryptoName, 60)
processCryptoCandleMinuteData(cryptoName, rawAPIResponseData)