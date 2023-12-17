# 概要  
project01,...,04は各設問1,...,4に対応する答案です。  
以下の内容では各projectの中身を説明します。  
前のprojectから変更がない場合は説明を省略します。  

## log.txt  
    192.168.1.1/24, 192.168.1.2/24, 192.168.1.3/24, 10.20.30.1/16, 10.20.30.2/16, 10.20.30.3/16
    に合計100回のpingを送った結果が date(YYYYMMDDhhmmss), address, time(ms)の形で保存されています。  
    192.168.1.1/24 は　1回だけのタイムアウトが3回  
    192.168.1.2/24 は　2回連続のタイムアウトが1回、6回連続のタイムアウトが1回  
    192.168.1.3/24 は　5回連続タイムアウトして復活していない  
     10.20.30.1/16 は　1回だけのタイムアウトが1回  
     10.20.30.2/16 は　2回連続のタイムアウトが1回  
     10.20.30.3/16 は　3回連続のタイムアウトが1回  
    という設定になっています。  
##  project01    
     log.txtからタイムアウトになったサーバーを検出します。  
    log.txtの内容を読み込んで、  
    address    タイムアウト回数  
    ｎ回目 - 開始時刻　終了時刻　ダウンした時間  
    の形でproject01_output.txt に保存します。  
### detect_failures(logs)  
    log.txtのデータから　{address : [回数, {start_time, end_time}, {start_time, end_time}, ...], ... }  のディクショナリで故障内容を出します。  
### print_failures(failures)  
    detect_failuresからでた結果を片付けた文字列として出します。
### project01_output.txt  
    アドレス順に整列してないので順番に注意
    192.168.1.2/24 time-out 2 times  
    1 : - From 2023-12-18 14:30:19 to 2023-12-18 16:30:01. Duration: 1:59:42  
    2 : - From 2023-12-18 16:30:08 to 2023-12-18 17:30:08. Duration: 1:00:00  
    192.168.1.1/24 time-out 3 times  
    1 : - From 2023-12-18 14:30:19 to 2023-12-18 14:30:22. Duration: 0:00:03  
    2 : - From 2023-12-18 17:00:03 to 2023-12-18 17:00:04. Duration: 0:00:01  
    3 : - From 2023-12-18 17:30:11 to 2023-12-18 17:30:14. Duration: 0:00:03  
    10.20.30.2/16 time-out 1 times  
    1 : - From 2023-12-18 16:30:03 to 2023-12-18 16:30:09. Duration: 0:00:06  
    192.168.1.3/24 time-out 1 times  
    1 : - From 2023-12-18 17:30:09 until now.  
    10.20.30.3/16 time-out 1 times  
    1 : - From 2023-12-18 17:30:10 to 2023-12-18 17:30:19. Duration: 0:00:09  
    10.20.30.1/16 time-out 1 times  
    1 : - From 2023-12-18 17:30:12 to 2023-12-18 17:30:15. Duration: 0:00:03  
  設定と同じ結果になっているのが分かります。  
## project02  
    project01の検出関数detect_failures(logs)に連続タイムアウト回数を追加しました。  
### detect_failures(logs,n)  
    連続n回以上タイムアウトした時だけ故障とみなしてだします。  

### project02_output.txt (n=2 の結果) 
    192.168.1.2/24 time-out 2 times
    1 : - From 2023-12-18 14:30:19 to 2023-12-18 16:30:01. Duration: 1:59:42
    2 : - From 2023-12-18 16:30:08 to 2023-12-18 17:30:08. Duration: 1:00:00
    10.20.30.2/16 time-out 1 times
    1 : - From 2023-12-18 16:30:03 to 2023-12-18 16:30:09. Duration: 0:00:06
    192.168.1.3/24 time-out 1 times
    1 : - From 2023-12-18 17:30:09 until now.
    10.20.30.3/16 time-out 1 times
    1 : - From 2023-12-18 17:30:10 to 2023-12-18 17:30:19. Duration: 0:00:09
  タイムアウトが連続しない192.168.1.1/24と10.20.30.1/16が故障と判定されないことが分かります。  

## project03  
    log.txtの内容を読んで直近m回の平均応答時間がk 以上かによって過負荷状態かを判定するようになっています。  
    タイムアウトした場合その時点で過負荷状態と判定し、応答が戻ったらその時点から数えます。  
    (例：m=5 で４回前がタイムアウトで以降３回には応答があった場合は直近の3回だけ数える)

