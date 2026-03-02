# 创建 GitHub Release 指南

v0.3.0 标签已推送到 GitHub，现在需要在 GitHub 网页上创建正式的 Release。

## 步骤

### 1. 访问 Releases 页面

打开浏览器，访问：
```
https://github.com/wsyh4567/DATAVIZ-STUDIO/releases/new
```

或者：
1. 进入项目主页：https://github.com/wsyh4567/DATAVIZ-STUDIO
2. 点击右侧的 "Releases"
3. 点击 "Draft a new release" 按钮

### 2. 填写 Release 信息

#### 选择标签
- **Tag**: 选择 `v0.3.0`（已存在的标签）
- **Target**: `feature/data-workshop-redesign` 分支

#### 填写标题
```
v0.3.0 - 项目结构重构和文档完善
```

#### 填写描述

复制以下内容到描述框：

```markdown
## 🎉 版本亮点

v0.3.0 是一个重要的维护版本，专注于项目结构优化和代码组织改进。

### 核心改进
- ✨ 项目结构重构 - 更清晰的目录组织
- 📁 测试文件规范化 - 按功能分类的测试结构
- 📚 文档完善 - 新增项目结构说明文档
- 🔧 代码质量提升 - 更好的可维护性

---

## ✨ 新增功能

### 项目结构优化
- 创建 `scripts/` 目录存放工具脚本
- 创建 `docs/archived/` 目录存放归档文档
- 创建 `tests/integration/`、`tests/manual/`、`tests/archived/` 分类测试

### 文档改进
- 新增 `PROJECT_STRUCTURE.md` - 完整的项目结构说明
- 新增 `CHANGELOG.md` - 遵循规范的更新日志
- 新增 `scripts/README.md` - 工具脚本说明
- 新增 `docs/archived/README.md` - 归档文档索引
- 更新 `tests/README.md` - 测试文件说明

---

## 🔧 改进优化

- 清理根目录，移除散乱的临时文件
- 将历史文档移至归档目录
- 将工具脚本集中到 scripts 目录
- 按功能分类组织测试文件
- 更新 `.gitignore` 忽略日志和覆盖率文件

---

## 🐛 Bug 修复

- 修复 DataTable 在暗色主题下的文本可见性问题
- 修复浅色主题的玻璃效果显示问题
- 优化主题切换的平滑过渡

---

## 📦 安装使用

### 克隆项目
\`\`\`bash
git clone -b v0.3.0 https://github.com/wsyh4567/DATAVIZ-STUDIO.git
cd DATAVIZ-STUDIO
\`\`\`

### 安装依赖
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 启动应用
\`\`\`bash
python app.py
\`\`\`

---

## 📚 完整文档

- [更新日志](https://github.com/wsyh4567/DATAVIZ-STUDIO/blob/v0.3.0/CHANGELOG.md)
- [发布说明](https://github.com/wsyh4567/DATAVIZ-STUDIO/blob/v0.3.0/RELEASE_NOTES_v0.3.0.md)
- [项目结构](https://github.com/wsyh4567/DATAVIZ-STUDIO/blob/v0.3.0/PROJECT_STRUCTURE.md)
- [快速开始](https://github.com/wsyh4567/DATAVIZ-STUDIO/blob/v0.3.0/QUICKSTART.md)

---

## 🔄 从 v0.2.0 升级

本版本主要是文件结构调整，不涉及 API 变更：

\`\`\`bash
git pull origin main
python app.py
\`\`\`

---

**完整更新内容请查看 [CHANGELOG.md](https://github.com/wsyh4567/DATAVIZ-STUDIO/blob/v0.3.0/CHANGELOG.md)**
```

### 3. 设置 Release 选项

- ✅ 勾选 "Set as the latest release"
- ⬜ 不勾选 "Set as a pre-release"（这是正式版本）
- ⬜ 不勾选 "Create a discussion for this release"（可选）

### 4. 发布

点击 "Publish release" 按钮完成发布。

---

## 发布后的工作

### 1. 验证 Release

访问 Release 页面确认发布成功：
```
https://github.com/wsyh4567/DATAVIZ-STUDIO/releases/tag/v0.3.0
```

### 2. 更新 README Badge（可选）

在 README.md 中添加最新版本徽章：
```markdown
![GitHub release](https://img.shields.io/github/v/release/wsyh4567/DATAVIZ-STUDIO)
```

### 3. 合并到主分支

如果当前在 feature 分支，考虑合并到 main：
```bash
git checkout main
git merge feature/data-workshop-redesign
git push origin main
```

### 4. 通知用户（可选）

- 在项目 Discussions 发布公告
- 更新项目主页说明
- 在社交媒体分享

---

## 下载链接

发布后，用户可以通过以下方式下载：

- **ZIP**: https://github.com/wsyh4567/DATAVIZ-STUDIO/archive/refs/tags/v0.3.0.zip
- **TAR.GZ**: https://github.com/wsyh4567/DATAVIZ-STUDIO/archive/refs/tags/v0.3.0.tar.gz

---

## 常见问题

### Q: 如何删除已发布的 Release？
A: 在 Release 页面点击 "Delete" 按钮，但标签仍会保留。

### Q: 如何修改 Release 说明？
A: 在 Release 页面点击 "Edit release" 按钮。

### Q: 如何删除标签？
A: 
```bash
# 删除本地标签
git tag -d v0.3.0

# 删除远程标签
git push origin :refs/tags/v0.3.0
```

---

**准备就绪！现在可以在 GitHub 上创建 Release 了。**
