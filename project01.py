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

def detect_failures(logs):#
    failures = {} #failuresはdictionaryで各要素は　address : [回数, {start_time, end_time}, {start_time, end_time}, ...]　
    time = 0
    address = 1
    response = 2
    for i in range(len(logs)):
        if logs[i][response] == '-':#タイムアウトしたとき
            if logs[i][address] in failures :#初めてのタイムアウトかを確認
                if failures[logs[i][address]][-1]["end_time"] != '-':#最近のタイムアウトはもう終わった==新たなタイムアウト
                    failures[logs[i][address]][0] += 1#回数を増やす
                    failures[logs[i][address]].append({"start_time" : logs[i][time], "end_time" : '-' })#今回の時間を記録
            else :
                failures[logs[i][address]] = [ 1, {"start_time" : logs[i][time], "end_time" : '-' }]#初めてのタイムアウトなので回数１で時間を記録
        else :#応答があったとき
            if logs[i][address] in failures :#タイムアウトしたと記録がある。
                if failures[logs[i][address]][-1]["end_time"]=='-':#タイムアウト状態だったとき
                    failures[logs[i][address]][-1]["end_time"] = logs[i][0]#タイムアウト終了時間を記録
                #タイムアウト状態ではなかったら何もしない
    return failures#log分析した内容を返す

def print_failures(failures):
    if failures :
        for address in failures.keys():
            print(f"{address} time-out {failures[address][0]} times")
            for i in range(1,failures[address][0]+1):
                start_time = failures[address][i]["start_time"]
                if failures[address][i]["end_time"] == '-':
                    print(f"{i} : - From {start_time.strftime("%Y-%m-%d %H:%M:%S")} until now.")
                else :
                    end_time = failures[address][i]["end_time"]
                    duration = end_time - start_time
                    print(f"{i} : - From {start_time.strftime("%Y-%m-%d %H:%M:%S")} to {end_time.strftime("%Y-%m-%d %H:%M:%S")}. Duration: {duration}")
    else :
        print("everythings are fine")

logs = read_monitoring_logs("log.txt")

failures = detect_failures(logs)

print_failures(failures)


