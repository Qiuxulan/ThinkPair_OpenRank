import os

# 输入和输出文件路径
input_file = r"C:\Users\大头\Desktop\repo_name.txt"
output_file = r"C:\Users\大头\Desktop\repo_url.txt"

def convert_repos(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            repo = line.strip()
            if repo:
                clone_url = f"https://github.com/{repo}.git"
                outfile.write(f"{clone_url}\n")
    print(f"转换完成，已保存到 {output_path}")

if __name__ == "__main__":
    convert_repos(input_file, output_file)
