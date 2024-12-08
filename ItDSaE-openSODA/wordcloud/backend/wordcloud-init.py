import base64
import requests
from datetime import datetime, timedelta
from collections import Counter
from flask import Flask, jsonify
import schedule
import time
from flask_cors import CORS

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域访问

CORS(app, resources={r"/api/*": {"origins": "*"}})  # 确保所有来源都被允许
# 存储词频的全局变量
word_frequency = {}

# 技术关键词列表
tech_keywords = [
    "Python", "JavaScript", "React", "Vue", "Angular","Linux","Web",
    "Node.js", "Django", "Flask", "Spring", "Kotlin", 
    "Machine Learning", "Deep Learning", "Kubernetes", 
    "Docker", "TensorFlow", "PyTorch"]



# GitHub API Headers
HEADERS = {
    "Authorization": "token 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"  
    # 替换为你的 GitHub Token
}

def fetch_readme(repo_full_name):
    """从 GitHub 仓库获取 README.md 的内容"""
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 404:
        print(f"README.md not found for {repo_full_name}. Skipping...")
    elif response.status_code == 200:
        data = response.json()
        # README 文件内容是 base64 编码的
        readme_content = base64.b64decode(data['content']).decode('utf-8')
        return readme_content
    else:
        print(f"Failed to fetch README for {repo_full_name}. Status code: {response.status_code}")
        return ""

def extract_keywords_from_readme(readme_content):
    """从 README 内容中提取技术关键词"""
    keywords = []
    for tech in tech_keywords:
        if tech.lower() in readme_content.lower():
            keywords.append(tech)
    return keywords

def fetch_github_data():
    """从 GitHub 获取更新的数据并提取技术关键词"""
    global word_frequency

    # 计算近一个月的日期
    one_month_ago = datetime.now() - timedelta(days=30)
    date_str = one_month_ago.strftime("%Y-%m-%d")

    # GitHub 搜索 API URL，筛选最近更新的项目
    url = f"https://api.github.com/search/repositories?q=pushed:>={date_str}&sort=updated"
    response = requests.get(url, headers=HEADERS)
    #print("GitHub API response:", response.json())
    print(f"Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
    if response.status_code == 200:
        data = response.json()
        repos = data['items']

        # 提取关键词并更新词频
        keywords = []
        for repo in repos:
            repo_full_name = repo['full_name']  # e.g., "owner/repo"
            readme_content = fetch_readme(repo_full_name)
            if readme_content:
                keywords.extend(extract_keywords_from_readme(readme_content))
        
        # 统计关键词词频
        word_frequency = dict(Counter(keywords))
        print("Updated word frequencies:", word_frequency)
    else:
        print(f"Failed to fetch GitHub data. Status code: {response.status_code}")

# 定时任务，每小时更新一次
schedule.every(1).hours.do(fetch_github_data)

# 在后台运行定时任务
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# 启动定时任务线程
import threading
threading.Thread(target=run_scheduler, daemon=True).start()

# API 端点，返回最新的关键词词频
@app.route('/api/wordcloud', methods=['GET'])
def get_wordcloud_data():
    return jsonify(word_frequency)

if __name__ == "__main__":
    fetch_github_data()
    app.run(host='0.0.0.0', port=5000)