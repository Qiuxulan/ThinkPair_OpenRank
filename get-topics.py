import json
import requests

# 从文件中读取仓库名列表
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\get300-repo.json', 'r') as f:
    repo_name_user = json.load(f)

# 全局变量定义
result1 = {}  # 存储仓库名称及其对应的主题标签
result2 = {}  # 存储主题标签及其对应的仓库列表

# GitHub API 认证头
HEADERS = {
    "Authorization": "token 隐私信息无法通过github提交"  
}

def get_repo_topics(repo_name, owner):
    """
    通过 GitHub API 获取指定仓库的主题标签
    
    参数:
        repo_name: 仓库名称
        owner: 仓库所有者
    返回:
        tech: 包含仓库主题标签的列表
    """
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    tech = []
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        repo_info = response.json()
        tech = repo_info.get('topics', []) #获得topics部分
        print(f"{repo_name}: {tech}") #输出便于跟踪
        return tech
    else:
        print(f"{repo_name} Error: {response.status_code}")
        return []

def get_dict1():
    """
    获取所有仓库的主题标签，并存储在 result1 中
    格式: {仓库名: [主题标签列表]}
    """
    for repo_name, owner in repo_name_user.items():
        tech = get_repo_topics(repo_name, owner)
        if tech:
            result1[repo_name] = tech

def get_dict2():
    """
    将 result1 中的数据重新组织，生成主题标签到仓库的映射
    并统计每个主题标签出现的次数
    
    返回:
        result: 包含出现次数大于1的主题标签及其频次的字典
    """
    # 构建主题标签到仓库的映射
    for repo_name, tech in result1.items():
        for t in tech:
            if t in result2:
                result2[t].append(repo_name) #去重
            else:
                result2[t] = [repo_name]
    
    # 统计主题标签出现次数
    result = {}
    for k, v in list(result2.items()):
        if len(v) > 1:  # 只保留出现次数大于1的主题标签
            result[k] = len(v) #统计个数
        else:
            result2.pop(k)
    return result


# 执行主题标签获取和统计
get_dict1()
result = get_dict2()

# 保存详细的主题标签-仓库映射关系
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_topics-details.json', 'w') as f:
    json.dump(result2, f, indent=4)

# 保存主题标签出现次数统计
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_topics-count.json', 'w') as f:
    json.dump(result, f, indent=4)






