from colorama.ansi import Back, Fore, Style
import requests
import json
import datetime
from time import sleep
import os
import sys

# create upbit API query URL according to current market code
def createQueryURL():
    queryURL = "https://api.upbit.com/v1/market/all"

    try:
        upbitCryptoMarketCode = requests.get(queryURL)
        upbitCryptoMarketCode.encoding = 'UTF-8'
    except:
        # unexpected error occured
        return "createQueryURLFailed"

    upbitCryptoMarketCode = json.loads(upbitCryptoMarketCode.text)

    APIqueryURL = "https://api.upbit.com/v1/ticker?markets="

    for sequence in upbitCryptoMarketCode:
        if "KRW-" in sequence["market"]:
            APIqueryURL += sequence["market"] 
            APIqueryURL += ","

    # We have to delete unnecessary last appended comma(",") to create valid query URL
    APIqueryURL = APIqueryURL[:-1]
    
    return APIqueryURL


# gather necessary information
def gatherInformation(APIqueryURL):

    if APIqueryURL == "createQueryURLFailed":
        return "APIqueryURLFailed"

    try:
        # cryptocurrency information
        responseCryptoAPI = requests.get(APIqueryURL)
        responseCryptoAPI.encoding = 'UTF-8'
    except:
        # unexpected error occured
        return "UnexpectedErrorAtGatheringInformation"

    cryptoDataBundle = json.loads(responseCryptoAPI.text)

    # print(cryptoDataBundle[0]["market"])
    return cryptoDataBundle


def cryptoDataProcessing(APIqueryURL, cryptoShowQuantity):

    cryptoDataBundle = gatherInformation(APIqueryURL)

    # error handling
    if cryptoDataBundle == "APIqueryURLFailed":
        return "APIqueryURLFailed"
    elif cryptoDataBundle == "UnexpectedErrorAtGatheringInformation":
        return "UnexpectedErrorAtGatheringInformation"

    try:
        # sort data(dictionary in list) as descending order according to the 24h trade volume
        cryptoDataBundle = sorted(cryptoDataBundle, key = lambda x:x["acc_trade_price_24h"], reverse = True)

        os.system("cls")

        print(" 종목         가격           변동량(변동률)         24시간 고가      24시간 저가                    24시간 거래량")
        print("=============================================================================================================================================")

        #for sequence in range(len(cryptoDataBundle)):          # if you want to show everything..
        for sequence in range(cryptoShowQuantity):   
            symbol = cryptoDataBundle[sequence]["market"][4:]           # ex) KRW-BTC   ---> BTC
            currentPrice = "{:,}".format(round(cryptoDataBundle[sequence]["trade_price"]))
            highPrice = "{:,}".format(round(cryptoDataBundle[sequence]["high_price"]))
            lowPrice = "{:,}".format(round(cryptoDataBundle[sequence]["low_price"]))
            changePrice = "{:,}".format(round(cryptoDataBundle[sequence]["signed_change_price"]))
            realChangeRate = cryptoDataBundle[sequence]["signed_change_rate"]               # accurate change rate. no ceiling. to decide if crypto went up or down or even.
            changeRate = "{:.3f}".format(cryptoDataBundle[sequence]["signed_change_rate"])
            accumulatedTradePrice24hr = "{:,}".format(round(cryptoDataBundle[sequence]["acc_trade_price_24h"]))
            accumulatedTradeVolume24hr = "{:,.2f}".format(round(cryptoDataBundle[sequence]["acc_trade_volume_24h"], 2))


            if realChangeRate > 0:            # price went up
                changePrice = Fore.RED + str(changePrice) + " " + Style.RESET_ALL
                changeRate = Fore.RED + str(changeRate) + "%" + Style.RESET_ALL
                changeArrow = Fore.RED + "▲" + Style.RESET_ALL
            elif realChangeRate < 0:          # price went down
                changePrice = Fore.BLUE + str(changePrice) + " " + Style.RESET_ALL
                changeRate = Fore.BLUE + str(changeRate) + "%" + Style.RESET_ALL
                changeArrow = Fore.BLUE + "▼" + Style.RESET_ALL
            elif realChangeRate == 0:                                  # even
                changePrice = Fore.WHITE + str(changePrice) + " " + Style.RESET_ALL
                changeRate = Fore.WHITE + "0.000%" + Style.RESET_ALL
                changeArrow = Fore.WHITE + "■" + Style.RESET_ALL

            # print information!
            print("{0:^6} | ₩ {1:>11} ( {2:>20}~{3:>17} {4}) | ₩ {5:>11} | ₩ {6:>11} | ₩ {7:>19} ( ≈{8:>20} {9:^5}) ".
                format(symbol, currentPrice, changePrice, changeRate, changeArrow, highPrice, lowPrice,
                accumulatedTradePrice24hr, accumulatedTradeVolume24hr, symbol))
    except:
        return "unexpectedErrorAtCryptoDataProcessing"

    return "successfulProcessing"

def runProgram():

    # refresh interval to get and process a new data
    refreshInterval = 2

    updateCycleCount = 0
    apiCallFailedCount = 0
    exceptionCount = 0
    uptimeRatio = 0

    print("*Note : It is shown as the descending order of market cap. | *참고 : 시가총액 기준 내림차순 순서대로 보여집니다.")
    cryptoShowQuantity = int(input("How many cryptos to livestream? [1~75] : "))
    if cryptoShowQuantity < 1 or cryptoShowQuantity > 75:
        sys.exit("Check your quantity input and try again. It's wrong input.")

    APIqueryURL = createQueryURL()

    while True:
        # os.system("cls")                      # <-- to reduce void screen time, I inserted this into function cryptoDataProcessing()
        now = datetime.datetime.now()

        # run!
        runtimeResult = cryptoDataProcessing(APIqueryURL, cryptoShowQuantity)
        
        # runtime procedure verification
        if runtimeResult == "successfulProcessing":
            updateCycleCount += 1
        elif runtimeResult == "APIqueryURLFailed":
            apiCallFailedCount += 1
            print("API call creation failed. Retry in 2 seconds. | API 요청 제작 실패. 2초 내 재시도합니다.")
        elif runtimeResult == "UnexpectedErrorAtGatheringInformation":
            exceptionCount += 1
            print("Unexpected error occured at gathering information. Retry in 2 seconds. | 데이터 수집중 예상치 못한 오류 발생. 2초 내 재시도합니다.")
        elif runtimeResult == "unexpectedErrorAtCryptoDataProcessing":
            exceptionCount += 1
            print("Unexpected error occured at data processing. Retry in 2 seconds. | 데이터 처리중 예상치 못한 오류 발생. 2초 내 재시도합니다.")

        if apiCallFailedCount == 0 and exceptionCount == 0:
            uptimeRatio = 100
        else:
            uptimeRatio = "{:.2f}".format((updateCycleCount * 100) / (apiCallFailedCount + exceptionCount))
        
        # runtime log
        print("")
        print("============================================================================================================================================")
        print("업데이트 시각 : {} | 업데이트 횟수 : {} 회 | API Call 실패 : {} 회 | 기타 에러 : {} 회 | Uptime 비율 : {} % "
                    .format(now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초'), updateCycleCount, apiCallFailedCount, exceptionCount, uptimeRatio))
        print("============================================================================================================================================")
        print("powered by UPBIT. created by LUMINOUS(blog.naver.com/agerio100 | agerio100@naver.com)")

        # wait for designated refresh interval
        sleep(refreshInterval)


if __name__ == "__main__":
    runProgram()