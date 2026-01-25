from requests_html import HTMLSession
from bs4 import BeautifulSoup
    
s = HTMLSession() 
baseURL = "https://www.1377x.to" 
defUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"  

def fetch(query,pgno,userAgent=defUserAgent):
    data_list = []
    if query== None:
        return {"Message":"Empty Request"}
    if pgno ==None:
        pgno =1
    url = f"https://www.1377x.to/category-search/{query}/Music/{pgno}/"
    soup =getSoup(url,userAgent)
    scrapeData(soup,userAgent,data_list)

    if len(data_list) == 0:
        return {"Message":"No data found"}

    return data_list

def getSoup(url,userAgent):
    r = s.get(url, headers={'User-Agent': userAgent})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def scrapeData(soup,userAgent,data_list):
    table = soup.find('table', class_='table-list table table-responsive table-striped')

    if table is None or len(table) == 0:
        print("No table found")
        return data_list
    
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        name = columns[0].text.strip()
        link = columns[0].find_all('a')[1]
        href = link.get('href')
        se =  columns[1].text.strip()
        le = columns[2].text.strip()
        date = columns[3].text.strip()
        size = columns[4].text.strip()
        complete_url = baseURL+href
        magnet,lst1,lst2,imgSrc = scrapeMagnet(complete_url,userAgent)
        try:
            data = {"name": name,"Images":imgSrc,"Seeders": se,"Leechers": le,"Date": date,"Size":size,"otherDetails":{"category":lst1[0].text,"type":lst1[1].text,"language":lst1[2].text,"uploader":lst1[4].text,"downloads":lst2[0].text,"dateUploaded":lst2[2].text},"magnet": magnet}
        except Exception as e:
            print(e)
            data = {"error":"Failed to scrape data for "+name}
        print(data)
        data_list.append(data)
    
def scrapeMagnet(complete_url,userAgent): 
    soup = getSoup(complete_url,userAgent)
    drop_down = soup.find("ul", class_="dropdown-menu")
    try:
        magnet =  drop_down.find_all("a")[3].get("href")
    except:
        magnet = "Na"  
    imgSrc = []
    try:
        for i in  soup.find_all("img", class_="img-responsive"):
          imgSrc.append(i.get("src"))
    except:
        imgSrc = "Na"
    try:      
        lst = soup.find_all("ul", class_="list")
        lst1 = lst[1].find_all("span")
        lst2 = lst[2].find_all("span")
    except:
        lst,lst1,lst2 = None,None,None     
    return magnet,lst1,lst2,imgSrc   



#<img src="https://i.postimg.cc/vmGwpNF8/1.jpg" class="img-responsive descrimg">



