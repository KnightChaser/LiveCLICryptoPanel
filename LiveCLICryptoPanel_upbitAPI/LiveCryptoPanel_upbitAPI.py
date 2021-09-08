from colorama.ansi import Back, Fore, Style     # colorize to emphasize and highlight the important information
import requests                                 # getting information from UPBIT API
import json                                     # process raw data from UPBIT API which consisted of JSON data
import datetime                                 # print updating time
from time import sleep                          # set updating period
import os                                       # to command operating system command
import sys                                      # to terminate program
import timeit                                   # to measure program performance (every procedure)

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
        # we won't support USDT market because its trading volume is too small
        if "KRW-" in sequence["market"] or "BTC-" in sequence["market"] :
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

    try:
        cryptoDataBundle = json.loads(responseCryptoAPI.text)
        return cryptoDataBundle
    except:
        return "JSONDecodeErrorAtGatheringInformation"


def cryptoDataProcessing(cryptoDataBundle, dataSortCriterion, sortDirection):

    # error handling
    if cryptoDataBundle in ["APIqueryURLFailed", "UnexpectedErrorAtGatheringInformation", "JSONDecodeErrorAtGatheringInformation"]:
        return cryptoDataBundle

    # how much money have traded in recent 24 hour?
    totalUPBITKRWMarketTradePrice24hr = 0               # KRW Market
    totalUPBITBTCMarketTradePrice24hr = 0               # BTC Market

    # for BTC market
    currentBTCprice = float(round(cryptoDataBundle[0]["trade_price"]))          # <-- Its orginal value type was <class='str'>

    # sort data(dictionary in list) as descending order according to the 24h trade volume
    # Do completion enumeration and convert BTC market coin into KRW currency
    for sequence in range(len(cryptoDataBundle)):
        if "BTC-" in cryptoDataBundle[sequence]["market"]:
            cryptoDataBundle[sequence]["acc_trade_price_24h"] *= currentBTCprice
            totalUPBITBTCMarketTradePrice24hr += cryptoDataBundle[sequence]["acc_trade_price_24h"]
            # previousCryptoKRWprice[cryptoDataBundle[sequence]["market"]] = cryptoDataBundle[sequence]["acc_trade_price_24h"]  # store price data
        else:
            totalUPBITKRWMarketTradePrice24hr += cryptoDataBundle[sequence]["acc_trade_price_24h"]
            # previousCryptoKRWprice[cryptoDataBundle[sequence]["market"]] = cryptoDataBundle[sequence]["acc_trade_price_24h"]  # store price data

    # Sort data as criteria with KRW value.
    if sortDirection == 2:              # descending order
        cryptoDataBundle = sorted(cryptoDataBundle, key = lambda x:x[dataSortCriterion], reverse = True)
    else:
        cryptoDataBundle = sorted(cryptoDataBundle, key = lambda x:x[dataSortCriterion], reverse = False)

    return "DataProcessingSuccessful", cryptoDataBundle, totalUPBITKRWMarketTradePrice24hr, totalUPBITBTCMarketTradePrice24hr, currentBTCprice


