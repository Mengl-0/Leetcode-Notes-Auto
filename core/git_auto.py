# -*- coding:utf-8 -*-
"""
Git 自动化模块：自动 add、commit、push
不依赖 shell=True，规避提交信息中含引号导致的命令注入/失效问题
"""
import os
import subprocess

from config.settings import BASE_DIR


def _run_git(args):
    """在项目根目录执行 git 命令，返回 CompletedProcess"""
    return subprocess.run(
        ["git"] + args,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def is_git_repo():
    """判断项目是否已初始化 git 仓库"""
    return os.path.isdir(os.path.join(BASE_DIR, ".git"))


def get_change_summary():
    """返回当前变更文件列表（含未跟踪文件），无 git 环境返回空列表"""
    if not is_git_repo():
        return []
    ret = _run_git(["status", "--porcelain"])
    if ret.returncode != 0:
        return []
    return [line[3:] for line in ret.stdout.splitlines() if line.strip()]


def git_commit_and_push(commit_msg: str):
    """
    执行 git add → commit → push
    :return: True 表示有变更且推送成功；False 表示无需提交或推送失败
    """
    if not is_git_repo():
        print("❌ 当前项目还不是 git 仓库，请先执行 git init 并配置远程仓库")
        return False

    print("🔍 git add ...")
    add_ret = _run_git(["add", "-A"])
    if add_ret.returncode != 0:
        print(f"❌ git add 失败：{add_ret.stderr.strip()}")
        return False

    status = _run_git(["diff", "--cached", "--quiet"])
    if status.returncode == 0:
        print("ℹ️ 没有文件变更，无需提交")
        return False

    print("📝 git commit ...")
    commit_ret = _run_git(["commit", "-m", commit_msg])
    if commit_ret.returncode != 0:
        print(f"❌ git commit 失败：{commit_ret.stderr.strip() or commit_ret.stdout.strip()}")
        return False

    print("🚀 git push ...")
    push_ret = _run_git(["push"])
    if push_ret.returncode == 0:
        print("✅ Git 提交并推送成功！")
        return True

    err = (push_ret.stderr or push_ret.stdout).strip()
    if "no upstream" in err.lower() or "repository has no upstream" in err.lower():
        print("⚠️ 当前分支没有上游远程分支，首次推送请手动执行：git push -u origin <分支名>")
    else:
        print(f"❌ Git 推送失败：{err}")
        print("💡 常见原因：未配置远程仓库 / 网络异常 / 需要凭据，可手动 git push 排查")
    return False
