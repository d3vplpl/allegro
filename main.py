import collections, bs4, \
     re, requests
import seller
from datetime import datetime
import machine
import pandas as pd

from secret import client_ID


def process_feedbacks(seller):

    url = 'http://allegro.pl/show_user.php?uid=&type=fb_seller&p=1'
    url = url[:36] + str(seller.seller_id) + url[36:]
    limit_pages = 10
    print(url)
    res = requests.get(url)
    whole_page = bs4.BeautifulSoup(res.text)
    print(whole_page)
    seniority_date = whole_page.find(text=re.compile(r'Użytkownik od:'))
    seniority_date = seniority_date[15:]
    seniority_datetime = datetime.strptime(seniority_date, '%d.%m.%Y, %H:%M:%S')
    seniority_datetime = datetime.strftime(seniority_datetime, '%Y-%m-%d %I:%M:%S')
    print('seniority date as date: ' + str(seniority_datetime))
    # pagination
    no_pages = 1
    no_pages_bs = whole_page.select('ul[class="pagination"]')
    if len(no_pages_bs) != 0:
        no_pages_li = no_pages_bs[0].select('li')
        no_pages_suffix = whole_page.find('li', class_='suffix')
        index = no_pages_li.index(
            no_pages_suffix) + 1  # set index to element li after element conatining z (out of) - suffix
        no_pages = no_pages_li[index].text

    print('No of feedback pages: ' + str(no_pages))
    if int(no_pages) > limit_pages:
        print('Auctioner ' + str(seller.seller_id) + ' has excessive numbers of feedbacks, processing only ' + str(
            limit_pages) + ' pages')

    auction_ids = whole_page.select('a[data-item-id]')
    #print(auction_ids)
    feedbacks = []
    for page in range(2, int(no_pages) + 2):
        print('Processing url ' + url)
        print('page: ' + str(page - 1))
        for a in auction_ids:
            feedbacks.append(a.attrs['data-item-id'])
        url = url.split('&p=', 1)[0] + '&p=' + str(page)
        res = requests.get(url)
        whole_page = bs4.BeautifulSoup(res.text)
        auction_ids = whole_page.select('a[data-item-id]')
        if page > limit_pages:
            break
    cnt = collections.Counter(feedbacks)  # to jest count po id aukcji (do różnorodności komentarzy)

    print('Counted feedbacks: ' + str(len(feedbacks)))
    print('Feedbacks :' + str(feedbacks))
    return cnt, seniority_datetime, len(feedbacks)


'''
Process many auctions with paging
returns list of auction urls
'''


def process_auctions(starting_url):
    limit_pages = 2
    res = requests.get(starting_url)
    whole_page = bs4.BeautifulSoup(res.text)
    print("starting url: " + starting_url)

    no_pages_bs = whole_page.select('a[rel="last"]')
    no_pages = no_pages_bs[0].text
    if int(no_pages) > limit_pages:
        no_pages = str(limit_pages)
    print("No_pages: " + no_pages)
    auctions = []
    for page in range(2, int(no_pages) + 1):
        print("page: " + str(page - 1))
        auctions_list = whole_page.select('h2 > a')
        auctions_list.remove(auctions_list[0])

        for a in auctions_list:
            auctions.append(a.attrs['href'])
        starting_url = starting_url.split('&p=', 1)[0] + '&p=' + str(page)

        print("starting url: " + starting_url)
        res = requests.get(starting_url)
        whole_page = bs4.BeautifulSoup(res.text)
    print("Found " + str(len(auctions)) + " auctions")
    print((auctions))

    return auctions


def process_single_auction(auction_url):
    print(auction_url)
    res = requests.get(auction_url)
    whole_page = bs4.BeautifulSoup(res.text)

    auction_date = whole_page.select('time')

    return auction_date[0].attrs['datetime']


'''
Extracts seller id from single auction by auction URL
'''


