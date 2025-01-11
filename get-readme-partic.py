import base64
import requests
import json
import re
import spacy

# 使用 SpaCy 提取英文技术名词
nlp = spacy.load("en_core_web_sm")

with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\get300-repo.json', 'r') as f:
    repo_names = json.load(f)

HEADERS = {
    "Authorization": "token 隐私信息无法通过github提交"  
}# 我的 GitHub Token

all_words_count = {}
# 获取 README 文件的内容
def get_readme_content(repo_name,owner):
    readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
    try:
        response = requests.get(readme_url,headers=HEADERS)
        response.raise_for_status()
        data=response.json()
        readme_content = base64.b64decode(data['content']).decode('utf-8')
        # README 文件内容是 base64 编码的
        return readme_content
    except requests.exceptions.HTTPError as http_err:
        # 如果是 HTTP 错误，比如 404 (Not Found)，则打印错误并跳过
        print(f"HTTP error occurred for {repo_name}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        # 其他请求相关的错误（如网络问题）
        print(f"Request error occurred for {repo_name}: {req_err}")
    except Exception as e:
        # 捕获所有其他异常
        print(f"An error occurred for {repo_name}: {e}")

    return ""  # 如果发生错误，返回空字符串表示读取失败

#数据清洗
# 检查字符串是否只包含字母、空格和连字符
def check_string(s):
    pattern = re.compile('[^a-zA-Z -]')
    return not bool(pattern.search(s))

def extract_technical_words(text):
    doc = nlp(text)
    tech_entities = []
    for ent in doc.ents:
        # 只考虑技术相关实体，如编程语言、框架、库等
        if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART','LANGUAGE'] and check_string(ent.text) and (ent.text.rstrip() not in tech_entities):  # 这些实体可能是技术名词
            tech_entities.append(ent.text.rstrip())
    return tech_entities
    
# 对 README 文件中的技术词汇进行词频统计
def count_readme_word_frequency(repo_names):
    all_words = {}
    i=0
    for repo in repo_names.keys():
        i+=1
        readme_content = get_readme_content(repo,repo_names[repo])
        if readme_content:
            words = extract_technical_words(readme_content)
            for word in words:
                if word in all_words.keys():
                    all_words[word].append(repo)
                else:
                    all_words[word] =[repo] 
    return all_words

# 示例：假设 repo_names 是 300 个仓库的字典
i=0
readme_word_details = count_readme_word_frequency(repo_names)
for word in list(readme_word_details.keys()):
    freq = len(readme_word_details[word])
    if freq <= 1:
        readme_word_details.pop(word)
        # 只保留出现次数大于 1 的词汇
    else:
        i+=1
        print(f"{i} {word}: {readme_word_details[word]}")
        all_words_count[word] = freq
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_readme-details.json', 'w') as f:
    json.dump(readme_word_details, f,indent=4)
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_readme-count.json', 'w') as f:
    json.dump(all_words_count, f, indent=4)