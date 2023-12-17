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
    time = 0
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

logs = read_monitoring_logs("log.txt")

failures = detect_failures(logs,2)
failures = print_failures(failures)
f = open("project02_output.txt","w+")
for i in range(len(failures)):
    f.write(f"{failures[i]}\n")
f.close()