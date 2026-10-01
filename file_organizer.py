"""file_organizer.py —— 按文件后缀，把文件夹里的文件分门别类地归档。

用法：
    py file_organizer.py
    然后输入要整理的文件夹路径（比如 D:\\下载\\杂七杂八）

流程：
    1. 扫描目标文件夹第一层的文件（子文件夹一律跳过）
    2. 按后缀分类，先"预演"列出每个文件将要去哪个文件夹
    3. 输入 y 确认后，才真正创建文件夹并移动文件

安全设计（重要）：
    - 只处理第一层文件，子文件夹原地不动
    - 不删除任何东西；目标已有同名文件时自动改名，绝不覆盖
    - 会跳过脚本自己（免得把自己也移走）
    - 没确认之前不动任何文件
"""

import os
import shutil

# 没有后缀的文件（比如 README、Makefile）统一放进这个文件夹
NO_EXTENSION_FOLDER = "no_extension"

# 脚本自己的绝对路径，用来在整理时跳过自身
SELF_PATH = os.path.abspath(__file__)


def ask_target_folder():
    """询问要整理的文件夹路径。直接回车 = 取消，不做任何操作。"""
    text = input("请输入要整理的文件夹路径（直接回车 = 取消）：").strip()
    # 容忍用户直接从资源管理器复制来带引号的路径
    text = text.strip('"').strip("'")
    if not text:
        return None
    return os.path.abspath(text)


def collect_files(target):
    """列出目标文件夹第一层的文件，返回 [(文件名, 目标文件夹名), ...]。"""
    plan = []
    for name in sorted(os.listdir(target)):
        full_path = os.path.join(target, name)

        if os.path.isdir(full_path):
            print(f"  [跳过] {name}（是文件夹，原地不动）")
            continue
        if os.path.abspath(full_path) == SELF_PATH:
            print(f"  [跳过] {name}（这是脚本自己）")
            continue

        # 后缀统一转小写，.JPG 和 .jpg 归为同一类
        extension = os.path.splitext(name)[1].lstrip(".").lower()
        folder = extension if extension else NO_EXTENSION_FOLDER
        plan.append((name, folder))

    return plan


def unique_path(folder_path, filename):
    """目标文件夹里已有同名文件时自动改名：photo.jpg -> photo(2).jpg，绝不覆盖。"""
    stem, extension = os.path.splitext(filename)
    candidate = os.path.join(folder_path, filename)
    index = 2
    while os.path.exists(candidate):
        candidate = os.path.join(folder_path, f"{stem}({index}){extension}")
        index += 1
    return candidate


def show_preview(plan):
    """按目标文件夹分组，展示"打算怎么搬"——此时还没有动任何文件。"""
    groups = {}
    for name, folder in plan:
        groups.setdefault(folder, []).append(name)

    print("\n预演（还没有动任何文件）：")
    for folder in sorted(groups):
        names = groups[folder]
        print(f"  {folder}/   ← {len(names)} 个文件")
        for name in names:
            print(f"        {name}")


def do_move(target, plan):
    """真正执行移动。失败的文件单独报错，不中断整体。"""
    moved = 0
    failed = 0
    for name, folder in plan:
        folder_path = os.path.join(target, folder)
        source = os.path.join(target, name)
        try:
            os.makedirs(folder_path, exist_ok=True)  # 已存在就复用，不报错
            destination = unique_path(folder_path, name)
            shutil.move(source, destination)
            moved += 1
            print(f"  [已移动] {name}  →  {folder}/")
        except OSError as error:
            failed += 1
            print(f"  [失败] {name}：{error}")

    if failed:
        print(f"\n完成：成功移动 {moved} 个文件，失败 {failed} 个。")
    else:
        print(f"\n完成：成功移动 {moved} 个文件。")


def main():
    target = ask_target_folder()
    if target is None:
        print("已取消，没有做任何事。")
        return
    if not os.path.isdir(target):
        print(f"找不到文件夹：{target}")
        return

    print(f"\n准备整理：{target}")
    print("扫描结果：")
    plan = collect_files(target)

    if not plan:
        print("\n这一层没有可整理的文件，结束。")
        return

    show_preview(plan)

    answer = input("\n确认要按上面的方案移动吗？输入 y 执行，其它任意键取消：").strip().lower()
    if answer != "y":
        print("已取消，没有移动任何文件。")
        return

    print()
    do_move(target, plan)


if __name__ == "__main__":
    main()
