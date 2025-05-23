import os
import re
from collections import defaultdict
import stat


def find_duplicate_files(folder_path):
    # 正则：匹配文件名主体 + 中英文括号数字 + 扩展名
    pattern = re.compile(r'^(?P<base_name>.*?)(\(|\（)(?P<number>\d+)(\)|\）)(?P<extension>\.[^.]+)$')
    duplicates = defaultdict(list)

    # 收集所有文件的完整路径，按文件名索引
    all_files = defaultdict(list)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            all_files[file].append(os.path.join(root, file))

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            match = pattern.match(file)
            if match:
                base_name_with_ext = match.group('base_name') + match.group('extension')
                full_path = os.path.join(root, file)
                # 检查是否存在主体文件（不带括号数字）
                if base_name_with_ext in all_files:
                    duplicates[base_name_with_ext].append(full_path)

    # 过滤出有匹配的主体
    return {k: v for k, v in duplicates.items() if len(v) > 0}, all_files


def can_write(path):
    """检查文件是否可写"""
    if not os.path.exists(path):
        return False
    try:
        os.chmod(path, stat.S_IWRITE)
        return True
    except:
        return False


if __name__ == "__main__":
    folder_path = input("请输入文件夹地址：").strip()
    if not os.path.exists(folder_path):
        print("输入的文件夹地址不存在，请检查后重新运行。")
        exit()

    print("\n正在扫描文件...")
    duplicate_files, all_files = find_duplicate_files(folder_path)

    if not duplicate_files:
        print("\n未找到符合条件的文件（要求：存在主体文件如“xxx.pdf”，且存在带(数字)或（数字）的文件如“xxx(1).pdf”）。")
        exit()

    print("\n找到以下符合条件的重复文件组（保留主体文件，删除带括号数字的文件）：")
    for base_name, paths in duplicate_files.items():
        print(f"\n主体文件：{base_name}")

        # 显示主体文件的保存路径
        if base_name in all_files:
            print("  保存路径：")
            for path in all_files[base_name]:
                print(f"    {path}")

        print("待删除文件：")
        for path in paths:
            status = "可删除" if can_write(path) else "拒绝访问"
            print(f"  {status}: {os.path.basename(path)}")
            print(f"     路径: {path}")

    choice = input("\n请输入 0 放弃删除，1 确认删除：").strip()
    if choice != '1':
        print("操作已取消，未删除任何文件。")
        exit()

    print("\n开始删除文件...")
    total = sum(len(paths) for paths in duplicate_files.values())
    success = 0
    failed = []

    for paths in duplicate_files.values():
        for path in paths:
            try:
                if not can_write(path):
                    failed.append((path, "权限不足"))
                    continue
                os.remove(path)
                success += 1
                print(f"✓ 已删除：{os.path.basename(path)}")
            except Exception as e:
                failed.append((path, str(e)))
                print(f"✗ 删除失败：{os.path.basename(path)} - {str(e)}")

    print(f"\n操作完成：成功删除 {success}/{total} 个文件。")
    if failed:
        print("\n删除失败的文件：")
        for path, error in failed:
            print(f"  {os.path.basename(path)} - {error}")
            print(f"     路径: {path}")
        print("\n提示：若权限问题持续存在，请尝试以管理员身份运行此脚本。")