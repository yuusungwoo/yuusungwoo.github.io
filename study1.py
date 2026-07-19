# BLUEPRINT | DONT EDIT

import requests
from bs4 import BeautifulSoup

response = requests.get(
    "https://berlinstartupjobs.com/engineering/",
    headers={
        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

skills = ["python", "typescript", "javascript", "rust"]

# /BLUEPRINT

# 👇🏻 YOUR CODE 👇🏻:
headers = {"User-Agent": response.request.headers["User-Agent"]}

def extract_jobs(soup):
    jobs_data = []
    jobs = soup.find_all("li", class_="bjs-jlid")
    for job in jobs:
        title_elem = job.find("h4", class_="bjs-jlid__h")
        title = title_elem.text if title_elem else "N/A"
        
        link = ""
        if title_elem and title_elem.find("a"):
            link = title_elem.find("a")["href"]
            
        company_elem = job.find("a", class_="bjs-jlid__b")
        company = company_elem.text if company_elem else "N/A"
        
        desc_elem = job.find("div", class_="bjs-jlid__description")
        description = desc_elem.text if desc_elem else "N/A"
        
        jobs_data.append({
            "title": title,
            "company": company,
            "description": description,
            "link": link
        })
    return jobs_data

def scrape_pages(url, initial_response=None):
    all_jobs = []
    current_url = url
    print(f"\n[{url}] 스크래핑 시작...")
    
    first_pass = True
    while current_url:
        if first_pass and initial_response:
            resp = initial_response
            first_pass = False
        else:
            print(f"Requesting: {current_url}")
            resp = requests.get(current_url, headers=headers)
            
        if resp.status_code != 200:
            print(f"페이지를 불러오지 못했습니다. 상태 코드: {resp.status_code}")
            break
            
        soup = BeautifulSoup(resp.content, "html.parser")
        jobs = extract_jobs(soup)
        all_jobs.extend(jobs)
        
        next_btn = soup.find("a", class_="next page-numbers")
        if next_btn:
            current_url = next_btn["href"]
        else:
            current_url = None
            
    print(f"완료! 총 {len(all_jobs)}개의 채용공고를 찾았습니다.")
    return all_jobs


engineering_jobs = scrape_pages("https://berlinstartupjobs.com/engineering/", initial_response=response)


skills_jobs = {}
for skill in skills:
    url = f"https://berlinstartupjobs.com/skill-areas/{skill}/"
    skills_jobs[skill] = scrape_pages(url)


print("\n--- 결과 요약 ---")
print(f"Engineering 공고: {len(engineering_jobs)}개 수집됨")
for skill in skills:
    print(f"{skill.capitalize()} 공고: {len(skills_jobs[skill])}개 수집됨")

# /YOUR CODE