#!/usr/bin/env python3
"""
AI Commit Message Generator
自动分析 git diff 内容，生成规范的 commit message
支持 Conventional Commits 格式
"""

import argparse
import os
import subprocess
import sys
import re
from typing import Optional, Dict, List


class GitDiffAnalyzer:
    """分析 git diff 内容"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def get_diff(self, staged_only: bool = False) -> str:
        """获取 git diff 内容"""
        try:
            if staged_only:
                result = subprocess.run(
                    ["git", "diff", "--cached"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["git", "diff"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Error getting diff: {e}"
    
    def get_status(self) -> str:
        """获取 git status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error getting status: {e}"


class CommitMessageGenerator:
    """生成 commit message"""
    
    CONVENTIONAL_TYPES = {
        "feat": "新功能",
        "fix": "修复bug",
        "docs": "文档更新",
        "style": "代码格式（不影响功能）",
        "refactor": "代码重构",
        "perf": "性能优化",
        "test": "测试相关",
        "build": "构建系统或依赖",
        "ci": "CI配置",
        "chore": "其他修改",
        "revert": "回滚"
    }
    
    def __init__(self):
        self.diff_analyzer = GitDiffAnalyzer()
    
    def analyze_changes(self, diff: str) -> Dict[str, any]:
        """分析 diff 内容"""
        analysis = {
            "added_lines": 0,
            "deleted_lines": 0,
            "files_changed": set(),
            "file_types": set(),
            "has_tests": False,
            "has_docs": False,
            "change_summary": []
        }
        
        # 统计新增和删除的行数
        analysis["added_lines"] = len(re.findall(r'^\+[^+]', diff, re.MULTILINE))
        analysis["deleted_lines"] = len(re.findall(r'^-[^-]', diff, re.MULTILINE))
        
        # 提取修改的文件
        file_pattern = r'^\+\+\+ b/(.+)$|^diff --git a/(.+?) b/'
        files = re.findall(file_pattern, diff, re.MULTILINE)
        for f in files:
            filename = f[0] or f[1]
            if filename:
                analysis["files_changed"].add(filename)
                ext = os.path.splitext(filename)[1]
                if ext:
                    analysis["file_types"].add(ext)
                
                # 检查是否包含测试或文档文件
                if 'test' in filename.lower() or filename.endswith('_test.py'):
                    analysis["has_tests"] = True
                if 'readme' in filename.lower() or filename.endswith('.md'):
                    analysis["has_docs"] = True
        
        # 生成变更摘要
        for filename in list(analysis["files_changed"])[:10]:
            analysis["change_summary"].append(f"  - {filename}")
        
        return analysis
    
    def determine_type(self, analysis: Dict) -> str:
        """根据变更内容决定 commit 类型"""
        files = list(analysis["files_changed"])
        
        # 检查特定文件类型
        has_python = any(f.endswith('.py') for f in files)
        has_js = any(f.endswith(('.js', '.ts', '.jsx', '.tsx')) for f in files)
        has_docs = any('readme' in f.lower() or f.endswith('.md') for f in files)
        has_tests = any('test' in f.lower() for f in files)
        has_config = any(f in ['package.json', 'requirements.txt', 'setup.py', 'Dockerfile'] for f in files)
        
        # 基于文件路径推断类型
        if any('fix' in f.lower() for f in files if not f.startswith('.')):
            return "fix"
        if any('feat' in f.lower() or 'feature' in f.lower() for f in files):
            return "feat"
        if has_docs:
            return "docs"
        if has_tests and not has_python and not has_js:
            return "test"
        if has_config:
            return "chore"
        
        # 默认基于语言
        if has_python:
            return "feat"
        if has_js:
            return "feat"
        
        return "chore"
    
    def generate_message(self, diff: str, language: str = "en") -> str:
        """生成 commit message"""
        analysis = self.analyze_changes(diff)
        
        if not analysis["files_changed"]:
            return "No changes detected" if language == "en" else "未检测到变更"
        
        commit_type = self.determine_type(analysis)
        type_display = commit_type
        type_desc = self.CONVENTIONAL_TYPES.get(commit_type, "")
        
        # 生成简短描述
        files = list(analysis["files_changed"])[:5]
        if len(files) == 1:
            short_desc = os.path.basename(files[0])
        else:
            short_desc = f"{os.path.basename(files[0])} and {len(files)-1} more files"
        
        # 构建 commit message
        message_parts = []
        
        # Header
        if language == "zh":
            message_parts.append(f"{type_display}: {short_desc}")
            message_parts.append("")
            message_parts.append(f"## 变更内容")
        else:
            message_parts.append(f"{type_display}: {short_desc}")
            message_parts.append("")
            message_parts.append("## Changes")
        
        # Body
        for summary in analysis["change_summary"]:
            message_parts.append(summary)
        
        if len(analysis["files_changed"]) > 10:
            message_parts.append(f"  ... and {len(analysis['files_changed']) - 10} more files")
        
        # Footer - 统计信息
        message_parts.append("")
        if language == "zh":
            message_parts.append(f"## 统计")
            message_parts.append(f"- 文件数: {len(analysis['files_changed'])}")
            message_parts.append(f"- 新增行: +{analysis['added_lines']}")
            message_parts.append(f"- 删除行: -{analysis['deleted_lines']}")
        else:
            message_parts.append("## Statistics")
            message_parts.append(f"- Files: {len(analysis['files_changed'])}")
            message_parts.append(f"- Added: +{analysis['added_lines']}")
            message_parts.append(f"- Deleted: -{analysis['deleted_lines']}")
        
        return "\n".join(message_parts)


def main():
    parser = argparse.ArgumentParser(
        description="AI Commit Message Generator - Generate commit messages from git diff"
    )
    parser.add_argument(
        "--staged", "-s",
        action="store_true",
        help="Use staged changes only"
    )
    parser.add_argument(
        "--language", "-l",
        choices=["en", "zh"],
        default="en",
        help="Output language (default: en)"
    )
    parser.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy message to clipboard"
    )
    parser.add_argument(
        "--path", "-p",
        default=".",
        help="Repository path (default: current directory)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    # 分析 diff
    analyzer = GitDiffAnalyzer(args.path)
    diff = analyzer.get_diff(staged_only=args.staged)
    
    if not diff.strip():
        print("No changes detected.", file=sys.stderr)
        sys.exit(1)
    
    # 生成 message
    generator = CommitMessageGenerator()
    message = generator.generate_message(diff, language=args.language)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"Message saved to {args.output}")
    else:
        print(message)
    
    # 复制到剪贴板
    if args.copy:
        try:
            import pyperclip
            pyperclip.copy(message)
            print("\n✓ Message copied to clipboard!")
        except ImportError:
            print("\n⚠ pyperclip not installed. Run: pip install pyperclip")


if __name__ == "__main__":
    main()
