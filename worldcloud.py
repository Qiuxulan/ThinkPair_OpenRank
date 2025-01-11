# wordcloud词云代码，尝试后发现用词云图片加关键词坐标无法将悬浮窗功能部署在网页中，
# 故改用html直接生成词云并绑定悬浮框
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image as Image
from matplotlib import colors

with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_readme-details.json', 'r') as f:
    readme_datails = json.load(f)
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_topics-details.json', 'r') as f:
    topics_datails = json.load(f)
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_readme-count.json', 'r') as f:
    readme_count = json.load(f)
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\repo_topics-count.json', 'r') as f:
    topics_count = json.load(f)

#合并count topics与readme权重为40%和60% 最终结果为topics_count
for tech in list(readme_count.keys()):
    if tech in topics_count.keys():
        topics_count[tech] += 1.5*readme_count[tech]
    else:
        topics_count[tech] = 1.5*readme_count[tech]
del topics_count['hacktoberfest']
del topics_count['Android'] #特殊数据单独处理

# 将字典按数量降序排序，并获取前30个技术
top_30_tech = dict(sorted(topics_count.items(), key=lambda item: item[1], reverse=True)[:30])

word_positions = {}
#生成词云，实现：1.词云形状——背景图形状+透明 2.字体、大小、颜色、排列方式等美观程度 3.悬浮框显示topics的description和repos
def generate_wordcloud(word_freq):
    """
    生成词云图
    实现功能：
    1. 词云形状 - 使用背景图形状并支持透明背景
    2. 自定义字体、大小、颜色、排列方式等视觉效果
    3. 支持悬浮框显示 topics 的描述和相关仓库
    """

    #设置png掩膜
    background = Image.open("D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\meow_transformed.png")
    mask = np.array(background)

    # 设置字体
    font_path = "C:\\Windows\\Fonts\\timesbd.ttf"
    
    # 建立颜色数组，可更改颜色
    color_list = [
        "#00FFFF",  # 青绿色
        "#7FFF00",  # 亮绿色
        "#A8D5BA",  # 柔和浅绿色
        "#40E0D0",  # 蓝绿色
        "#E0FFFF",  # 浅蓝白色
        "#98FB98",  # 薄荷绿
        "#87CEEB",  # 柔和湖蓝色
        "#ADD8E6",  # 亮天蓝色
        "#F0FFFF"   # 青白色
    ]
           
    # 调用颜色数组
    colormap = colors.ListedColormap(color_list)
    # 生成词云
    wordcloud = WordCloud(scale=4,
                          font_path=font_path,
                          colormap=colormap,
                          width=800, 
                          height=400, 
                          max_words=45,
                          background_color=None,  # 背景颜色设置为 None
                          mode="RGBA", # 支持透明背景
                          mask=mask,
                          max_font_size=40,     #最大字体大小
                          min_font_size=3).generate_from_frequencies(word_freq)

    wordcloud.to_file('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\wordcloud.png')

    # 显示词云
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    
    for item in wordcloud.layout_:
        # 先打印看看 position 的实际内容
        print(f"Position: {item[2]}")
        
        word = item[0][0]
        position = item[2]
        
        # 只使用可用的坐标
        word_positions[word] = {
            'x': int(position[0]),
            'y': int(position[1]),
            'width': 100,  # 使用固定宽度
            'height': 50   # 使用固定高度
        }
    
# 生成并显示词云
generate_wordcloud(topics_count)

final_detail = {}
#合并details 去重 用作悬浮框  最终结果为final_datails
for repo in top_30_tech.keys():
    final_detail[repo] = []
    if repo in topics_datails.keys():
        final_detail[repo]=list(set(final_detail[repo]+topics_datails[repo]))[:5]
    if repo in readme_datails.keys():
        final_detail[repo]=list(set(final_detail[repo]+readme_datails[repo]))[:5]


with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\final_details.json', 'w') as f:
    json.dump(final_detail, f, indent=4)
with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\final_count.json', 'w') as f:
    json.dump(top_30_tech, f, indent=4)

with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\word_position.json', 'w') as f:
    json.dump(word_positions, f, indent=4)





