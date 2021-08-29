import os
import sys
import requests
import json
import datetime
from time import sleep
from colorama import Fore, Back, Style

# gather necessary information
def gatherInformation():

    # cryptocurrency information
    responseCryptoAPI = requests.get("https://api.coincap.io/v2/assets")

    responseCryptoAPI.encoding = 'UTF-8'

    if "Too many requests, please try again later." in responseCryptoAPI.text:
        print("Failed to gather data. Rate exceeded.")
        return None, None

    # fiat currency (USD <---> KRW) exchange rate information
    try:
        responseUSDKRWExchangeRateAPI = requests.get("https://exchange.jaeheon.kr:23490/query/USDKRW")
        responseUSDKRWExchangeRateAPI.encoding = 'UTF-8'
    except:
        print("Failed to load fiat currency exchange rate. You'd better to check API status.")
        return None, None


    cryptoDataBundle = json.loads(responseCryptoAPI.text).get("data")
    USDKRWExchangeRate = int(float(json.loads(responseUSDKRWExchangeRateAPI.text).get("USDKRW")[0]))

    return cryptoDataBundle, USDKRWExchangeRate

# user selection (only one task required)
cryptoVarietyQty = int(input("How many crypto do you want to see?(Arranged as market cap)[range : 1 ~ 50] : "))
if(cryptoVarietyQty > 50 or cryptoVarietyQty < 1):
    print("Check your input and supported range.")
    sys.exit()

# how many times information updated?
updateCycleCount = 0

# how many times API call failed
apiCallFailedCount = 0

while True:

    cryptoDataBundle, USDKRWExchangeRate = gatherInformation()

    # clear screen to show lastest information
    os.system("cls")

    if cryptoDataBundle == None or USDKRWExchangeRate == None:

        message = Back.WHITE + Fore.BLACK + "API call failed. We'll request after 3 seconds\n Please consider it may suddenly stop and run frequently\n because it's powered by free crypto API.\n" + Style.RESET_ALL
        message += Back.WHITE + Fore.BLACK + "API 요청에 실패해서 3초 뒤에 재요청을 보낼 예정입니다. \n 이 프로그램은 무료 암호화폐 API로부터 데이터를 받는 것이라 한계가 있어 중도에 잠깐 멈출 수 있다는 것을 양해해 주세요.\n" + Style.RESET_ALL
        print(message)
        apiCallFailedCount += 1
        sleep(3)

    else:

        updateCycleCount += 1

        # update metadata
        now = datetime.datetime.now()

        if apiCallFailedCount >= 1:
            uptimeRatio = round((updateCycleCount * 20 / (apiCallFailedCount * 3 + updateCycleCount * 20)) * 100, 2)
        else:
            uptimeRatio = 100

        # actual running
        try:
            print("=== Live CLI Crypto Pannel === ")
            print("업데이트 시각 : {} | 업데이트 횟수 : {} 회 | API Call 실패 : {} 회 | Uptime 비율 : {} % "
                    .format(now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초'), updateCycleCount, apiCallFailedCount, uptimeRatio))
            print()             #new line

            # process the gathered information
            print("  암호화폐          현재 가격 (변동률)            24시간 거래량               시가총액                             공급량  ")
            print("=============================================================================================================================================")

            for cryptoInfo in cryptoDataBundle:
                if int(cryptoInfo.get("rank")) <= cryptoVarietyQty:

                    rank = int(cryptoInfo.get("rank"))
                    name = cryptoInfo.get("name")
                    symbol = cryptoInfo.get("symbol")
                    priceKRW = "{:,}".format(round(float(cryptoInfo.get("priceUsd")) * USDKRWExchangeRate, 2))
                    changePercent24Hr = "{:.2f}".format(round(float(cryptoInfo.get("changePercent24Hr")), 2))
                    volumeKRW24Hr = "{:,}".format(round(float(cryptoInfo.get("volumeUsd24Hr")) * USDKRWExchangeRate))
                    marketCapKRW = "{:,}".format(round(float(cryptoInfo.get("marketCapUsd")) * USDKRWExchangeRate))
                    supply = "{:,}".format(round(float(cryptoInfo.get("supply"))))

                    # Arrow direction and colorize chagnes rate as change
                    if float(changePercent24Hr) > 0:                                                                            # UP
                        changePercent24Hr = Back.RED + Fore.WHITE + "(" + str(changePercent24Hr)  + " % " + Style.RESET_ALL
                        changeDirectionArrow = Back.RED + Fore.WHITE + "▲" + ")" + Style.RESET_ALL
                    elif float(changePercent24Hr) < 0:                                                                          # DOWN
                        changePercent24Hr = Back.BLUE + Fore.WHITE + "(" + str(changePercent24Hr)  + " % " + Style.RESET_ALL
                        changeDirectionArrow = Back.BLUE + Fore.WHITE + "▲" + ")" + Style.RESET_ALL
                    else:                                                                                                       # Steady (0% change rate recorded)
                        changePercent24Hr = Back.BLACK + Fore.WHITE + "(" + str(changePercent24Hr) + " % " + Style.RESET_ALL
                        changeDirectionArrow = Back.BLACK + Fore.WHITE + "■" + ")" + Style.RESET_ALL


                    # maxSupply contents may be None if its value is infinity(∞)
                    if cryptoInfo.get("maxSupply") != None:
                        maxSupply = "{:,}".format(round(float(cryptoInfo.get("maxSupply"))))
                    else:
                        maxSupply = "∞"

                    print("""[#{0:0>2}] {1:<6} | ₩ {2:>13} {3:>24}{4} | ₩ {5:>19} | ₩ {6:>22} | {7:>20} / {8:>15} {9: <5}""".
                        format(rank, symbol, priceKRW, changePercent24Hr, changeDirectionArrow, volumeKRW24Hr, marketCapKRW, supply, maxSupply, symbol
                        ,end=''))

            # update interval is every 20 seconds
            sleep(20)

        except:
            message = Back.WHITE + Fore.BLACK + "Unexpected elements detected in received data from API. We'll request after 3 seconds\n" + Style.RESET_ALL
            message += Back.WHITE + Fore.BLACK + "API로부터 받은 데이터에 예상하지 못한 값이 있습니다. 3초 뒤에 재요청하겠습니다.\n" + Style.RESET_ALL
            print(message)
            apiCallFailedCount += 1
            sleep(3)