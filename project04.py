import datetime

def parse_log_line(line):#logの各行をtimestamp, server_address, responseに分ける
    timestamp_str, server_address, response  = line.strip().split(',')
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
    return timestamp, server_address, response

def read_monitoring_logs(log_file_path):#各要素に(timestamp, server_address, response)を保存したリストを出力
    with open(log_file_path, 'r') as file:
        lines = file.readlines()
        logs = [list(parse_log_line(line)) for line in lines]
    return logs

def detect_failures(logs,n):#logの中で連続n回以上タイムアウトだったサーバーだけfailuresとして返す
    failures = {} #failuresはdictionaryで各要素は　address : [回数, {start_time, end_time}, {start_time, end_time}, ...]　
    time = 0#failures上のアドレスを分かりやすくするための設定
    address = 1
    response = 2
    for i in range(len(logs)):#記録途中には回数を連続タイムアウト回数として扱う
        if logs[i][response] == '-':#タイムアウトしたとき
            if logs[i][address] in failures :#初めてのタイムアウトかを確認
                if failures[logs[i][address]][-1]["end_time"] != '-':#最近のタイムアウトはもう終わった==新たなタイムアウト
                    failures[logs[i][address]][0] = 1
                    failures[logs[i][address]].append({"start_time" : logs[i][time], "end_time" : '-' })#今回の時間を記録
                else :
                    failures[logs[i][address]][0] += 1#何回目かを記録
            else :#初めてのタイムアウトの場合
                failures[logs[i][address]] = [ 1, {"start_time" : logs[i][time], "end_time" : '-' }]#初めてのタイムアウトなので回数１で時間を記録
        else :#応答があったとき
            if logs[i][address] in failures :#タイムアウトしたと記録がある。
                if failures[logs[i][address]][-1]["end_time"]=='-':
                    if failures[logs[i][address]][0]< n : #タイムアウトがn回未満
                        failures[logs[i][address]].pop()
                        if len(failures[logs[i][address]])==1:
                            del failures[logs[i][address]]
                    else :
                        failures[logs[i][address]][-1]["end_time"] = logs[i][0]#タイムアウト終了時間を記録
                    #タイムアウト状態ではなかったら何もしない
    for address in failures.keys():
        if failures[address][0]< n : #復活してないがタイムアウト回数がn回未満は消す
            failures[address].pop()
        failures[address][0] = len(failures[address])-1 #記録が終わったので全部何回のタイムアウトが起こったのかに書き直す
    return failures#log分析した内容を返す

def print_failures(failures):
    failures_log = []
    if failures :
        for address in failures.keys():
            failures_log += [f"{address} time-out {failures[address][0]} times"]
            for i in range(1,failures[address][0]+1):
                start_time = failures[address][i]["start_time"]
                if failures[address][i]["end_time"] == '-':
                    failures_log += [f"{i} : - From {start_time.strftime("%Y-%m-%d %H:%M:%S")} until now."]
                else :
                    end_time = failures[address][i]["end_time"]
                    duration = end_time - start_time
                    failures_log += [f"{i} : - From {start_time.strftime("%Y-%m-%d %H:%M:%S")} to {end_time.strftime("%Y-%m-%d %H:%M:%S")}. Duration: {duration}"]
    else :
        failures_log +=["everythings are fine"]
    return failures_log

def detect_overload(logs, m):
    overload = {}#overload = {"count" : pingを送った回数（最大 m）（ダウンのときは0）, "average" : 平均応答時間（ダウンのときは"overloaded"）}
    time = 0#failures上のアドレスを分かりやすくするための設定
    address = 1#logsを分析するとき添え字として使う
    response = 2
    for i in range(len(logs)):
        if logs[i][response] == '-':#タイムアウトしたとき
            overload[logs[i][address]] = {"count" : 0, "average" : "overload" } # タイムアウトがあったときは過負荷状態とする
        else :
            if logs[i][address] in overload :#記録があるとき
                if overload[logs[i][address]]["count"] < m:
                    overload[logs[i][address]]["count"] += 1#応答回数を増やす
                    if  overload[logs[i][address]]["average"] == "overload" :#サーバーが治ったとき
                        overload[logs[i][address]]["average"] = [logs[i][response]]
                    else :
                        overload[logs[i][address]]["average"].append(logs[i][response])#最近(m回まで)の応答時間をリストで保存
                else :#m回のデータがあるとき
                    del overload[logs[i][address]]["average"][0]#m回以前のデータを消す
                    overload[logs[i][address]]["average"].append(logs[i][response])#最近の内容を保存
            else :
                overload[logs[i][address]] = {"count" : 1, "average" : [logs[i][response]]}
    for address in overload.keys():#ここでのaddressは文字列なので注意
        sum = 0
        if overload[address]["count"] > 0:
            for i in range(len(overload[address]["average"])):
                sum += int(overload[address]["average"][i])
            overload[address]["average"] = sum/overload[address]["count"] #リストの内容から平均値を計算して置き換える
    return overload#log分析した内容を返す

def check_overload(overload, t):
    is_overload = {}
    for address in overload.keys():
        if overload[address]["average"] == "overload":
            is_overload[address] = [False, 0]
        else :
            if overload[address]["average"] > t :
                is_overload[address] = [False, overload[address]["average"]]
            else :
                is_overload[address] = [True,  overload[address]["average"]]
    return is_overload
            
def print_overload(overload): #平均応答時間が基準時間tを超えているかによって
    overload_log = []
    for address in overload.keys():
        if overload[address][0] == False:
            if overload[address][1] == 0:
                overload_log += [f"{address} is down"]
            else :
                overload_log += [f"{address} is overloaded. average response time is {overload[address][1] :.3f}"]
        else :
                overload_log += [f"{address} is fine. average response time is {overload[address][1] :.3f}"]
    return overload_log
            
def address_to_bin(address, length): #addressとlengthからサブネットのbinaryを返す
    address = address.split(".")
    address_str=''
    for i in range(len(address)):
        address[i] = int(address[i])
        address_str += format(address[i], 'b').zfill(8)
    return [address_str[i:i+length] for i in range(0, len(address_str), length)]

def bin_to_address(bin):#binaryになっているサブネットを.で区分した10進数に変える
    address = [bin[i:i+8] for i in range(0, len(bin), 8)]
    address[-1]= address[-1]+('0'*(8-len(address[-1])))#サブネットマスクが8の倍数でないときの処理
    for i in range(len(address)):
        address[i] = str(int(address[i],2))
    return ('.'.join(address))

def address_to_subnet(address):#アドレスからサブネットアドレスを作る
    address,length = address.split("/")
    result = address_to_bin(address,int(length))
    result = bin_to_address(result[0])
    return result

def check_subnet(logs,n):
    for i in range(len(logs)):
        logs[i][1]=address_to_subnet(logs[i][1])
    return detect_failures(logs,n)

logs = read_monitoring_logs("log.txt")


#print(check_subnet(logs,1))

failures= print_failures(check_subnet(logs,2))
f = open("project04_output.txt","w+")
for i in range(len(failures)):
    f.write(f"{failures[i]}\n")
f.close()

    
