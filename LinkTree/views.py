from django.shortcuts import render
from django.views import generic
from .forms import Form
from django.urls import reverse_lazy
import urllib.request
import requests
from bs4 import BeautifulSoup
import collections
import emoji
import re
import time
from urllib.parse import urljoin
from urllib.parse import urlparse

# Create your views here.

class IndexView(generic.FormView):
    template_name = "index.html"
    form_class = Form
    success_url = reverse_lazy('list')

def listfunc(request):
    global i, domain, lists
    url = request.POST.get('url') # 入力したURLを取得
    parsed_url = urlparse(url) # URLをパース
    domain = parsed_url.netloc # ドメインを取得
    lists = []

    res = requests.get(url)
    time.sleep(2)
    soup = BeautifulSoup(res.content, 'html.parser')

    # 【要件1-1】基準とするページはリンクテキストが存在しないので、title → H1 → H2 の優先度でリンクテキストの代替とする
    h_tag = soup.find('title')
    if h_tag:
        a_tag = soup.find('a')
        lists.append(('ー　' + h_tag.text + '(' + a_tag['href'] + ')'))
    else:
        h_tag = soup.find('h1')
        if h_tag:
            a_tag = soup.find('a')
            lists.append(('ー　' + h_tag.text + '(' + a_tag['href'] + ')'))
        else:
            h_tag = soup.find('h2')
            a_tag = soup.find('a')
            lists.append(('ー　' + h_tag.text + '(' + a_tag['href'] + ')'))



    # 探索の関数
    def search(text2, url2, a_href2):
        global i, domain, lists
        if domain in a_href2:
            page_url = url2
        else:
            page_url = urljoin(url2, f'{a_href2}')
        res2 = requests.get(page_url)
        # 【要件8】対象とするサイトヘのアクセスを軽減する為、リクエスト間隔を1秒以上空けること
        time.sleep(2)
        soup2 = BeautifulSoup(res2.content, 'html.parser')

        # 下位階層のページ内の「リンクテキスト（パス）」を表示
        text3 = text2 + '　　'
        a_tags2 = soup2.find_all(['a'])
        a_hrefs2 = []
        # 【要件2】1ページ内で同一ページへのリンクが複数ある場合、一つにまとめること
        for a_tag2 in a_tags2:
            if 'href' in a_tag2.attrs:
                a_hrefs2.append(a_tag2.attrs['href']) # a_tag2.attrs['href']の配列を作成
        a_hrefs_num2 = []
        a_hrefs_num2 = collections.Counter(a_hrefs2) # a_hrefsの要素ごとの出現回数をカウント（「要素：出現回数」の形式で表示）
        a_hrefs2 = list(dict.fromkeys(a_hrefs2)) # 重複しているパスを削除
        for a_href3 in a_hrefs2:
            pattern2 = re.compile(f'{a_href3}')
            a_tag2 = soup2.find('a', href = pattern2)
            if a_tag2 is None: # a_tagがNoneの場合はスキップ
                continue

            # 【要件3】探索 [2] は最大30回とし、未探索のページには末尾に$を付与する
            if a_hrefs_num[f'{a_href3}'] < 2 and i >= 30: # 要素の出現回数が1回　かつ　i>=30の場合
                # 【要件1-2】aタグの中身が画像などになっていて、リンクテキストが存在しない場合はリンクテキストは**とする
                if a_tag2.text == '' or emoji.is_emoji(a_tag2.text):
                    lists.append(('　　' + text3 + 'ー　＊＊(' + a_tag2['href'] + ')$'))
                else:
                    # 【要件6】取得したキーワードはすべて出力をする
                    lists.append(('　　' + text3 + 'ー　' + a_tag2.text.strip() + '(' + a_tag2['href'] + ')$'))

            elif a_hrefs_num2[f'{a_href3}'] < 2: # 要素の出現回数が1回の場合
                if a_tag2.text == '' or emoji.is_emoji(a_tag2.text):
                    lists.append(('　　' + text3 + 'ー　＊＊(' + a_tag2['href'] + ')'))
                else:
                    lists.append(('　　' + text3 + 'ー　' + a_tag2.text.strip() + '(' + a_tag2['href'] + ')'))

                # 【要件7】ページの探索は上位階層を優先する
                if a_href2 == a_hrefs2[-1]: # a_href2が配列a_hrefs2の最後の要素の場合
                    # 【要件4】入力で指定したドメイン以外の探索は行わないこと
                    if domain in a_href3 and 'http' in a_href3: # a_href3がドメインを含む　かつ　a_href3が'http'を含む
                        search(text, url, a_href3)

                        # 【要件3】探索 [2] は最大30回とし、未探索のページには末尾に$を付与する
                        i += 1 # 探索回数をカウント
                        if i >= 30:
                            break
                    elif 'http' in a_href3:
                        continue
                    else:
                        search(text3, url2, a_href3)

                        # 【要件3】探索 [2] は最大30回とし、未探索のページには末尾に$を付与する
                        i += 1 # 探索回数をカウント
                        if i >= 30:
                            break

            # 【要件5】出現ページが重複した場合、末尾に!を付与し、それ以降の探索を行わないこと
            else:
                if a_tag2.text == '' or emoji.is_emoji(a_tag2.text):
                    lists.append(('　　' + text3 + 'ー　＊＊(' + a_tag2['href'] + ')!'))
                else:
                    lists.append(('　　' + text3 + 'ー　' + a_tag2.text.strip() + '(' + a_tag2['href'] + ')!'))



    # ページ内の「リンクテキスト（パス）」を表示
    text = ''
    a_tags = soup.find_all(['a'])
    a_hrefs = []
    # 【要件2】1ページ内で同一ページへのリンクが複数ある場合、一つにまとめること
    for a_tag in a_tags:
        if 'href' in a_tag.attrs:
            a_hrefs.append(a_tag.attrs['href']) # a_tag.attrs['href']の配列を作成
    a_hrefs_num = []
    a_hrefs_num = collections.Counter(a_hrefs) # a_hrefsの要素ごとの出現回数をカウント（「要素：出現回数」の形式で表示）
    a_hrefs = list(dict.fromkeys(a_hrefs)) # 重複している要素（パス）を削除
    i = 0
    for a_href in a_hrefs:
        pattern = re.compile(f'{a_href}')
        a_tag = soup.find('a', href = pattern)
        if a_tag is None: # a_tagがNoneの場合はスキップ
            continue

        # 【要件3】探索 [2] は最大30回とし、未探索のページには末尾に$を付与する
        if a_hrefs_num[f'{a_href}'] < 2 and i >= 30: # 要素の出現回数が1回　かつ　i>=30の場合
            # 【要件1-2】aタグの中身が画像などになっていて、リンクテキストが存在しない場合はリンクテキストは**とする
            if a_tag.text == '' or emoji.is_emoji(a_tag.text):
                lists.append(('　　' + text + 'ー　＊＊(' + a_tag['href'] + ')$'))
            else:
                # 【要件6】取得したキーワードはすべて出力をする
                lists.append(('　　' + text + 'ー　' + a_tag.text.strip() + '(' + a_tag['href'] + ')$'))

        elif a_hrefs_num[f'{a_href}'] < 2: # 要素の出現回数が1回の場合
            if a_tag.text == '' or emoji.is_emoji(a_tag.text):
                lists.append(('　　' + text + 'ー　＊＊(' + a_tag['href'] + ')'))
            else:
                lists.append(('　　' + text + 'ー　' + a_tag.text.strip() + '(' + a_tag['href'] + ')'))
            
            # 【要件4】入力で指定したドメイン以外の探索は行わないこと
            if domain in a_href and 'http' in a_href: # a_hrefがドメインを含む　かつ　a_hrefが'http'を含む
                search(text, url, a_href)

                # 【要件3】探索 [2] は最大30回とし、未探索のページには末尾に$を付与する
                i += 1 # 探索回数をカウント
                if i >= 30:
                    break
            elif 'http' in a_href:
                continue
            else:
                search(text, url, a_href)

                # 【要件3】探索 [2] は最大30回とし、未探索のページには末尾に$を付与する
                i += 1 # 探索回数をカウント
                if i >= 30:
                    break

        # 【要件5】出現ページが重複した場合、末尾に!を付与し、それ以降の探索を行わないこと
        else:
            if a_tag.text == '' or emoji.is_emoji(a_tag.text):
                lists.append(('　　' + text + 'ー　＊＊(' + a_tag['href'] + ')!'))
            else:
                lists.append(('　　' + text + 'ー　' + a_tag.text.strip() + '(' + a_tag['href'] + ')!'))
    
    context = {'lists': lists}
    return render(request, 'list.html', context)
