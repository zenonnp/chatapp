import tkinter as tk
import socket, select
import requests, sys, webbrowser, bs4
from tkinter.messagebox import showinfo
import requests
import json
import threading

context1 = ""
mode1 = ""

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

def question_ai():
    if len(entered_txt.get()) <= 0:
        return
    apikey = "386e4f563663766c5761322e4251555577733136794c7659425863394544727550636e7a4373435236722f"
    params = {'q': entered_txt.get(), 'APIKEY': apikey}
    s = requests.session()
    r = s.get('https://api.apigw.smt.docomo.ne.jp/knowledgeQA/v1/ask', params=params)
    res_json = json.loads(r.text)
    if res_json["code"].startswith("S"):
        if res_json["code"] =="S020011" :
            response = res_json["message"]["textForDisplay"]
            res2 = res_json["answers"][0]["linkUrl"]
            Answer = response +"\n"+ res2
        else :
            response = res_json["message"]["textForDisplay"]
            Answer = response
    else:
        Answer = "回答が得られませんでした"
    stocked_msg.append(Answer)
    etr.delete(0, tk.END)

def send_msg(ev=None):
    if len(entered_txt.get()) <= 0:
        return
    sock.send(entered_txt.get().encode())
    etr.delete(0, tk.END)


def receive_msg(msg):
    if text_w is None:
        return
    text_w.configure(state=tk.NORMAL)
    text_w.insert(tk.END, msg + "\n")
    text_w.configure(state=tk.DISABLED)
    text_w.see(tk.END)


def stock_msg(msg):
    stocked_msg.append(msg)


def check_msg():
    while len(stocked_msg) > 0:
        receive_msg(stocked_msg.pop(0))
    text_w.after(200, check_msg)


def dicting():
    if len(entered_txt.get()) <= 0:
        return
    word = entered_txt.get()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = requests.get('http://dic.yahoo.co.jp/search/?p=' + word)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text)
    summary_elems = soup.select('.result-r li div')
    title_elems = soup.select('.result-r a')

    if len(summary_elems) == 0:
        showinfo('検索結果', "そのような単語は見つかりませんでした。")
        etr.delete(0, tk.END)
    else:
        # tkMessageBox.showinfo(title_elems[1].getText())
        for i in range(1):
            showinfo(title_elems[1].getText(), summary_elems[i].getText())
        etr.delete(0, tk.END)



root = tk.Tk(None)
root.title("しりとりチャット")

frame = tk.Frame(master=root, width=640, height=420)

label1 = tk.Label(master=frame, text="しりとりチャット", font=('Meiryo UI', '12'), bg="#FCFAF2")
label1.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)

# 複数行テキスト(state=tk.NORMAL の場合は編集可能 state=tk.DESABLEの場合は編集不可能
text_w = tk.Text(master=frame, state=tk.DISABLED, font=('Meiryo UI', '12'), bg="#FCFAF2")
text_w.place(relx=.05, rely=.1, relwidth=.85, relheight=0.7)

# スクロールバー
sb_y = tk.Scrollbar(master=frame, orient=tk.VERTICAL, command=text_w.yview)
sb_y.place(relx=0.9, rely=0.1, relwidth=0.05, relheight=0.7)
# スクロールバーの状態を複数行テキストと合わせる
text_w.config(yscrollcommand=sb_y.set)

# 入力された文字列を扱うための文字列変数オブジェクト
entered_txt = tk.StringVar()
# 1行編集テキスト
etr = tk.Entry(master=frame, width=30, textvariable=entered_txt)
# bindで、キーイベントと、キーが押された時に呼ばれる関数を指定
etr.bind('<Return>', send_msg)
etr.place(relx=0.05, rely=0.85, relwidth=0.65, relheight=0.1)

# ボタン
# commandオプションで、ボタンが押された時に呼ばれる関数を指定
bt = tk.Button(master=frame, text="発言", bg="#FCFAF2", command=send_msg)
bt.place(relx=0.75, rely=0.85, relwidth=0.10, relheight=0.1)
# fillはtk.Xで横に広げる,tk.Yで縦に広げる

#怪しいボタン
strange_bt = tk.Button(master=frame, text="意味検索", bg="#FCFAF2", command=question_ai)
strange_bt.place(relx=0.65, rely=0.85, relwidth=0.10, relheight=0.1)

# frameをpack
frame.pack()

host = '10.65.165.60'
port = 44444
bufsize = 4096

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 送られてきたメッセージをストックするためのリスト
stocked_msg = []


def listen():
    try:
        sock.connect((host, port))
        while True:
            r_ready_sockets, w_ready_sockets, e_ready_sockets = select.select([sock], [], [])
            try:
                recev_msg = sock.recv(bufsize).decode()
            except:
                break
            # 直接recive_msgを呼ぶのではなくstock_msgを読んでメッセージをストック
            stock_msg(recev_msg)
    except Exception as e:
        print(e)
    finally:
        sock.close()
        receive_msg("サーバーとの接続が切断されました")


# ストックされたメッセージを定期的に処理するcheck_msgを呼び出す
check_msg()
# サーバーから送信を待つ処理を別のthreadで制御する(並列処理)
# targetで指定したlistenをthreadで処理する
thrd = threading.Thread(target=listen)
thrd1 = threading.Thread(target=question_ai)
thrd.start()
thrd1.start()
root.mainloop()
