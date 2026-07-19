from flask import Flask, render_template, request, redirect
from flask_frozen import Freezer
import requests
from bs4 import BeautifulSoup
import sys

app = Flask(__name__)
freezer = Freezer(app)


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def scrape_berlin(term):
    url = f"https://berlinstartupjobs.com/skill-areas/{term}/"
    jobs_data = []
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            jobs = soup.find_all("li", class_="bjs-jlid")
            for job in jobs:
                title_elem = job.find("h4", class_="bjs-jlid__h")
                title = title_elem.text if title_elem else "N/A"
                
                company_elem = job.find("a", class_="bjs-jlid__b")
                company = company_elem.text if company_elem else "N/A"
                
                link = "N/A"
                if title_elem and title_elem.find("a"):
                    link = title_elem.find("a")["href"]
                    
                jobs_data.append({"title": title, "company": company, "link": link})
    except Exception as e:
        print("Error scraping BerlinStartupJobs:", e)
    return jobs_data

def scrape_web3(term):
    url = f"https://web3.career/{term}-jobs"
    jobs_data = []
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            jobs = soup.find_all("tr", class_="table_row")
            for job in jobs:
                title_elem = job.find("h2")
                title = title_elem.text if title_elem else "N/A"
                
                company_elem = job.find("h3")
                company = company_elem.text if company_elem else "N/A"
                
                link_elem = job.find("a")
                link = "https://web3.career" + link_elem["href"] if link_elem and "href" in link_elem.attrs else "N/A"
                
                jobs_data.append({"title": title, "company": company, "link": link})
    except Exception as e:
        print("Error scraping Web3 Career:", e)
    return jobs_data

def scrape_wwr(term):
    url = f"https://weworkremotely.com/remote-jobs/search?utf8=%E2%9C%93&term={term}"
    jobs_data = []
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            jobs = soup.find_all("li", class_="feature")
            for job in jobs:
                title_elem = job.find("span", class_="new-listing__header__title__text")
                title = title_elem.text if title_elem else "N/A"
                
                company_elem = job.find("p", class_="new-listing__company-name")
                company = company_elem.text if company_elem else "N/A"
                
                links = job.find_all("a")
                link = "N/A"
                for a in links:
                    if "href" in a.attrs and "/remote-jobs/" in a["href"]:
                        link = "https://weworkremotely.com" + a["href"]
                        break
                        
                jobs_data.append({"title": title, "company": company, "link": link})
    except Exception as e:
        print("Error scraping We Work Remotely:", e)
    return jobs_data

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search/<term>/")
def search(term):
    if not term:
        return redirect("/")
    
    term = term.lower().strip()
    
    # 세 사이트에서 스크래핑 진행
    berlin_jobs = scrape_berlin(term)
    web3_jobs = scrape_web3(term)
    wwr_jobs = scrape_wwr(term)
    
    # 결과 그룹화
    jobs_by_source = {
        "Berlin Startup Jobs": berlin_jobs,
        "Web3 Career": web3_jobs,
        "We Work Remotely": wwr_jobs
    }
    
    total_count = sum(len(jobs) for jobs in jobs_by_source.values())
    
    return render_template("search.html", term=term, jobs_by_source=jobs_by_source, count=total_count)

@freezer.register_generator
def search():
    for term in ["python", "javascript", "java"]:
        yield {"term": term}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(debug=True, port=8000)