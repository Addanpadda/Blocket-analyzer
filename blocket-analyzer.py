#!/bin/bash
import urllib3
import html
import re

data = []
start = 0
page = 'https://www.blocket.se/hela_sverige?q=volvo+940&cg=1020&w=3&st=s&ps=&pe=&mys=&mye=&ms=&me=&cxpf=&cxpt=&fu=&pl=&gb=&ca=11&is=1&l=0&md=th&cp='
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

#Set headers, start connection and decode the answer
user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
http = urllib3.PoolManager(10, headers=user_agent)
urllib3.disable_warnings()

def download_pages(url):
    try:
        request = http.request('GET', url)
    except:
        print('[-]No internet connection')
        exit(1)
    return request.data.decode('utf-8')


def pre_process():
    PageCount = 1

    while True:
        lastData = len(data)

        print('[+]Crawling', page + '&o=%d' % (PageCount))
        answer = download_pages(page + '&o=%d' % (PageCount))
        if answer.find('<h1 class="h5 media-heading ptxs" itemprop="name"><a href="') != -1:
            start = 0

            #Retrieving all the links for each announcement
            while True:
                if answer.find('<h1 class="h5 media-heading ptxs" itemprop="name"><a href="', start) != -1:
                    start = answer.find('<h1 class="h5 media-heading ptxs" itemprop="name"><a href="', start)+59
                    end = answer.find('"', start)
                    data.append([answer[start:end]])

                else:
                    break
            start = 0


            #Retrieving the location of each announcement
            for x in range(lastData, len(data)):
                if answer.find('<div class="pull-left ">', start) != -1:
                    start = answer.find('<div class="pull-left ">', start) + 24
                    if answer[start] == '<':
                        if answer.find('''<a class="label label-default mrxs" itemprop="url" onclick="return xt_click(this,'C','11','Butiksbadge','N')"''', start) == start:
                            start = answer.find('Butik</a>', start) + 9
                        else:
                            start = answer.find('&nbsp;', start) + 6
                    end = answer.find('<', start)
                    data[x].append(answer[start:end])
                else:
                    data[x].append('')
            PageCount += 1
        else:
            print('[+]Found %d announcements!' % (len(data)))
            break


def process():
    for currentPage in range(len(data)):
        #Downloading the current page
        answer = download_pages(data[currentPage][0])

        #Getting the name of the car
        start = answer.find('<h1 class="h3 ')+33
        if answer.find('<h1 class="h3 subject_medium">') != -1:
            start+=1
        end = answer.find('<', start)-11
        while True:
            if answer[start:end][-1] == ' ':
                end-=1
            else:
                break
        data[currentPage].append(html.unescape(answer[start:end]).replace('"', ''))

        #Getting the price of the car
        if answer.find('<div id="vi_price" class="h3 nmb"') != -1:
            start = answer.find('\n', answer.find('<div id="vi_price" class="h3 nmb"'))+1

            end = answer.find(' kr', start)
            data[currentPage].append(answer[start:end])
        else:
            data[currentPage].append('')

        #Getting the milage
        if answer.find('<dt>Miltal</dt>') != -1:
            start = answer.find('<dt>Miltal</dt>')+39
            end = answer.find('<', start)-4
            data[currentPage].append(answer[start:end])
        else:
            data[currentPage].append('')

        #Getting the year of production
        if answer.find('<dt>Modellår</dt>') != -1:
            start = answer.find('<dt>Modellår</dt>')+33
            end = answer.find('<', start)
            data[currentPage].append(answer[start:end])
        else:
            data[currentPage].append('')

        #Getting the posting date
        start = answer.find('<time datetime="')+16
        end = answer.find('"', start)
        date = answer[start:end].replace('T', ' ')+':00'
        data[currentPage].append(date)

        #Getting the description
        if answer.find('<p class="motor-car-description">') != -1:      #If the car is sold by a store
            start = answer.find('<p class="motor-car-description">')+38
            end = answer.find('</p>', start)-4
            text = answer[start:end]
        elif answer.find('<h2 class="body-content-description-headline h6">Beskrivning</h2>') != -1:         #If the car is sold by a induvidual
            start = answer.find('<h2 class="body-content-description-headline h6">Beskrivning</h2>')+76
            end = answer.find('<!', start)-2
            text = answer[start:end]
        elif answer.find('<div class="col-xs-12 body">') != -1:
            start = answer.find('<div class="col-xs-12 body">') + 57
            end = answer.find('<!-- Car extra data -->', start)-2
            text = answer[start:end]
        else:
            text = ''
        text = html.unescape(text).replace('\n', ' ').replace('<br />', '\n').replace('<wbr>', '')  # Parsing the output and removing html characters
        text = emoji_pattern.sub(r'', text)
        data[currentPage].append(text)

        #Getting the pictures
        if answer.find('data-src="https://cdn.blocket.com/static/') != -1:
            start = answer.find('data-src="https://cdn.blocket.com/static/')+10
            end = answer.find('"', start)
            data[currentPage].append(answer[start:end])
            while True:
                if answer.find('data-src="https://cdn.blocket.com/static/', start) != -1:
                    start = answer.find('data-src="https://cdn.blocket.com/static/', start)+10
                    end = answer.find('"', start)
                    data[currentPage][8] = data[currentPage][8] + ', ' + answer[start:end]
                else:
                    break
        else:
            data[currentPage].append('')

pre_process()
process()

print(data)
