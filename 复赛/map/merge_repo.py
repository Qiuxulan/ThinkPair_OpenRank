import json
import os
import logging
import argparse

def setup_logging(log_file):
    """
    设置日志记录。
    :param log_file: 日志文件路径
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def read_json_file(file_path):
    """
    读取 JSON 文件并返回其内容。
    :param file_path: JSON 文件路径
    :return: 解析后的 JSON 数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"成功读取文件：{file_path}")
        return data
    except FileNotFoundError:
        logging.error(f"文件未找到：{file_path}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"无法解析 JSON 文件 {file_path}：{e}")
        return None
    except Exception as e:
        logging.error(f"读取文件 {file_path} 时出错：{e}")
        return None

def get_openrank_value(openrank_path):
    """
    从 openrank.json 文件中提取 '2024-10' 的值。
    :param openrank_path: openrank.json 文件路径
    :return: '2024-10' 对应的值，若不存在则返回 None
    """
    openrank_data = read_json_file(openrank_path)
    if openrank_data is None:
        return None
    openrank_value = openrank_data.get('2024-10', None)
    if openrank_value is None:
        logging.warning(f"'2024-10' 数据在 {openrank_path} 中不存在。")
    return openrank_value

def merge_repositories(repo_info, descriptions, data_collection_path):
    """
    合并所有仓库的信息。
    :param repo_info: 仓库基本信息列表
    :param descriptions: 仓库描述列表
    :param data_collection_path: data_collection 文件夹路径
    :return: 合并后的仓库信息列表
    """
    if not isinstance(repo_info, list):
        logging.error("repo_info.json 的结构不符合预期，应为一个列表。")
        return []
    if not isinstance(descriptions, list):
        logging.error("description.json 的结构不符合预期，应为一个列表。")
        return []
    
    if len(repo_info) != len(descriptions):
        logging.error(f"repo_info.json 中的仓库数量 ({len(repo_info)}) 与 description.json 中的描述数量 ({len(descriptions)}) 不匹配。")
        # 根据需求决定是否继续合并
        # 这里选择继续，只处理数量匹配的部分
        min_length = min(len(repo_info), len(descriptions))
        logging.info(f"将仅合并前 {min_length} 个仓库。")
    else:
        min_length = len(repo_info)
        logging.info(f"repo_info.json 和 description.json 中均有 {min_length} 个条目。")

    merged_repos = []

    for index in range(min_length):
        repo = repo_info[index]
        description_entry = descriptions[index]
        description = description_entry.get('description', '').strip()

        try:
            full_name = repo.get('repo', '').strip()
            if not full_name:
                logging.warning(f"第 {index+1} 个仓库的 'repo' 字段为空。跳过此仓库。")
                continue

            html_url = f"https://github.com/{full_name}"
            latitude = repo.get('latitude', None)
            longitude = repo.get('longitude', None)
            location = repo.get('location', None)

            owner = repo.get('owner', '').strip()
            if not owner:
                logging.warning(f"仓库 '{full_name}' 缺少 'owner' 字段。")
                owner = "UnknownOwner"

            # 提取仓库名称，从 "owner/repo_name" 中获取 "repo_name"
            repo_name = full_name.split('/')[-1]

            # 构建仓库文件夹路径：data_collection/<owner>/<repo_name>/openrank.json
            repo_folder_path = os.path.join(data_collection_path, owner, repo_name)
            openrank_path = os.path.join(repo_folder_path, 'openrank.json')

            if not os.path.isdir(repo_folder_path):
                logging.warning(f"仓库文件夹不存在：{repo_folder_path}。设置 openrank 为 None。")
                openrank = None
            elif not os.path.isfile(openrank_path):
                logging.warning(f"openrank.json 文件不存在于 {repo_folder_path}。设置 openrank 为 None。")
                openrank = None
            else:
                openrank = get_openrank_value(openrank_path)

            merged_repo = {
                "full_name": full_name,
                "html_url": html_url,
                "latitude": latitude,
                "longitude": longitude,
                "location": location,
                "description": description,
                "openrank": openrank
            }

            merged_repos.append(merged_repo)
            logging.info(f"已合并仓库：{full_name}")

        except Exception as e:
            logging.error(f"处理第 {index+1} 个仓库 '{full_name}' 时出错：{e}")

    return merged_repos

def main():
    # 直接在脚本中定义文件路径
    repo_info_path = r"D:\华师大\openSoda 比赛\地图\repo_info.json"
    description_path = r"D:\华师大\openSoda 比赛\地图\description.json"
    data_collection_path = r"D:\华师大\openSoda 比赛\data_collection"
    output_path = r"D:\华师大\openSoda 比赛\地图\merged_repositories.json"
    log_path = r"D:\华师大\openSoda 比赛\地图\merge_repositories.log"
    
    # 设置日志记录
    setup_logging(log_path)

    # 读取 repo_info.json
    repo_info = read_json_file(repo_info_path)
    if repo_info is None:
        logging.critical("无法继续执行，因为 repo_info.json 读取失败。")
        return

    # 读取 description.json
    descriptions = read_json_file(description_path)
    if descriptions is None:
        logging.critical("无法继续执行，因为 description.json 读取失败。")
        return

    # 合并仓库信息
    merged_repos = merge_repositories(repo_info, descriptions, data_collection_path)

    if not merged_repos:
        logging.critical("没有合并任何仓库信息。请检查输入文件和 data_collection 文件夹。")
        return

    # 创建最终的 JSON 结构
    final_data = {
        "repositories": merged_repos
    }

    # 将合并后的数据写入输出文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        logging.info(f"成功：所有仓库信息已合并到 {output_path}")
    except Exception as e:
        logging.error(f"无法写入输出文件 {output_path}：{e}")

if __name__ == "__main__":
    main()