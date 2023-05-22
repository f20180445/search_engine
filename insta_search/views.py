from django.shortcuts import render, HttpResponse
import os
from . import followers
from . import ads
# Create your views here.

followers_scraped = False
ads_scraped = False
global docsearch
def search(request):
    return render(request, "insta_search/index.html")

def upload(request):
    return render(request, "insta_search/upload.html")

def uploaded(request):
    try:
        if request.method == 'POST':
            handle_uploaded_file(request.FILES['insta_data'], str(request.FILES['insta_data']))
            return render(request, "insta_search/search.html")
    except:
        print("error: returning upload page again")
        return render(request, "insta_search/upload.html")

def handle_uploaded_file(file, filename):
    if not os.path.exists('upload/'):
        os.mkdir('upload/')

    with open('upload/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    if "followers" in filename:
        print("scraping followers")
        scrape_followers()
    if "ads" in filename:
        scrape_ads()

def scrape_followers():
    global followers_scraped
    if followers_scraped == False:
        print("starting parse")
        followers.parse_html()
        print("followers scraped")
        followers.create_tables()
        print("followers table created")
        followers_scraped = True
    else:
        print("not scraping followers")

def ask_followers(prompt):
    global followers_scraped
    if followers_scraped == True:
        query = followers.ask_question(prompt)
        result = followers.get_answer(query)
        return result
        # results(result=result)
    else:
        scrape_followers()
        return ask_followers(prompt)

def scrape_ads():
    global docsearch, ads_scraped
    if ads_scraped == False:
        ads.parse_html()
        ads.create_ads_pdf()
        docsearch = ads.prepare_search_engine()
        ads_scraped = True

def ask_ads(prompt):
    global docsearch, ads_scraped
    if ads_scraped == True:
        result = ads.run_search_engine(docsearch, prompt)
        return result
    else:
        scrape_ads()
        return ask_ads(prompt)

def go_to_results(request):
    if request.method == 'POST':
        search_type = request.POST.get('type')
        query = request.POST.get('query')
        print(search_type)
        print(query)
        if search_type == "followers":
            result = ask_followers(query)
            print(result)
            return results(request, result)
        elif search_type == "ads":
            result = ask_ads(query)
            return results(request, result)
        else:
            return search(request)
    return results(request, "abc")

def results(request, result):
    return render(request, "insta_search/results.html", {"result":result})