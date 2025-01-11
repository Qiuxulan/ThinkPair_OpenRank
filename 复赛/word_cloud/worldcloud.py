import json
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image as Image
from matplotlib import colors

with open('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\repo_readme-details.json', 'r') as f:
    readme_datails = json.load(f)
with open('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\repo_topics-details.json', 'r') as f:
    topics_datails = json.load(f)
with open('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\repo_readme-count.json', 'r') as f:
    readme_count = json.load(f)
with open('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\repo_topics-count.json', 'r') as f:
    topics_count = json.load(f)

#合并count topics与readme权重为40%和60% 最终结果为topics_count
for tech in list(readme_count.keys()):
    if tech in topics_count.keys():
        topics_count[tech] += 1.5*readme_count[tech]
    else:
        topics_count[tech] = 1.5*readme_count[tech]
del topics_count['hacktoberfest'] #特殊数据单独处理

#word_positions = {}
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
    background = Image.open("D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\meow_transformed.png")
    mask = np.array(background)

    # 设置字体
    font_path = "C:\\Windows\\Fonts\\timesbd.ttf"
    # 设置字体大小
    max_font_size =40
    min_font_size =3
    
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
    '''["#B4A0FF",  # 浅紫色
        "#96C8FF",  # 浅蓝色
        "#DC96FF",  # 粉紫色
        "#FFFFFF",  # 白色
        "#FFC0DC",  # 淡粉色
        "#78B4C8",  # 浅灰蓝色
        "#6450A0",  # 深紫色
        "#78C8FF",  # 柔和的亮蓝色
        "#F0F0DC",  # 米白色
        "#A0C8FF"]  # 青紫色
    '''
    
        
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
                          max_font_size=max_font_size,     #最大字体大小
                          min_font_size=min_font_size).generate_from_frequencies(word_freq)

    wordcloud.to_file('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\wordcloud.png')

    # 显示词云
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    
    '''for item in wordcloud.layout_:
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
        }'''
    # 提取出现的关键词
    return wordcloud.words_
    
# 生成并显示词云
realwords=generate_wordcloud(topics_count)

#合并details 去重 用作悬浮框  最终结果为topics_datails
for repo in realwords.keys():
    realwords[repo] = []
    if repo in topics_datails.keys():
        realwords[repo]=list(set(realwords[repo]+topics_datails[repo]))[:5]
    if repo in readme_datails.keys():
        realwords[repo]=list(set(realwords[repo]+readme_datails[repo]))[:5]
        
with open('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\'hoverframe-repo.json, 'w') as f:
    json.dump(realwords, f, indent=4)
#with open('D:\\MyVScode\\Python\\ItDSaE-openSODA\\wordcloud\\word_position.json', 'w') as f:
    #son.dump(word_positions, f, indent=4)

