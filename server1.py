import socket
import select
import tkinter as tk
import threading
import requests
import json
import sys

context1 = ""
mode1 = ""

def send_to(sock, msg):
    try:
        sock.send(msg.encode())
        return True
    except:
        sock.close
        return False


def broadcast(socklist, msg):
    for sock in socklist:
        if not send_to(sock, msg):
            sock_list.remove(sock)

def AI(text,context="",mode=""):
    payload = {
        "utt": text,
        "context": context,
        "nickname": "",
        "nickname_y": "",
        "sex": "",
        "bloodtype": "",
        "birthdateY": "",
        "birthdateM": "",
        "birthdateD": "",
        "age": "21",
        "constellations": "",
        "place": "東京",
        "mode": mode,
    }

    url = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=386e4f563663766c5761322e4251555577733136794c7659425863394544727550636e7a4373435236722f'
    s = requests.session()
    r = s.post(url, data=json.dumps(payload))
    res_json = json.loads(r.text)
    global context1
    context1 = res_json["context"]
    response = res_json["utt"]
    global mode1
    mode1 = res_json["mode"]
    return response


host = '127.0.0.1'
port = 44444
backlog = 10
bufsize = 4096

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket is created")


def window():
    root = tk.Tk(None)
    root.title("サーバー管理画面")
    frame = tk.Frame(master=root, width=640, height=420)

    label1 = tk.Label(master=frame, text="サーバー管理画面", font=('Meiryo UI', '12'), bg="#FCFAF2")
    label1.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)
    frame.pack()
    root.mainloop()




thrd1 = threading.Thread(target=window)
#thrd1.start()がウィンドウ表示の合図
thrd1.start()
try:
    server_sock.bind((host, port))
    print("socket bind")
    server_sock.listen(backlog)
    print("sock listen")
    global sock_list
    sock_list = [server_sock]
    # クライアントのソケットをポートで管理するために
    # 辞書型でソケットを保存
    client_sock_table = {}
    while True:
        r_ready_sockets, w_ready_sockets, e_ready_sockets = select.select(sock_list, [], [])
        # select.select(rlist,wlist,xlist[,timeout])
        # rlist読み込み可能となるまで待機
        # wlist書き込み可能となるまで待機
        # xlist例外状態となるまで待機
        # timeoutタイムアウトの時間
        # 戻り値は準備完了状態のオブジェクト(最初の3つの印数のサブセット)
        for sock in r_ready_sockets:
            if sock == server_sock:
                conn, address = sock.accept()
                sock_list.append(conn)
                # ポートをキーとしてソケットを保存
                client_sock_table[address[1]] = conn
                # 誰かの接続があったことを全員に送る
                sock_list.remove(server_sock)
                broadcast(sock_list, "ポート" + str(address[1]) + "番のユーザーが接続しました")
                sock_list.append(server_sock)
                print(str(address) + "is connected")
            else:
                try:
                    b_msg = sock.recv(bufsize)
                    msg = b_msg.decode('utf-8')
                    if len(msg) == 0:
                        sock.close()
                        sock_list.remove(sock)
                    else:
                        # client_sock_tableから送受信のポートを調べる
                        sender_port = None
                        # 辞書型のキーと値をfor文で順に参照する
                        for key, val in client_sock_table.items():
                            if val == sock:
                                sender_port = key
                                break
                        if sender_port is not None:
                            sock_list.remove(server_sock)
                            broadcast(sock_list, str(sender_port) + ":" + msg)
                            broadcast(sock_list, "AIちゃん：" + AI(msg,context1,mode1))
                            sock_list.append(server_sock)
                except:
                    import traceback
                    traceback.print_exc()
                    sock.close()
                    sock_list.remove(sock)
                    sock_list.remove(server_sock)
                    broadcast(sock_list, "someone disconnected")
                    sock_list.append(server_sock)
except Exception as e:
    print("EXCEPTION")
    print(e)
    server_sock.close()

