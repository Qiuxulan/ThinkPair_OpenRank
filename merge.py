# 尝试：将repos和description合并到hoverframe-repo.json中，后来弃用
import json

# 加载两个文件
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\fetch_topic-description.json', 'r') as f:
    fetch_data = json.load(f)

with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\hoverframe-repo.json', 'r') as f:
    hover_data = json.load(f)

# 将 fetch_data 中的描述信息加到 hover_data 中对应键的列表的最后
for key, description in fetch_data.items():
    if key in hover_data:
        # 假设 hover_data[key] 是一个列表，且我们需要把描述加到该列表的最后
        hover_data[key].append(description)
    else:
        # 如果 hover_data 中没有这个键，则创建一个新的列表，并加入描述
        hover_data[key] = [description]

# 保存更新后的 hoverframe-repo.json
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\hoverframe-repo.json', 'w') as f:
    json.dump(hover_data, f, indent=4)

print("数据更新成功!")
