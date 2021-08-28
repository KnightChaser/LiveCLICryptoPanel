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

    if "Too many requests, please try again later." in responseCryptoAPI.text:
        print("Failed to gather data. Rate exceeded.")
        return None, None

    # fiat currency (USD <---> KRW) exchange rate information
    try:
        responseUSDKRWExchangeRateAPI = requests.get("https://exchange.jaeheon.kr:23490/query/USDKRW")
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

        print("API call failed. We'll try after 3 seconds")
        apiCallFailedCount += 1
        sleep(3)

    else:

        updateCycleCount += 1

        # update metadata
        now = datetime.datetime.now()
        print("=== Live CLI Crypto Pannel === ")
        print("업데이트 시각 : {} | 업데이트 횟수 : {} 회 | API Call 실패 : {} ".format(now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초'), updateCycleCount, apiCallFailedCount))
        print()             #new line

        # process the gathered information
        print("  암호화폐          현재 가격 (변동량)            24시간 거래량               시가총액                             공급량")
        print("============================================================================================================================================")

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
                    changePercent24Hr = Fore.RED + str(changePercent24Hr)  + " % " + Style.RESET_ALL
                    changeDirectionArrow = Fore.RED + "▲" + Style.RESET_ALL
                elif float(changePercent24Hr) < 0:                                                                          # DOWN
                    changePercent24Hr = Fore.BLUE + str(changePercent24Hr)  + " % " + Style.RESET_ALL
                    changeDirectionArrow = Fore.BLUE + "▲" + Style.RESET_ALL
                else:                                                                                                       # Steady (0% change rate recorded)
                    changePercent24Hr = Fore.BLACK + str(changePercent24Hr) + " % " + Style.RESET_ALL
                    changeDirectionArrow = Fore.BLACK + "■" + Style.RESET_ALL

                # maxSupply contents may be None if its value is infinity(∞)
                if cryptoInfo.get("maxSupply") != None:
                    maxSupply = "{:,}".format(round(float(cryptoInfo.get("maxSupply"))))
                else:
                    maxSupply = "∞"

                print("""[#{0:0>2}] {1:<6} | ₩ {2:>13} ({3:>18}{4}) | ₩ {5:>19} | ₩ {6:>22} | {7:>20} / {8:>15} {9: <5}""".
                    format(rank, symbol, priceKRW, changePercent24Hr, changeDirectionArrow, volumeKRW24Hr, marketCapKRW, supply, maxSupply, symbol
                    ,end=''))

        # update interval is every 12 seconds
        sleep(15)