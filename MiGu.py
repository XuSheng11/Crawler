from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import execjs
import requests
from lxml import etree
import json
from selenium.webdriver.chrome.options import Options

headers = {
    'referer': 'https://music.migu.cn/v3/music/player/audio',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.68'
}

options = Options()
options.add_argument('--headless')



def search(keyword):
    driver = webdriver.Chrome(options=options)

    driver.get('https://music.migu.cn/v3')
    actions = ActionChains(driver)
    handle = driver.current_window_handle

    icon = driver.find_element_by_xpath('//*[@id="header"]/div[1]/div/div[2]/div[1]/div/span/i')
    actions.move_to_element(icon).perform()
    time.sleep(0.5)

    search = driver.find_element_by_xpath('//*[@id="search_ipt"]')
    search.send_keys(keyword)
    time.sleep(0.5)


    icon.click()

    handles = driver.window_handles

    # 对窗口进行遍历
    for newhandle in handles:
        if newhandle != handle:
            # 切换到新打开的窗口B
            driver.switch_to.window(newhandle)

    return driver.page_source


def get_song_info():
    keyword = input("请输入你想要下载的歌曲：")
    page_source = search(keyword)

    html = etree.HTML(page_source)
    song_id = html.xpath('//div[@class="songlist-body"]/div[@class="row J_CopySong"]/@data-cid')
    song_name = html.xpath('//div[@class="songlist-body"]//a[@class="song-name-txt"]/@title')
    singer = html.xpath('//div[@class="songlist-body"]//div[@class="song-singers J_SongSingers"]/a//text()')

    return (song_id, song_name, singer)


def get_cookies():
    driver = webdriver.Chrome(options=options)
    driver.get('https://music.migu.cn/v3')
    actions = ActionChains(driver)
    touxiang = driver.find_element_by_xpath('//div[@id="J-user-info"]//img[@class="default-avatar"]')
    actions.move_to_element(touxiang).perform()
    denglu = driver.find_element_by_xpath('//div[@class="user-info-action"]/a[@id="J-popup-login"]')
    denglu.click()
    driver.switch_to.frame('loginIframe53645')
    mimadenglu = driver.find_element_by_xpath(
        '//div[@class="form-login J_FormLogin formLoginW"]//li[@class="accountLg"]')
    mimadenglu.click()

    shouji1 = driver.find_element_by_xpath('//*[@id="J_AccountPsd"]')
    shouji1.send_keys('13631309901')

    mima = driver.find_element_by_xpath('//div[@class="form-item"]/input[@class="txt J_NoTip J_DelectIcon J_PwPsd"]')
    mima.send_keys('0427shun')

    submit = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/div/div[5]/input')
    submit.click()

    time.sleep(2)

    cookies = driver.get_cookies()
    cookies_dict = {}
    for i in cookies:
        cookies_dict[i['name']] = i['value']
    return cookies_dict


def get_play_url(id):
    t = {"copyrightId": id, "type": 1, "auditionsFlag": 0}
    s = '4ea5c508a6566e76240543f8feb06fd457777be39549c4016436afda65d2330e'
    getdata = execjs.compile(open('getdata.js').read())
    data = getdata.call('getdata', json.dumps(t), s).replace('\n', '')
    print(data)
    enseckey = "Up9IPj+kUseIhSkkZ1Q52blx58O+4w+nLEd/NhkFidEzZem3pSGPB1jx/SCUdONVFC1iqGKxMD7uAfUL1Mgi4VkAATQ6otA+xJIbpCGWee0piSF38x9oGBApd0Qum37QpAEOdflgOiU77oFPV3oibLYHylwEYCvMkwW086NuqRI="
    url = 'https://music.migu.cn/v3/api/music/audioPlayer/getPlayInfo'
    params = {
        'dataType': 2,
        'data': data,
        'secKey': enseckey
    }
    cookie = get_cookies()

    res = requests.get(url=url, params=params, headers=headers, cookies=cookie).text
    print(res)
    play_url = json.loads(res)['data']['playUrl']
    return play_url


def download(url, name):
    res = requests.get(url, headers=headers)
    with open('./Music/' + name + '.mp3', 'wb') as f:
        f.write(res.content)
        print('下载成功！')


if __name__ == '__main__':
    info = get_song_info()
    print(info)

    tplt = "{0:<10}\t{1:<10}\t{2:<20}"
    print(tplt.format("序号", "歌名", "歌手"))

    for i in range(len(info[0])):
        print(tplt.format(i, info[1][i], info[2][i]))

    num = int(input('请输入序号选择你要下载的歌曲：'))

    playurl = get_play_url(info[0][num])
    print(playurl)
    download('http:'+playurl, info[1][num])
