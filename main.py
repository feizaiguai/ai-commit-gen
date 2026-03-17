#!/usr/bin/env python3
"""
AI Commit Message Generator - 智能提交信息生成器
分析 git diff 自动生成规范的 commit message
"""

import subprocess
import sys
import re
from typing import List, Dict, Any
from colorama import init, Fore, Style

init(autoreset=True)


class CommitMessageGenerator:
    """提交信息生成器"""
    
    def __init__(self):
        self.conventional_types = {
            'feat': '新功能',
            'fix': '修复bug',
            'docs': '文档更新',
            'style': '代码格式',
            'refactor': '重构',
            'perf': '性能优化',
            'test': '测试相关',
            'chore': '构建/工具',
        }
    
    def generate_from_diff(self) -> str:
        """从 git diff 生成提交信息"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged'],
                capture_output=True,
                text=True,
                check=True
            )
            
            diff = result.stdout
            
            if not diff:
                print(f"{Fore.YELLOW}没有暂存的更改")
                return ""
            
            print(f"{Fore.CYAN}正在分析 git diff...\n")
            
            # 分析 diff 内容
            analysis = self._analyze_diff(diff)
            
            # 生成提交信息
            message = self._generate_message(analysis)
            
            return message
            
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}请确保在 git 仓库中运行此命令")
            return ""
        except Exception as e:
            print(f"{Fore.RED}生成失败: {str(e)}")
            return ""
    
    def generate_from_diff_text(self, diff_text: str) -> str:
        """从提供的 diff 文本生成提交信息"""
        if not diff_text.strip():
            print(f"{Fore.YELLOW}diff 内容为空")
            return ""
        
        analysis = self._analyze_diff(diff_text)
        return self._generate_message(analysis)
    
    def _analyze_diff(self, diff: str) -> Dict[str, Any]:
        """分析 diff 内容"""
        analysis = {
            'type': 'chore',
            'scope': '',
            'changes': [],
            'files': [],
            'has_tests': False,
            'has_docs': False,
        }
        
        lines = diff.split('\n')
        current_file = None
        
        for line in lines:
            # 检测文件变更
            if line.startswith('+++'):
                match = re.search(r'\+\+\+ [ab]/(.+)', line)
                if match:
                    current_file = match.group(1)
                    if current_file not in analysis['files']:
                        analysis['files'].append(current_file)
            
            # 检测变更类型
            if line.startswith('+') and not line.startswith('+++'):
                change_type = self._classify_change(line)
                if change_type:
                    analysis['changes'].append(change_type)
                    
                    if 'test' in change_type.lower():
                        analysis['has_tests'] = True
                    if 'doc' in change_type.lower():
                        analysis['has_docs'] = True
            
            if line.startswith('-') and not line.startswith('---'):
                change_type = self._classify_change(line)
                if change_type:
                    analysis['changes'].append(change_type)
        
        # 确定主要类型
        if analysis['has_docs'] and not analysis['has_tests']:
            analysis['type'] = 'docs'
        elif 'feat' in analysis['changes'] or 'function' in analysis['changes']:
            analysis['type'] = 'feat'
        elif 'fix' in analysis['changes']:
            analysis['type'] = 'fix'
        elif 'style' in analysis['changes']:
            analysis['type'] = 'style'
        
        # 提取范围
        if analysis['files']:
            first_file = analysis['files'][0]
            if '/' in first_file:
                analysis['scope'] = first_file.split('/')[0]
        
        return analysis
    
    def _classify_change(self, line: str) -> str:
        """分类变更内容"""
        line_lower = line.lower()
        
        if any(keyword in line_lower for keyword in ['def ', 'class ', 'function ', '=>']):
            return 'feat'
        elif any(keyword in line_lower for keyword in ['fix', 'bug', 'error', 'wrong']):
            return 'fix'
        elif any(keyword in line_lower for keyword in ['test', 'spec', 'jest', 'pytest']):
            return 'test'
        elif any(keyword in line_lower for keyword in ['doc', 'readme', 'comment']):
            return 'docs'
        elif any(keyword in line_lower for keyword in ['import', 'require']):
            return 'chore'
        
        return 'chore'
    
    def _generate_message(self, analysis: Dict[str, Any]) -> str:
        """生成提交信息"""
        msg_type = analysis['type']
        scope = analysis.get('scope', '')
        
        # Conventional Commits 格式
        header = f"{msg_type}"
        if scope:
            header += f"({scope})"
        
        # 生成描述
        description = self._generate_description(analysis)
        
        # 生成正文
        body = self._generate_body(analysis)
        
        # 组装消息
        message = f"{header}: {description}\n"
        if body:
            message += f"\n{body}\n"
        
        return message
    
    def _generate_description(self, analysis: Dict[str, Any]) -> str:
        """生成描述"""
        changes = analysis['changes']
        files = analysis['files']
        
        if not changes and not files:
            return "更新代码"
        
        # 简单描述
        if 'feat' in changes:
            return f"添加新功能到 {analysis.get('scope', '项目')}"
        elif 'fix' in changes:
            return f"修复 {analysis.get('scope', '项目')} 中的问题"
        elif files:
            filename = files[0].split('/')[-1]
            return f"更新 {filename}"
        
        return "更新代码"
    
    def _generate_body(self, analysis: Dict[str, Any]) -> str:
        """生成正文"""
        lines = []
        
        if analysis['files']:
            lines.append("### 变更的文件:")
            for f in analysis['files'][:5]:  # 最多显示5个文件
                lines.append(f"- {f}")
        
        return '\n'.join(lines)


def main():
    """主函数"""
    generator = CommitMessageGenerator()
    
    print(f"{Fore.CYAN}AI Commit Message Generator")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    if len(sys.argv) > 1:
        # 从文件读取 diff
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                diff_text = f.read()
            message = generator.generate_from_diff_text(diff_text)
        except Exception as e:
            print(f"{Fore.RED}读取文件失败: {str(e)}")
            sys.exit(1)
    else:
        # 从 git 获取 diff
        message = generator.generate_from_diff()
    
    if message:
        print(f"{Fore.GREEN}生成的提交信息:\n")
        print(f"{Fore.WHITE}{message}")
        
        print(f"\n{Fore.YELLOW}使用方法:")
        print(f"  git commit -m '{message}'")
    else:
        print(f"{Fore.YELLOW}未能生成提交信息")


if __name__ == '__main__':
    main()
