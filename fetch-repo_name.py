from clickhouse_driver import Client
import json

# 设置 ClickHouse 客户端连接参数
client = Client(
    host='cc-2ze7189376o5m9759.public.clickhouse.ads.aliyuncs.com',
    port=9000,
    user='opensoda_2024',
    password='1eUr4jCLdYiR7Mdr',
    database='opensource',
)

def fetch_data():
    """
    从 ClickHouse 数据库获取 GitHub 上最近一个月内 PullRequestReviewComment 事件数量排名前300的仓库
    并将结果保存到 JSON 文件中
    """
    try:
        # 构建 SQL 查询语句：
        # 1. 筛选最近一个月内的 PullRequestReviewCommentEvent
        # 2. 限定平台为 GitHub 且动作为 created
        # 3. 按仓库名分组并计数
        # 4. 按数量降序排序，取前300个
        query="""SELECT repo_name AS n, COUNT(*) AS c
        FROM opensource.events
        WHERE (type = 'PullRequestReviewCommentEvent' AND pull_review_comment_updated_at >= now() - INTERVAL 1 MONTH) 
            AND platform = 'GitHub'
            AND action = 'created'
        GROUP BY n
        ORDER BY c DESC
        LIMIT 300"""

        # 执行查询并获取结果
        result = client.execute(query)
        repo_names = [row[0] for row in result]
        
        # 检查查询结果是否为空
        if not repo_names:
            print("查询结果为空")
            return        
        
        print("数据抓取成功")
        repo_data = {}  # 创建字典用于存储仓库信息，格式：{repository: username}
        
        # 遍历结果，将仓库全名拆分为用户名和仓库名
        for repo_name in repo_names:
            if '/' in repo_name:  # 确保仓库名包含用户名（格式：username/repository）
                username, repository = repo_name.split('/', 1)  # 以第一个斜杠分割
                repo_data[repository] = username  # 存储格式：仓库名作为键，用户名作为值
        
        # 将处理后的数据写入 JSON 文件
        with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\get300-repo.json', 'w') as f:
            json.dump(repo_data, f, indent=4)

        print("数据已成功保存到 get300-repo.json 文件中")    
    
    except Exception as e:
        # 异常处理：打印错误信息
        print(f"连接失败: {e}")
    finally:
        # 确保在程序结束时关闭数据库连接
        client.disconnect()
fetch_data()

