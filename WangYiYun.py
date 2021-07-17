import random
import requests
from Crypto.Cipher import AES
from binascii import hexlify
import json
import base64
import sys



headers = {'referer': 'https://music.163.com/',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.63'
           }


def aes_encrypt(text,key):
    iv = b'0102030405060708'  #cbc模式下有偏移量

    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad     #将明文补足到16位的倍数
    model = AES.MODE_CBC       #选择aes模式
    aes = AES.new(key.encode(),model,iv)   #创建一个aes对象
    en_text = aes.encrypt(text.encode())  #加密明文
    en_text = base64.encodebytes(en_text)   #将返回的字节型数据转进行base64编码
    en_text = en_text.decode()   #将字节型数据转换成python中的字符串类型

    return en_text

def a():
    s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    random_str = ''
    for i in range(16):
        index =random.randint(0,len(s)-1)
        random_str += s[index]
    return random_str

def b(d,g,i):
    first = aes_encrypt(d,g)
    second = aes_encrypt(first,i)
    return second

def c(e,f,i):       #rsa
    text = i[::-1]
    result = pow(int(hexlify(text.encode()), 16), int(e, 16), int(f, 16))
    return format(result, 'x').zfill(131)

def get_data(d):
    e = "010001"
    f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    g = "0CoJUm6Qyw8W8jud"
    i = a()
    params = b(d,g,i)
    encSecKey = c(e,f,i)
    data = {'params':params,'encSecKey':encSecKey}

    return data


def show_search_res(res):
    tplt = "{0:<10}\t{1:<10}\t{2:<20}"
    print(tplt.format("ID", "歌名", "歌手"))
    for item in res:
        id = list(item.keys())[0]
        name = list(item.values())[0]['return_name']
        artist = list(item.values())[0]['artist']
        print(tplt.format(id,name,artist))


def search(keyword):
    d_search = {'s': keyword, 'type': 1, 'offset': 0, 'sub': 'false', 'limit': 9}
    data_search = get_data(json.dumps(d_search))

    res = requests.post('https://music.163.com/weapi/cloudsearch/get/web?csrf_token=', headers=headers,
                        data=data_search)
    search_res = json.loads(res.text)
    if 'result' in search_res:
        songs = search_res['result']['songs']
        _search_res = []
        for song in songs:
            id = song['id']
            return_name = song['name']
            artist = song['ar'][0]['name']
            _search_res.append({id:{'return_name':return_name,'artist':artist}})
        show_search_res(_search_res)
    else:
        print("网易云没有你想要的歌曲，垃圾")
        sys.exit()
    return _search_res


def get_write(id,return_name):
    d_geturl = {"ids": [id], "br": 128000, "csrf_token": ""}
    data_geturl = get_data(json.dumps(d_geturl))
    res = requests.post('https://music.163.com/weapi/song/enhance/player/url?csrf_token=', headers=headers,
                        data=data_geturl)

    url = json.loads(res.text)['data'][0]['url']
    code = json.loads(res.text)['data'][0]['code']
    if url is not None and code == 200:
        res = requests.get(url, headers=headers)
        with open('./Music/' + return_name + '.mp3', 'wb') as f:
            f.write(res.content)
            print('下载成功！')
    elif code == -110:
        print("付费歌曲，可惜")
    elif code == 404:
        print("网易云没版权，垃圾")
    else:
        print("下载失败")


if __name__ == '__main__':
    keyword = input("请输入你的吗搜索关键字：")
    search_res = search(keyword=keyword)
    id = int(input("请输入你想要下载的歌曲id："))
    for item in search_res:
        if list(item.keys()) == [id]:
            write_name = item[id].get('return_name')
    get_write(id,write_name)