def extract_auctioner_from_auction(auction_url):
    print(auction_url)
    res = requests.get(auction_url)
    whole_page = bs4.BeautifulSoup(res.text)

    seller_id = whole_page.select('a[id="seller-rating"]')
    result = None
    if len(seller_id) > 0:
        result = (seller_id[0].attrs['href']).split('=', 1)[1]
        s = seller.Seller(result, 'brak nazwy', None, None, None, None, None)
    return s


'''
Wraps up multiple auctions to return set of distinct auctioners
'''


def extract_auctioners_from_auctions(auctions_urls):
    auctioners = []
    for auction in auctions_urls:
        auc = extract_auctioner_from_auction(auction)

        if auc != None:
            auctionerExists = False
            for a in auctioners:
                if a.seller_id == auc.seller_id:
                    auctionerExists = True
            if not auctionerExists:
                auctioners.append(auc)

    return auctioners


'''
Take auctioneers with only id filled and add seniority date
'''


def enrich_auctioners_data(auctioners):
    for auctioner in auctioners:
        cnt, seniority_date, feedbacks_count = process_feedbacks(auctioner)
        auctioner.senior = seniority_date
        auctioner.feedbacks_count = feedbacks_count
    return auctioners


def database_connect():
    try:
        conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='123456'")
    except:
        print('I am unable to connect to the database')

    return conn


def persist_seller_to_database(seller):
    conn = database_connect()
    cur = conn.cursor()
    betw = '\',\''
    insert_query = 'INSERT INTO public.sellers("Seller_ID", "Seller_name", "Seniority_date", "Feedbacks_count" )\
        VALUES (\'' + str(seller.seller_id) + betw + seller.seller_name + betw + str(seller.senior) + '\',' \
        + str(seller.feedbacks_count) + ');'

    print('Trying to execute SQL: ' + insert_query)
    cur.execute(insert_query)
    conn.commit()


def fetch_sellers_from_db():
    conn = database_connect()
    cur = conn.cursor()
    select_query = 'SELECT public.sellers."Seller_ID", "Seniority_date", "Feedbacks_count" FROM public.sellers'
    cur.execute(select_query)
    sellers = cur.fetchall()
    return sellers

fake_seller = True


if fake_seller:
    s = seller.Seller(43854717, 'fake seller', None, None, None, None, None )#    instantiate seller
    sellers = []
    #sellers.append(str(s))
    #print("Fake seller is: ", s)
    #process_feedbacks(s)
    #exit()

    #sellers = fetch_sellers_from_db()
auctioners_seniority = []
auctioners_feedbacks_count = []
    #data = array.array('i', [])
for s in sellers:
    auctioners_seniority.append(((datetime.now().date()) - s[1]).days)
    auctioners_feedbacks_count.append(s[2])

# tu są przykłady
df_train_example = pd.read_csv('train1.csv', delimiter=',', dtype=str)
df_train_example.drop('seller_id', axis=1,inplace=True)
print('df_train_example:', df_train_example)
df_test_example = pd.read_csv('test1.csv', delimiter=',', dtype=str)
df_test_example.drop('seller_id', axis=1, inplace=True)

train_example_target = [1, 1, 0, 1, 0, 1, 1]
df_train_example_target = pd.DataFrame(data=train_example_target)


train_target = [1, 1, 1, 0, 0, 1, 0]
#print('train target: ' + str(train_target))


df_train_auctioners = pd.DataFrame(
    {'seniority': auctioners_seniority[:5], 'feedbacks_count': auctioners_feedbacks_count[:5]})
df_test_auctioners = pd.DataFrame(
    {'seniority': auctioners_seniority[5:10], 'feedbacks_count': auctioners_feedbacks_count[5:10]})
df_train_target = pd.DataFrame(data=train_target)

#print("df_train_target: " + str(df_train_target))

#df_train_auctioners = pd.DataFrame(data=train_auctioners)
#print("df_train_auctioners: " + str(df_train_auctioners))

#print('df_test_auctioners' + str(df_test_auctioners))

#predictions = machine.full_machine(df_train_auctioners, df_train_target, df_test_auctioners)
predictions = machine.full_machine(df_train_example, df_train_example_target, df_test_example)
print('predictions: ' + str(predictions))

print ('klient test: ', client_ID)
