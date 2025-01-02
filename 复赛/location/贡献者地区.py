import requests
import json
import os
import time
token = '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'  # 请确保此 Token 是有效且安全的
headers = {
    'Authorization': f'token {token}'
}

def get_github_repo_info(repo_name):
    url = f"https://api.github.com/repos/{repo_name}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP error occurred: {errh} for {repo_name}")
    except requests.exceptions.RequestException as err:
        print(f"Request failed: {err} for {repo_name}")
    return None

def get_github_user_info(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP error occurred: {errh} for user {username}")
    except requests.exceptions.RequestException as err:
        print(f"Request failed: {err} for user {username}")
    return None

def save_repo_location_to_file(repo_file=r'C:\Users\大头\Desktop\repo_name.txt', output_file='repo_locations.json'):
    """
    从 repo_name.txt 文件中读取仓库名称，获取位置信息并保存为 JSON 文件
    """
    locations = []
    user_cache = {}  # 缓存用户位置信息，避免重复请求
    
    if not os.path.exists(repo_file):
        print(f"File {repo_file} does not exist.")
        return

    # 打开文件并读取仓库名
    with open(repo_file, 'r', encoding='utf-8') as file:
        repos = file.readlines()
    
    # 遍历仓库名列表
    for idx, repo in enumerate(repos, start=1):
        repo = repo.strip()  # 去除每行的多余空格或换行符
        if not repo:
            continue
        print(f"Processing ({idx}/{len(repos)}): {repo}")
        repo_info = get_github_repo_info(repo)
        
        if repo_info:
            owner_info = repo_info.get('owner', {})
            username = owner_info.get('login', 'Unknown')
            
            # 检查缓存
            if username in user_cache:
                location = user_cache[username]
            else:
                user_info = get_github_user_info(username)
                if user_info:
                    location = user_info.get('location', 'Not provided')  # 获取用户的位置信息
                else:
                    location = 'Not provided'
                user_cache[username] = location  # 缓存位置
            
            locations.append({
                "repo": repo,
                "owner": username,
                "location": location
            })
        else:
            print(f"Failed to fetch info for {repo}")
        
        # 避免触发速率限制，等待1秒
        time.sleep(1)

    # 将位置数据保存为 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=4, ensure_ascii=False)

    print(f"Repository locations have been saved to {output_file}")

# 执行保存仓库位置信息的操作
if __name__ == "__main__":
    save_repo_location_to_file()
