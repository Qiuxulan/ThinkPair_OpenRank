import requests
import os

def download_data(owner, repo, file_name, base_url, save_dir):
    """
    下载指定仓库的 JSON 文件并保存到本地。
    Args:
        owner (str): 仓库所有者 (e.g., "alibaba")
        repo (str): 仓库名称 (e.g., "nacos")
        file_name (str): 文件名称 (e.g., "openrank.json")
        base_url (str): 基础 URL (e.g., "https://oss.x-lab.info/open_digger/github/")
        save_dir (str): 本地保存目录
    """
    url = f"{base_url}/{owner}/{repo}/{file_name}"
    save_path = os.path.join(save_dir, owner, repo)
    os.makedirs(save_path, exist_ok=True)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            file_path = os.path.join(save_path, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {url} -> {file_path}")
        else:
            print(f"Failed to download {url}. HTTP Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def main():
    # 基础 URL
    base_url = "https://oss.x-lab.info/open_digger/github"
    
    # 文件名列表
    file_names = []  # 添加所需要的文件名称
    # 读取仓库列表
    repos_file = r"C:\Users\大头\Desktop\repo_name.txt"  
    save_dir = r"D:\华师大\openSoda 比赛\data_collection"  

    if not os.path.exists(repos_file):
        print(f"Repos file {repos_file} not found.")
        return

    with open(repos_file, 'r') as f:
        for line in f:
            repo = line.strip()
            if repo:
                owner, repo_name = repo.split('/')
                for file_name in file_names:
                    download_data(owner, repo_name, file_name, base_url, save_dir)

if __name__ == "__main__":
    main()