def cryptoDataPrinting(cryptoDataBundle, previousCryptoValueChange, cryptoShowQuantity, totalUPBITKRWMarketTradePrice24hr, totalUPBITBTCMarketTradePrice24hr, currentBTCprice):

    try:

        os.system("cls")

        print("  종목    마켓        가격                 변동량(변동률)              24시간 고가      24시간 저가                    24시간 거래량")
        print("==========================================================================================================================================================")

        #for sequence in range(len(cryptoDataBundle)):          # if you want to show everything..
        for sequence in range(cryptoShowQuantity):   
            market = cryptoDataBundle[sequence]["market"]
            symbol = cryptoDataBundle[sequence]["market"][4:]           # ex) KRW-BTC   ---> BTC
            
            # No relationship between whether current market is BTC-related or KRW-related
            changeRate = "{:.3f}".format(cryptoDataBundle[sequence]["signed_change_rate"] * 100)
            realChangeRate = cryptoDataBundle[sequence]["signed_change_rate"]              # accurate change rate. no ceiling. to decide if crypto went up or down or even.
            accumulatedTradeVolume24hr = "{:,.2f}".format(round(cryptoDataBundle[sequence]["acc_trade_volume_24h"], 2))

            # if we're seeking BTC market
            if "BTC-" in cryptoDataBundle[sequence]["market"]:
                currentPrice = "{:,}".format(round(cryptoDataBundle[sequence]["trade_price"] * currentBTCprice))
                highPrice = "{:,}".format(round(cryptoDataBundle[sequence]["high_price"] * currentBTCprice))
                lowPrice = "{:,}".format(round(cryptoDataBundle[sequence]["low_price"] * currentBTCprice))
                changePrice = "{:,}".format(round(cryptoDataBundle[sequence]["signed_change_price"] * currentBTCprice))
                accumulatedTradePrice24hr = "{:,}".format(round(cryptoDataBundle[sequence]["acc_trade_price_24h"]))     # it's already multiplied
                marketType = "BTC"

            # or, if we're seeking KRW market
            elif "KRW-" in cryptoDataBundle[sequence]["market"]:
                currentPrice = "{:,}".format(round(cryptoDataBundle[sequence]["trade_price"]))
                highPrice = "{:,}".format(round(cryptoDataBundle[sequence]["high_price"]))
                lowPrice = "{:,}".format(round(cryptoDataBundle[sequence]["low_price"]))
                changePrice = "{:,}".format(round(cryptoDataBundle[sequence]["signed_change_price"]))
                accumulatedTradePrice24hr = "{:,}".format(round(cryptoDataBundle[sequence]["acc_trade_price_24h"]))
                marketType = "KRW"
            

            if realChangeRate > 0:            # price went up
                changePrice = Fore.RED + Style.BRIGHT + str(changePrice) + " " + Style.RESET_ALL
                changeRate = Fore.RED + Style.BRIGHT + str(changeRate) + "%" + Style.RESET_ALL
                changeArrow = Fore.RED + Style.BRIGHT + "▲" + Style.RESET_ALL
            elif realChangeRate < 0:          # price went down
                changePrice = Fore.BLUE + Style.BRIGHT + str(changePrice) + " " + Style.RESET_ALL
                changeRate = Fore.BLUE + Style.BRIGHT + str(changeRate) + "%" + Style.RESET_ALL
                changeArrow = Fore.BLUE + Style.BRIGHT + "▼" + Style.RESET_ALL
            elif realChangeRate == 0:                                  # even
                changePrice = Fore.WHITE + Style.BRIGHT + str(changePrice) + " " + Style.RESET_ALL
                changeRate = Fore.WHITE + Style.BRIGHT + "0.000%" + Style.RESET_ALL
                changeArrow = Fore.WHITE + Style.BRIGHT + "~" + Style.RESET_ALL

            # 
            if cryptoDataBundle[sequence]["market"] not in previousCryptoValueChange:
                # previousCryptoValueChange = {cryptoDataBundle[sequence]["market"] : realChangeRate}
                liveCryptoValueChangeDirection = Back.GREEN + Fore.WHITE + Style.BRIGHT + "준비중 ＠" + Style.RESET_ALL
            else:

                if realChangeRate > previousCryptoValueChange.get(market):        # going up
                    liveCryptoValueChangeDirection = Back.RED + Fore.WHITE + Style.BRIGHT + "상승세 ↑" + Style.RESET_ALL
                elif realChangeRate < previousCryptoValueChange.get(market):
                    liveCryptoValueChangeDirection = Back.BLUE + Fore.WHITE + Style.BRIGHT + "하락세 ↓" + Style.RESET_ALL
                elif realChangeRate == previousCryptoValueChange.get(market):
                    liveCryptoValueChangeDirection = Fore.WHITE + Style.BRIGHT + "보합세 ↔" + Style.RESET_ALL


            # print information!
            print("{0:^7} | {1} | ₩ {2:>11} ( {3:>25}~{4:>23} {5} {6}) | ₩ {7:>11} | ₩ {8:>11} | ₩ {9:>19} ( ≈{10:>20} {11:^7}) ".
                format(symbol, marketType, currentPrice, changePrice, changeRate, changeArrow, liveCryptoValueChangeDirection,
                    highPrice, lowPrice, accumulatedTradePrice24hr, accumulatedTradeVolume24hr, symbol))

            # save previous data
            previousCryptoValueChange[cryptoDataBundle[sequence]["market"]] = realChangeRate

        print("")
        exchangeTradingVolumeNotificationMessage = Back.CYAN + Fore.WHITE + Style.BRIGHT + "[UPBIT 최근 24시간 거래량] KRW마켓 ≈ ₩ {:,} | BTC마켓 ≈ ₩ {:,} | 합산 ≈ ₩ {:,}".format(
                    round(totalUPBITKRWMarketTradePrice24hr), round(totalUPBITBTCMarketTradePrice24hr),
                    round(totalUPBITKRWMarketTradePrice24hr + totalUPBITBTCMarketTradePrice24hr)) + Style.RESET_ALL

        print(exchangeTradingVolumeNotificationMessage)

    except:
        return "unexpectedErrorAtCryptoDataProcessing", previousCryptoValueChange


    return "everythingWasSuccessful", previousCryptoValueChange



