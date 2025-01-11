import json
from transformers import GPT2LMHeadModel, GPT2Tokenizer

with open(r'D:\Data_code\Competition\ItDSaE-openSODA-wordcloud\final_count.json', 'r') as f:
    technologies = json.load(f)

result= {}
# 加载预训练的 GPT-2 模型和分词器
model_name = "gpt2"  # 你可以选择其他更大的 GPT-2 变体（如 "gpt2-medium" 或 "gpt2-large"）
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

def tech_description(tech_name):
    input_text = f"Provide a brief technical description of the technology {tech_name}, in about 30 words."

    # 对输入文本进行编码
    inputs = tokenizer.encode(input_text, return_tensors="pt")

    # 生成简要介绍
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1, temperature=0.7, no_repeat_ngram_size=2)

    # 解码并打印生成的文本
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # 去除开头的“Provide a brief technical description...”部分
    # 假设模型返回的文本是以输入文本为前缀的
    summary = summary[len(input_text):].strip()

    print(f"{tech_name}: {summary}")
    result[tech_name] = summary

def tech_description_seri():
    for tech_name in technologies.keys():
        tech_description(tech_name)

tech_description_seri()

with open('D:\\Data_code\\Competition\\ItDSaE-openSODA-wordcloud\\fetch_topic-description.json', 'w') as f:
    json.dump(result, f, indent=4)

