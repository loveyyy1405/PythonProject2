import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 伪装浏览器（更稳妥的User-Agent）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Referer": "https://movie.douban.com/"
}

movies = []

# 共10页，每页25条：start=0,25,...,225
for page in range(10):
    start = page * 25
    url = f"https://movie.douban.com/top250?start={start}&filter="
    print(f"正在爬取第 {page+1} 页：{url}")

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"第 {page+1} 页请求失败：{e}")
        continue

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.find_all("div", class_="item")

    if not items:
        print(f"第 {page+1} 页没有找到电影数据，可能被反爬拦截了")
        continue

    for item in items:
        # 排名
        rank = item.find("em").text.strip() if item.find("em") else "无"
        # 电影名
        title_tag = item.find("span", class_="title")
        title = title_tag.text.strip() if title_tag else "无"
        # 评分
        score_tag = item.find("span", class_="rating_num")
        score = score_tag.text.strip() if score_tag else "无"
        # 评价人数（加了判断，防止报错）
        star_div = item.find("div", class_="star")
        people = "无"
        if star_div:
            spans = star_div.find_all("span")
            if len(spans) >= 4:
                people = spans[-1].text.strip()
        # 导演+主演+年份
        info_tag = item.find("div", class_="bd").p
        info = info_tag.text.strip() if info_tag else "无"
        # 简介
        quote_tag = item.find("span", class_="inq")
        quote = quote_tag.text.strip() if quote_tag else "无"

        movies.append({
            "排名": rank,
            "电影名": title,
            "评分": score,
            "评价人数": people,
            "信息": info,
            "简介": quote
        })

    time.sleep(2)  # 放慢速度，防止被封

# 保存到 Excel
if movies:
    df = pd.DataFrame(movies)
    df.to_excel("豆瓣电影TOP250.xlsx", index=False)
    print(f"✅ 爬取完成，共获取 {len(movies)} 条数据，已保存为：豆瓣电影TOP250.xlsx")
else:
    print("❌ 没有获取到任何数据，请检查网络或是否被反爬拦截")