### detect_overload(logs, m)  
    log.txt のデータからアドレス別の直近m回の平均応答時間を出力します。  
    出力は　{address : {"count" : pingを送った回数（最大 m）（ダウンのときは0）, "average" : 平均応答時間（ダウンのときは"overloaded"）}}形のdictionary  

### check_overload(overload, t)  
    detect_overloadの結果から平均応答時間がt以上かないかによって判定結果を文字列で出します。  
    フォーマットは  
    "address" is fine. average response time is "average" (通常状態のとき)  
    "address" is overloaded. average response time is "average" (過負荷状態のとき)  
    "address" is down. (サーバーダウンのとき)

### project03_output.txt (m=10, t = 9)  
    192.168.1.2/24 is overloaded. average response time is 11.200
    10.20.30.2/16 is overloaded. average response time is 9.700
    192.168.1.3/24 is down
    10.20.30.1/16 is fine. average response time is 7.500
    10.20.30.3/16 is fine. average response time is 6.000
    192.168.1.1/24 is fine. average response time is 8.667

## project04  
    log.txtの内容のaddressをサブネットアドレスに書き換えてサブネットごとにproject02と同じ判定をします。  
    結果的に同じサブネットの下で連続してタイムアウトしたときその内のサーバーが故障したとみなすことになります。  

### address_to_bin(address, length)
    ipアドレスとサブネットマスクをもらってサブネットアドレスのbinaryを出します。  
### bin_to_address(bin)  
    binaryになっているサブネットを.で区分した10進数に変えます。  
### address_to_subnet(address)  
    上の２つの関数を使ってアドレスをサブネットアドレスに書き換えます。  
### check_subnet(logs,n)  
    log.txtのデータをサブネットアドレスに書き換えて、サブネットごとにn回以上タイムアウトしたときを故障とみなして結果を出します。  

### project04_output.txt(n=1)
    192.168.1 time-out 14 times
    1 : - From 2023-12-18 14:30:19 to 2023-12-18 14:30:20. Duration: 0:00:01
    2 : - From 2023-12-18 14:30:23 to 2023-12-18 14:30:23. Duration: 0:00:00
    3 : - From 2023-12-18 16:30:08 to 2023-12-18 16:30:09. Duration: 0:00:01
    4 : - From 2023-12-18 17:00:01 to 2023-12-18 17:00:02. Duration: 0:00:01
    5 : - From 2023-12-18 17:00:03 to 2023-12-18 17:00:04. Duration: 0:00:01
    6 : - From 2023-12-18 17:00:06 to 2023-12-18 17:00:07. Duration: 0:00:01
    7 : - From 2023-12-18 17:00:09 to 2023-12-18 17:00:10. Duration: 0:00:01
    8 : - From 2023-12-18 17:30:02 to 2023-12-18 17:30:03. Duration: 0:00:01
    9 : - From 2023-12-18 17:30:05 to 2023-12-18 17:30:06. Duration: 0:00:01
    10 : - From 2023-12-18 17:30:09 to 2023-12-18 17:30:10. Duration: 0:00:01
    11 : - From 2023-12-18 17:30:11 to 2023-12-18 17:30:13. Duration: 0:00:02
    12 : - From 2023-12-18 17:30:15 to 2023-12-18 17:30:16. Duration: 0:00:01
    13 : - From 2023-12-18 17:30:18 to 2023-12-18 17:30:19. Duration: 0:00:01
    14 : - From 2023-12-18 17:30:21 until now.
    10.20 time-out 5 times
    1 : - From 2023-12-18 16:30:03 to 2023-12-18 16:30:04. Duration: 0:00:01
    2 : - From 2023-12-18 16:30:05 to 2023-12-18 16:30:06. Duration: 0:00:01
    3 : - From 2023-12-18 17:30:10 to 2023-12-18 17:30:11. Duration: 0:00:01
    4 : - From 2023-12-18 17:30:12 to 2023-12-18 17:30:14. Duration: 0:00:02
    5 : - From 2023-12-18 17:30:16 to 2023-12-18 17:30:17. Duration: 0:00:01

### project04_output.txt(n=2)
    192.168.1 time-out 2 times
    1 : - From 2023-12-18 14:30:19 to 2023-12-18 14:30:20. Duration: 0:00:01
    2 : - From 2023-12-18 17:30:11 to 2023-12-18 17:30:13. Duration: 0:00:02
    10.20 time-out 0 times

    