def runProgram():

    ####################################### user preference selection ####################################################
    os.system("cls")

    cryptoShowQuantity = int(input("How many cryptos to livestream? | 실시간으로 현황을 보실 종목은 몇 개 입니까? [1~75] : "))
    if cryptoShowQuantity < 1 or cryptoShowQuantity > 75:
        sys.exit("Check your quantity input and try again. It's wrong input. | 수량 입력을 확인하신 후 재시도 해 보세요. 잘못된 입력입니다.")
    os.system("cls")

    print("""*[1 : 가격(selection)] / [2 : 변동량(Change quantity)] / [3 : 변동률(Change rate)] /
        [4 : 24시간 고가(24hr high price)] / [5 : 24시간 저가(24hr low price)] / [6 : 24시간 거래량(24hr trade volume)] """)
    dataSortCriterionNumber = int(input("By what criteria would you like to sort your data? | 어떤 기준에 의해 데이터를 정렬하실 건가요? : "))
    if dataSortCriterionNumber < 1 or dataSortCriterionNumber > 6:
        sys.exit("Check your selection and try again. It's wrong input. | 선택 입력을 확인하신 후 재시도 해 보세요. 잘못된 입력입니다.")
    os.system("cls")

    supportedSelection = { 1 : "trade_price",
                           2 : "signed_change_price",
                           3 : "signed_change_rate",
                           4 : "high_price",
                           5 : "low_price",
                           6 : "acc_trade_price_24h"
                            }

    dataSortCriterion = supportedSelection[dataSortCriterionNumber]


    print("*[1 : 오름차순(ascending)] / [2 : 내림차순(descending)]")
    sortDirection = int(input("Select order direction. | 정렬 기준을 선택하세요.  : "))
    if sortDirection not in [1, 2]:
        sys.exit("Check your selection and try again. It's wrong input. | 선택 입력을 확인하신 후 재시도 해 보세요. 잘못된 입력입니다.")
    os.system("cls")

    # refresh interval to get and process a new data
    refreshInterval = 2

    updateCycleCount = 0
    apiCallFailedCount = 0
    exceptionCount = 0
    uptimeRatio = 0


    # Add extra arrow direction to express whether price went up or down than last update value
    # store exactly-recent data
    previousCryptoValueChange = {"init" : -1}

    #######################################################################################################################

    # Initalization essential operation : create API query URL
    APIqueryURL = createQueryURL()

    while True:

            startPerformanceMeasurement = timeit.default_timer()
        
            # os.system("cls")                      # <-- to reduce void screen time, I inserted this into function cryptoDataProcessing()
            now = datetime.datetime.now()

            # gathering data
            cryptoDataBundle = gatherInformation(APIqueryURL)

            try:

                # dataprocessing
                # Flag, cryptoDataBundle, totalUPBITKRWMarketTradePrice24hr, totalUPBITBTCMarketTradePrice24hr, currentBTCprice = cryptoDataProcessing(APIqueryURL, dataSortCriterion, sortDirection)
                FLAG, cryptoDataBundle, totalUPBITKRWMarketTradePrice24hr, totalUPBITBTCMarketTradePrice24hr, currentBTCprice = cryptoDataProcessing(cryptoDataBundle, dataSortCriterion, sortDirection)

                # data printing (do only data processing process was done without any error)
                if FLAG == "DataProcessingSuccessful":
                    FLAG, previousCryptoValueChange = cryptoDataPrinting(cryptoDataBundle, previousCryptoValueChange, cryptoShowQuantity, totalUPBITKRWMarketTradePrice24hr, totalUPBITBTCMarketTradePrice24hr, currentBTCprice)

            except:

                # set flag as failure and retry
                FLAG == "unexpectedErrorAtCryptoDataProcessing"

            # if everything went successfully
            if FLAG == "everythingWasSuccessful":
                updateCycleCount += 1

                if apiCallFailedCount == 0 and exceptionCount == 0:
                    uptimeRatio = 100
                else:
                    uptimeRatio = "{:.2f}".format((updateCycleCount * 100) / (updateCycleCount + apiCallFailedCount + exceptionCount))

                finishPerformanceMeasurement = timeit.default_timer()
                
                # runtime log
                print("==========================================================================================================================================================")
                print("업데이트 시각 : {} | 업데이트 횟수 : {:,} 회 | API Call 실패 : {:,} 회 | 기타 에러 : {:,} 회 | Uptime 비율 : {} % | {:.3f} sec/process"
                            .format(now.strftime('%Y. %m. %d. %H:%M:%S'), updateCycleCount, apiCallFailedCount, exceptionCount, uptimeRatio,
                                    finishPerformanceMeasurement - startPerformanceMeasurement))
                print("==========================================================================================================================================================")
                print("Powered by UPBIT. Created by LUMINOUS(blog.naver.com/agerio100 | agerio100@naver.com) | 업데이트 주기 : {} sec".format(refreshInterval))

                # wait for designated refresh interval
                sleep(refreshInterval)

            else:
                # runtime procedure verification
                if FLAG == "APIqueryURLFailed":
                    apiCallFailedCount += 1
                    print("API call creation failed. Retry in 2 seconds. | API 요청 제작 실패. 2초 내 재시도합니다.")
                elif FLAG == "UnexpectedErrorAtGatheringInformation":
                    exceptionCount += 1
                    print("Unexpected error occured at gathering information. Retry in 2 seconds. | 데이터 수집중 예상치 못한 오류 발생. 1초 내 재시도합니다.")
                elif FLAG == "unexpectedErrorAtCryptoDataProcessing":
                    exceptionCount += 1
                    print("Unexpected error occured at data processing. Retry in 2 seconds. | 데이터 처리중 예상치 못한 오류 발생. 1초 내 재시도합니다.")
                elif FLAG == "JSONDecodeErrorAtGatheringInformation":
                    exceptionCount += 1
                    print("JSON Decode exception at data processing. Retry in 2 seconds. | JSON 형태의 데이터를 디코딩하는 중 예외상황발생. 1초 내 재시도합니다.")
                
                # to execute fast recovery...
                sleep(1)
        



if __name__ == "__main__":
    runProgram()
