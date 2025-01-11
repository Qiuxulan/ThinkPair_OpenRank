from clickhouse_driver import Client
import datetime

# 设置 ClickHouse 客户端连接
client = Client(
    host='cc-2ze7189376o5m9759.public.clickhouse.ads.aliyuncs.com',
    port=9000,  
    user='opensoda_2024',
    password='1eUr4jCLdYiR7Mdr',
    database='opensource'
)

# 连接数据库并执行查询
def fetch_data():
    try:
        result = client.execute('')
        print("数据抓取成功，结果如下：")
        if not result:
            print("查询结果为空")
        for row in result:
            print(row)
    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    fetch_data()
