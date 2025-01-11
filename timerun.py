import subprocess

# 要运行的 Python 脚本路径
scripts = [
    r'D:\Data_code\Competition\ItDSaE-openSODA-wordcloud\fetch-repo_name.py',
    r'D:\Data_code\Competition\ItDSaE-openSODA-wordcloud\get-topics.py',
    r'D:\Data_code\Competition\ItDSaE-openSODA-wordcloud\get-readme-partic.py',
    r'D:\Data_code\Competition\ItDSaE-openSODA-wordcloud\worldcloud.py',
    r'D:\Data_code\Competition\ItDSaE-openSODA-wordcloud\topics-description.py',
]

# 按顺序执行每个脚本
for script in scripts:
    print(f"Running {script}...")
    subprocess.run(['python', script])
