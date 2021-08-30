# LiveCLICryptoPanel
개발 경험이 거의 없는 그냥 학생이  
파이썬으로 작성한 비교적 간단하고 깔끔한(?)  
실시간 CLI 기반 암호화폐 현황판입니다.

**사용하는 API에 따라 코드가 다르며**,  
API가 다른 경우 아예 디렉터리를 분류해놓았습니다.

현재 파일들)

```LiveCLICryptoPanel_upbitAPI```  
 - **2번째 작업물**
 - Upbit API 사용  
 - 2초에 한번씩 업데이트(기본값)
 - API 서비스를 제공하는 서버 능력이 좋아 uptime 비율이 아주 높음
 - 종가, 변동률, 변동량 등으로 정렬 가능
 - 유동 거래량
 - **제공 정보 : 암호화폐 종목, 마켓, 가격, 변동량과 변동률, 24시간 고가, 24시간 저가, 24시간 거래량(KRW, crypto)**

```LiveCLICryptoPanel_coincapAPI```  
 - **1번째 작업물**
 - 무료로 제공되는 해외 Coincap API 사용
 - 대략 15초에 한번씩 업데이트(기본값)
 - API 서비스를 제공하는 서버 능력이 별로 좋지 않아 Uptime 비율이 평균 90% 대에 불과
 - 전세계 거래량/시가총액 등 보다 덜 접하게 되는 정보가 많이 있으며, 전세계적인 자료가 특히 중점적으로 제공됨
 - **제공 정보 : 암호화폐 종목, 현재 가격, 변동률, 24시간 전세계 거래량, 전세계 시가총액, 전세계 암호화폐 공급량 및 공급한도량**

API마다 지원하는 정보, rate limit, API를 제공하는 서버의 수용능력 등에 따라  
프로그램의 performance, preference 등이 다릅니다.  

프로그램 코드를 원하는 API에 따라 다운받으신 다음 python으로 이를 실행하시면 됩니다.  
원하신다면 **pyinstaller** 등의 패키지를 이용해 실행 파일로 만드셔도 됩니다.  

- 코드 실행하기  
  ```python [LiveCryptoPanel_....API]py```  
- exe 파일 만들기  
  ``` pyinstaller --icon=[ico 파일 이름].ico --onefile [LiveCryptoPanel_....API]py ```  
  자세한 방법 : [자세한 pyinstaller 설정 방법](https://hongku.tistory.com/338)
