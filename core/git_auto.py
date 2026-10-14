# -*- coding:utf-8 -*-
"""
Git 自动化模块：自动 add、commit、push

设计要点：
- 参数化调用 git，不经过 shell，规避提交信息含引号导致的失效与命令注入
- 所有 git 调用带超时，避免网络异常时永久挂起
- 推送前校验远程仓库是否已配置，给出可操作的提示
- 准确区分「无变更」「无远程」「无上游分支」「推送失败」四种情况
"""
import os
import subprocess

from config.settings import BASE_DIR
from core.logger import get_logger

logger = get_logger("git")

# 本地命令（status/add/commit）超时较短；push 走网络，给足时间
LOCAL_TIMEOUT = 30
PUSH_TIMEOUT = 120


def _run_git(args: "list[str]", timeout: int = LOCAL_TIMEOUT) -> "subprocess.CompletedProcess | None":
    """在项目根目录执行 git 命令，返回 CompletedProcess；异常时返回 None"""
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        print("❌ 未找到 git 命令，请确认已安装 Git 并加入 PATH")
        logger.error("git 命令不存在")
        return None
    except subprocess.TimeoutExpired:
        print(f"❌ git {' '.join(args[:1])} 执行超时（{timeout}s），已中止")
        logger.error("git %s 超时", args)
        return None


def is_git_repo() -> bool:
    """判断项目是否已初始化 git 仓库"""
    return os.path.isdir(os.path.join(BASE_DIR, ".git"))


def has_remote() -> bool:
    """是否已配置远程仓库"""
    if not is_git_repo():
        return False
    ret = _run_git(["remote"])
    return bool(ret and ret.returncode == 0 and ret.stdout.strip())


def get_current_branch() -> str:
    """当前分支名，取不到返回空串"""
    ret = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return ret.stdout.strip() if ret and ret.returncode == 0 else ""


def get_change_summary() -> "list[str]":
    """返回当前变更文件列表（含未跟踪文件），无 git 环境返回空列表"""
    if not is_git_repo():
        return []
    ret = _run_git(["status", "--porcelain"])
    if not ret or ret.returncode != 0:
        return []
    return [line[3:] for line in ret.stdout.splitlines() if line.strip()]


def _try_pull_rebase_then_push() -> bool:
    """
    远程有新提交导致 push 被拒时，自动 git pull --rebase 并重试 push 一次（审计问题 7）。
    rebase 出现真冲突时中止（git rebase --abort）恢复现场，提示用户手动处理。
    """
    print("🔄 远程有新提交，尝试自动 git pull --rebase ...")
    rebase_ret = _run_git(["pull", "--rebase"], timeout=PUSH_TIMEOUT)
    if rebase_ret is None:
        return False
    if rebase_ret.returncode != 0:
        err = (rebase_ret.stderr or rebase_ret.stdout).strip()
        logger.error("git pull --rebase 失败：%s", err)
        print("⚠️ 自动变基失败（可能存在内容冲突），正在恢复原状态 ...")
        abort_ret = _run_git(["rebase", "--abort"])
        if abort_ret is not None and abort_ret.returncode != 0:
            print("⚠️ git rebase --abort 未成功，仓库可能处于变基中间状态，请手动执行：git rebase --abort")
        print("💡 本地提交已保留，请手动执行 git pull --rebase 解决冲突后重新同步")
        return False

    print("🚀 变基完成，重试 git push ...")
    retry_ret = _run_git(["push"], timeout=PUSH_TIMEOUT)
    if retry_ret is not None and retry_ret.returncode == 0:
        print("✅ Git 提交并推送成功（自动变基后重试）！")
        logger.info("自动 pull --rebase 后推送成功")
        return True
    err = (retry_ret.stderr or retry_ret.stdout).strip() if retry_ret else "未知错误"
    print(f"❌ 重试推送仍失败：{err}")
    logger.error("变基后重试 push 仍失败：%s", err)
    return False


def git_commit_and_push(commit_msg: str) -> bool:
    """
    执行 git add → commit → push
    :return: True 表示有变更且推送成功（或仅本地提交成功）；False 表示无需提交或推送失败
    """
    if not is_git_repo():
        print("❌ 当前项目还不是 git 仓库，请先执行 git init 并配置远程仓库")
        return False

    print("🔍 git add ...")
    add_ret = _run_git(["add", "-A"])
    if add_ret is None:
        return False
    if add_ret.returncode != 0:
        print(f"❌ git add 失败：{add_ret.stderr.strip()}")
        logger.error("git add 失败：%s", add_ret.stderr.strip())
        return False

    status = _run_git(["diff", "--cached", "--quiet"])
    if status is None:
        return False
    if status.returncode == 0:
        print("ℹ️ 没有文件变更，无需提交")
        return False

    branch = get_current_branch() or "当前分支"
    print(f"📝 git commit（{branch}）...")
    commit_ret = _run_git(["commit", "-m", commit_msg])
    if commit_ret is None:
        return False
    if commit_ret.returncode != 0:
        err = commit_ret.stderr.strip() or commit_ret.stdout.strip()
        print(f"❌ git commit 失败：{err}")
        logger.error("git commit 失败：%s", err)
        return False
    logger.info("已提交：%s", commit_msg)

    if not has_remote():
        print("⚠️ 已本地提交，但尚未配置远程仓库，跳过推送")
        print("💡 配置方式：git remote add origin <你的仓库地址>")
        return True

    print("🚀 git push ...")
    push_ret = _run_git(["push"], timeout=PUSH_TIMEOUT)
    if push_ret is None:
        return False
    if push_ret.returncode == 0:
        print("✅ Git 提交并推送成功！")
        logger.info("推送成功：%s", branch)
        return True

    err = (push_ret.stderr or push_ret.stdout).strip()
    low = err.lower()
    if "no upstream" in low or "has no upstream" in low:
        print(f"⚠️ 分支 {branch} 没有上游远程分支，首次推送请手动执行：")
        print(f"   git push -u origin {branch}")
    elif "rejected" in low or "fetch first" in low or "non-fast-forward" in low:
        # 远程有新提交：自动 pull --rebase 后重试一次（审计问题 7）
        return _try_pull_rebase_then_push()
    else:
        print(f"❌ Git 推送失败：{err}")
        print("💡 常见原因：网络异常 / 需要凭据认证 / 远程有新提交需先 pull")
    logger.error("git push 失败：%s", err)
    return False
