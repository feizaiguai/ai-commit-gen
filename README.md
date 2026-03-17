# AI Commit Message Generator

智能提交信息生成器，自动分析 git diff 生成规范的 commit message。

## 功能特性

- 🎯 支持 Conventional Commits 格式
- 🌐 多语言支持（中文/英文）
- ⚡ 快速从 git diff 生成提交信息
- 📋 自动分析变更类型

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
# 从当前 git diff 生成提交信息
python main.py

# 从文件读取 diff
python main.py diff.txt
```

## 提交类型

支持以下提交类型：

- `feat` - 新功能
- `fix` - 修复bug
- `docs` - 文档更新
- `style` - 代码格式
- `refactor` - 重构
- `perf` - 性能优化
- `test` - 测试相关
- `chore` - 构建/工具

## 示例输出

```
feat(api): 添加用户认证功能

### 变更的文件:
- src/auth/login.py
- src/auth/register.py
```

## 使用前提

需要在 git 仓库中运行，并确保有暂存的更改。

## 作者

- 邮箱: 196408245@qq.com
