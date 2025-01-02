import json

# 文件名
data_file = r"D:\华师大\openSoda 比赛\healthCount\2024-10_project_data.json"

# 原始权重（保持不变）
weights = {
    "activity.json": 0.35,
    "active_contributors": 0.06,
    "new_contributors.json": 0.06,
    "stars.json": 0.04,
    "technical_fork.json": 0.04,
    "change_intensity": 0.10,
    "refactor_ratio": 0.06,
    "net_feature_change": 0.04,
    "issue_response_time.json": 0.075,
    "change_request_response_time.json": 0.075,
    "issue_resolution_duration.json": 0.05,
    "change_request_resolution_duration.json": 0.05,
}

# 加载 JSON 文件数据
with open(data_file, "r") as f:
    repo_info = json.load(f)

# 初始化归一化辅助数据
min_max = {}

# 提取所有指标的最大值和最小值
for repo, metrics in repo_info.items():
    for metric, value in metrics.items():
        if metric not in min_max:
            min_max[metric] = {"min": float("inf"), "max": float("-inf")}
        min_max[metric]["min"] = min(min_max[metric]["min"], value)
        min_max[metric]["max"] = max(min_max[metric]["max"], value)

# 归一化函数（调整为 0-100 的范围）
def normalize(value, metric):
    min_val = min_max[metric]["min"]
    max_val = min_max[metric]["max"]
    if max_val - min_val == 0:  # 避免除以 0
        return 0
    return ((value - min_val) / (max_val - min_val)) * 100

# 健康度得分计算
health_scores = []

for repo, metrics in repo_info.items():
    # 提取和计算各项指标
    activity = normalize(metrics.get("activity.json", 0), "activity.json")
    active_contributors = normalize(
        metrics.get("participants.json", 0) - metrics.get("inactive_contributors.json", 0),
        "participants.json",
    )
    new_contributors = normalize(metrics.get("new_contributors.json", 0), "new_contributors.json")
    stars = normalize(metrics.get("stars.json", 0), "stars.json")
    technical_fork = normalize(metrics.get("technical_fork.json", 0), "technical_fork.json")

    # 代码变更相关
    change_intensity = normalize(
        metrics.get("code_change_lines_add.json", 0) + metrics.get("code_change_lines_remove.json", 0),
        "code_change_lines_add.json",
    )
    refactor_ratio = metrics.get("code_change_lines_remove.json", 0) / (
        metrics.get("code_change_lines_add.json", 0) + metrics.get("code_change_lines_remove.json", 0)
    ) if (metrics.get("code_change_lines_add.json", 0) + metrics.get("code_change_lines_remove.json", 0)) > 0 else 0
    refactor_ratio = normalize(refactor_ratio, "code_change_lines_remove.json")
    net_feature_change = normalize(metrics.get("code_change_lines_sum.json", 0), "code_change_lines_sum.json")

    # 响应时间相关
    issue_response_time = normalize(metrics.get("issue_response_time.json", 0), "issue_response_time.json")
    change_request_response_time = normalize(
        metrics.get("change_request_response_time.json", 0), "change_request_response_time.json"
    )
    issue_resolution_duration = normalize(
        metrics.get("issue_resolution_duration.json", 0), "issue_resolution_duration.json"
    )
    change_request_resolution_duration = normalize(
        metrics.get("change_request_resolution_duration.json", 0), "change_request_resolution_duration.json"
    )

    # 计算健康度得分
    score = (
        weights["activity.json"] * activity +
        weights["active_contributors"] * active_contributors +
        weights["new_contributors.json"] * new_contributors +
        weights["stars.json"] * stars +
        weights["technical_fork.json"] * technical_fork +
        weights["change_intensity"] * change_intensity +
        weights["refactor_ratio"] * refactor_ratio +
        weights["net_feature_change"] * net_feature_change +
        weights["issue_response_time.json"] * issue_response_time +
        weights["change_request_response_time.json"] * change_request_response_time +
        weights["issue_resolution_duration.json"] * issue_resolution_duration +
        weights["change_request_resolution_duration.json"] * change_request_resolution_duration
    )

    # 确保健康度得分不为负
    health_scores.append({"project": repo, "health_score": max(0, score)})

# 按健康度得分排序
health_scores = sorted(health_scores, key=lambda x: x["health_score"], reverse=True)

# 打印健康度排名
print("健康度排名：")
for rank, entry in enumerate(health_scores, start=1):
    print(f"{rank}. {entry['project']} - 健康度得分: {entry['health_score']:.2f}")

# 保存到结果文件
output_file = "health_scores.json"
with open(output_file, "w") as f:
    json.dump(health_scores, f, indent=4)

print(f"健康度排名已保存到 {output_file}")
