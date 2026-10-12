# 🧠 Claude Code + DeepSeek 安装配置教程

> Windows 环境 · 通过 npm 安装 · 接入 DeepSeek API

---

## 📋 前置要求

| 软件 | 版本要求 | 推荐安装位置 | 说明 |
| --- | --- | --- | --- |
| Git for Windows | 最新版 | `D:\Git`（示例） | 提供 Git Bash 环境，Claude Code 依赖它执行 Shell 命令 |
| Node.js | 18.x 或更高 | `D:\nodejs`（示例） | npm 会随 Node.js 一起安装 |

> 💡 **说明**：本文中的路径使用 `C:\Users\your_user_name\` 作为用户目录占位符，请根据你电脑的实际用户名替换。

> ⌨️ **如何打开 CMD（命令提示符）**：按 `Win + R` → 输入 `cmd` → 回车。教程中所有命令都在 CMD 里执行。每次配置完环境变量后，都要**关闭所有 CMD 窗口重新打开新的**，修改才会生效。

---

## 📦 第一步：安装 Git for Windows（装完立即配置环境变量）

### 1.1 下载与安装

- **下载**：访问 [git-scm.com/downloads/win](https://git-scm.com/downloads/win)，下载 64 位版本。
- **安装**：运行安装程序，关键选项如下：
  - **安装路径**：建议改为非系统盘，如 `D:\Git`
  - **选择编辑器**：建议改为 Visual Studio Code（避免卡在 Vim 里）
  - **调整 PATH**：务必选择 “Git from the command line and also from 3rd-party software”
  - **换行符**：选择 “Checkout Windows-style, commit Unix-style line endings”
  - **默认分支名**：选择 “Override the default branch name for new repositories”，填写 `main`

### 1.2 打开环境变量编辑界面

先学会打开 “环境变量” 窗口，后面所有 PATH 配置都在这里操作。

1. 按 `Win + I` 打开 Windows 设置；
2. 在顶部搜索框输入 “环境变量”，会看到两个搜索结果；
3. 根据你的用户权限选择其一：
   - **普通账户（无管理员权限）**：点击 “编辑账户的环境变量”，直接进入当前用户的变量编辑窗口；
   - **管理员账户**：点击 “编辑系统环境变量”，再在弹出窗口点击右下角 “环境变量” 按钮。

> 📍 **打开后认准位置**：窗口分上下两个框。上面是 “用户变量”（只对当前用户生效，教程全部操作都在这里），下面是 “系统变量”（对所有用户生效，需要管理员权限）。找到 `Path` → 选中 → 点击 “编辑” → 点击 “新建” → 粘贴路径 → 逐个点 “确定” 关闭窗口。

### 1.3 注入 Git / Git Bash 到 PATH

> 💡 **先确认你的 Git 装在哪**：教程以 `D:\Git` 为例。如果你装到了别的位置，打开文件管理器进入 Git 安装目录，确认里面能看到 `bin` 和 `cmd` 两个子文件夹，下面要填的路径就换成你的实际安装目录。

> 💡 **实测结论（安装器自动 vs 手动补）**：若安装时选择了 “Git from the command line and also from 3rd-party software”，安装器会自动把 `D:\Git\cmd`（git 命令）加入**系统变量**，这部分不用管；而 `D:\Git\bin`（Git Bash 的 bash 命令）不会自动加，需要手动补到**用户变量**。所以下面的手动操作重点是加 `bin` 这一条。

**手动操作（图形界面方式）：**

1. 按 **1.2 节** 打开环境变量编辑界面。
2. 在 “用户变量” 区域找到 `Path` → 选中 → 点击 “编辑”。
3. 点击 “新建”，粘贴 Git Bash 的路径（按你的实际安装路径调整）：

   ```text
   D:\Git\bin    <-- 注入 Git Bash（bash.exe、sh.exe、grep、sed 等 Unix 工具）
   ```

4. 逐个点 “确定” 关闭所有窗口。
5. 进入 1.4 验证。若 `where git` 没有输出，再返回本节，把下面这条也加入用户变量 `Path`（按你的实际安装路径调整）：

   ```text
   D:\Git\cmd    <-- 注入 git.exe（备用：通常安装器已自动加入系统变量，一般不需要）
   ```

### 1.4 验证

关闭所有 CMD 窗口，重新打开一个新的，执行：

```cmd
C:\Users\your_user_name> where git     # 应显示 D:\Git\cmd\git.exe
C:\Users\your_user_name> where bash     # 应显示 D:\Git\bin\bash.exe
```

两条都找到路径后，再执行版本检查：

```cmd
C:\Users\your_user_name> git --version    # 应显示 git version 2.xx.x.windows.1
C:\Users\your_user_name> bash --version    # 应显示 GNU bash, version 5.x.x
```

全部通过后再进入第二步 ✅（若 `bash` 报 “不是内部或外部命令”，返回 1.3 确认已加 `D:\Git\bin`；若 `git` 找不到，返回 1.3 第 5 步补 `D:\Git\cmd`）

---

## 📦 第二步：安装 Node.js（装完立即配置环境变量）

### 2.1 下载与安装

- **下载**：访问 [nodejs.org](https://nodejs.org)，下载 LTS 版本。
- **安装**：
  - **安装路径**：建议改为 `D:\nodejs`（示例）
  - 其他选项保持默认即可。

### 2.2 注入 Node.js / npm 到 PATH

> 💡 **实测结论**：Node.js 安装器默认勾选 “Add to PATH”，会自动把 `D:\nodejs` 加入**系统变量**，这一步通常不用手动操作。先按 2.3 验证，`node`/`npm` 命令找不到再手动补。

**手动补 PATH（验证失败才需要）**：按 **1.2 节** 打开环境变量编辑界面，在 “用户变量” 的 `Path` 编辑窗口中点击 “新建” 并粘贴（按你的实际安装路径调整）：

```text
D:\nodejs    <-- 注入 node.exe 和 npm.cmd（npm 就位于 Node.js 安装目录，不用单独加）
```

### 2.3 验证 node 和 npm

关闭所有 CMD 窗口，重新打开一个新的，执行：

```cmd
C:\Users\your_user_name> where node    # 应显示 D:\nodejs\node.exe
C:\Users\your_user_name> where npm      # 应显示 D:\nodejs\npm.cmd（或 D:\nodejs\npm）
```

找到路径后，执行版本检查：

```cmd
C:\Users\your_user_name> node --version    # 应显示 v18.x.x 或更高
C:\Users\your_user_name> npm --version      # 应显示 9.x.x 或更高
```

全部通过后进入 2.4 ✅（报 “不是内部或外部命令” 则返回 2.2 补 PATH）

### 2.4 配置 npm 全局包路径到 D 盘（推荐）

将 npm 全局包安装路径从 C 盘迁移到 D 盘，节省 C 盘空间。配置完成后需把新路径也注入 PATH，否则后面装好的 `claude` 命令找不到。

1. **创建文件夹**：在 `D:\nodejs` 下新建 `node_global` 文件夹。
2. **修改 npm 配置**：

   ```cmd
   C:\Users\your_user_name> npm config set prefix "D:\nodejs\node_global"
   ```

3. **验证配置**：

   ```cmd
   C:\Users\your_user_name> npm config get prefix    # 应返回 D:\nodejs\node_global
   ```

4. **注入 node_global 到 PATH（关键手动步骤）**：按 **1.2 节** 打开环境变量编辑界面，在 “用户变量” 的 `Path` 编辑窗口中点击 “新建” 并粘贴：

   ```text
   D:\nodejs\node_global    <-- 注入 claude 等全局 npm 包命令
   ```

> 📌 **为什么这条必须手动加**：npm 官方默认的全局路径是 `C:\Users\your_user_name\AppData\Roaming\npm`（安装 Node 时已自动在 PATH 里）。当你把 prefix 改到 `D:\nodejs\node_global` 后，npm 不会再往默认路径装包，而新路径不会自动进 PATH，所以必须手动注入，否则 `claude` 装完会报 “不是内部或外部命令”。原默认路径建议保留，`npx` 等工具仍会参考它。

### 2.5 验证 npm 全局路径配置

关闭所有 CMD 窗口，重新打开一个新的，执行：

```cmd
C:\Users\your_user_name> npm config get prefix    # 应返回 D:\nodejs\node_global
C:\Users\your_user_name> echo %PATH%              # 输出中应能看到 D:\nodejs\node_global（确认第 4 步的 PATH 注入已生效）
```

两项都确认后进入第三步 ✅

---

## ⚙️ 第三步：环境变量总检查与汇总

> ⚠️ 进入下一步前，确认终端能找到 `git`、`bash`、`node`、`npm`，以及（2.4 配置后的）全局 npm 包目录 `node_global`。

### 3.1 Path 应包含的条目汇总

此时 PATH 中应包含以下条目（实测验证过的真实情况：安装器会自动加进系统变量的有 `D:\Git\cmd` 和 `D:\nodejs`；需要你手动加进用户变量的是 `D:\Git\bin` 和 `D:\nodejs\node_global`）：

| 路径 | 作用 | 所在位置 | 如何配置 |
| --- | --- | --- | --- |
| `D:\Git\bin` | 让 bash 命令生效（Git Bash） | 用户变量 | 1.3 节手动加（安装器不会自动加这条） |
| `D:\Git\cmd` | 让 git 命令生效 | 系统变量 | 安装器自动加入；找不到时按 1.3 节手动补 |
| `D:\nodejs` | 让 node 和 npm 命令生效 | 系统变量 | 安装器自动加入；找不到时按 2.2 节手动补 |
| `D:\nodejs\node_global` | 让 claude 等全局 npm 包命令生效 | 用户变量 | 2.4 节手动加（关键步骤） |
| `C:\Users\your_user_name\AppData\Roaming\npm` | npm 默认全局路径，供 npx 等工具参考 | 用户变量 | 安装 Node 时自动加入，保留勿删 |

### 3.2 总检查

关闭所有 CMD 窗口，重新打开一个新的，依次执行：

```cmd
C:\Users\your_user_name> where git     # 应显示 D:\Git\cmd\git.exe
C:\Users\your_user_name> where bash     # 应显示 D:\Git\bin\bash.exe
C:\Users\your_user_name> where node     # 应显示 D:\nodejs\node.exe
C:\Users\your_user_name> where npm      # 应显示 D:\nodejs\npm.cmd（或 D:\nodejs\npm）
```

全部能找到路径，说明环境变量配置成功 ✅ 可以进入第四步安装 Claude Code。

---

## 🚀 第四步：安装 Claude Code

### 4.1 配置 npm 镜像源（加速下载）

默认官方源速度较慢，建议切换到国内镜像：

```cmd
C:\Users\your_user_name> npm config set registry https://registry.npmmirror.com
```

验证：

```cmd
C:\Users\your_user_name> npm config get registry    # 应返回 https://registry.npmmirror.com/
```

### 4.2 执行安装

在 CMD 中执行：

```cmd
C:\Users\your_user_name> npm install -g @anthropic-ai/claude-code
```

> ⚠️ **如果遇到 EPERM 权限错误：**
> 1. 确认 `D:\nodejs\node_global` 文件夹已创建。
> 2. 右键该文件夹 → 属性 → 安全 → 编辑 → 给当前用户勾选 “完全控制”。
> 3. 关闭所有 CMD 窗口，重新打开一个新的，再次执行安装。

### 4.3 验证安装

```cmd
C:\Users\your_user_name> claude --version    # 应显示版本号，如 2.1.214
```

如果显示版本号，说明安装成功 🎉

---

## 🔧 第五步：配置 DeepSeek API

Claude Code 默认使用 Anthropic 官方 API，需要通过 `settings.json` 切换到 DeepSeek。

**配置文件位置**

```text
C:\Users\your_user_name\.claude\settings.json
```

**创建并写入文件（跟着做）**

1. 打开 CMD，先创建 `.claude` 文件夹：

   ```cmd
   C:\Users\your_user_name> mkdir %USERPROFILE%\.claude
   ```

2. 用记事本打开（若文件不存在，记事本会提示新建，点 “是”）：

   ```cmd
   C:\Users\your_user_name> notepad %USERPROFILE%\.claude\settings.json
   ```

3. 把下面这段内容完整粘贴进去（把 API Key 换成你自己的）：

   ```json
   {
     "env": {
       "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
       "ANTHROPIC_AUTH_TOKEN": "sk-你的 DeepSeek API Key",
       "ANTHROPIC_MODEL": "deepseek-v4-pro[1m]",
       "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro[1m]",
       "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro[1m]",
       "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash[1m]",
       "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash[1m]",
       "CLAUDE_CODE_EFFORT_LEVEL": "max",
       "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
     }
   }
   ```

> 🔑 **获取 API Key**：访问 DeepSeek 平台 注册/登录后，在 API Keys 页面创建并复制你的 Key，替换上面代码中的 `sk-你的 DeepSeek API Key`。

> ⚠️ **注意：**
> - 如果 DeepSeek v4 Flash 不支持 1M 上下文，请去掉 `[1m]`，保留 `deepseek-v4-flash`。
> - 粘贴后，在记事本按 `Ctrl + S` 保存并关闭窗口。
> - 保存文件后，关闭所有 CMD 窗口重新打开新的，使配置生效。

### 🔓 可选：跳过 Anthropic 登录验证

某些版本首次运行 `claude` 时，会弹出浏览器 OAuth 登录验证。如果遇到，可以创建下面的配置文件来跳过。

**文件位置**

```text
C:\Users\your_user_name\.claude.json
```

**创建并写入**

在 CMD 中执行（若文件不存在，记事本会提示新建，点 “是”），把内容粘贴进去后 `Ctrl + S` 保存：

```cmd
C:\Users\your_user_name> notepad %USERPROFILE%\.claude.json
```

```json
{
  "hasCompletedOnboarding": true
}
```

> 💡 **说明**：这个步骤是**可选的**。如果你通过 `settings.json` 配置了 `ANTHROPIC_AUTH_TOKEN`，Claude Code 会直接使用 API Key 鉴权，通常不会弹出登录提示，因此这个文件不是必需的。若第六步遇到登录验证，再回来补这个文件。

---

## ✅ 第六步：验证完整配置

在 CMD 中输入：

```cmd
C:\Users\your_user_name> claude
```

✅ 如果进入 Claude Code 对话界面（出现 `>` 提示符或欢迎信息），说明全部配置成功！

---

## 🐛 常见问题

### Q1：安装时提示 `EPERM: operation not permitted`

- **原因**：npm 无权限写入 `node_global` 文件夹。
- **解决**：右键 `D:\nodejs\node_global` → 属性 → 安全 → 编辑 → 给当前用户勾选 “完全控制” → 确定。关闭所有 CMD 窗口重新打开后重试。

### Q2：安装完成后 `claude` 提示 “不是内部或外部命令”

- **原因**：`D:\nodejs\node_global` 未加入用户变量 `Path` 环境变量。
- **解决**：按 2.4 节第 4 步将该路径添加到用户变量 `Path` 中，重启 CMD。

### Q3：npm 安装速度非常慢

- **解决**：切换镜像源：

  ```cmd
  C:\Users\your_user_name> npm config set registry https://registry.npmmirror.com
  ```

### Q4：bash 命令找不到

- **原因**：`D:\Git\bin` 未加入环境变量，或安装 Git 时未勾选 “Git from the command line and also from 3rd-party software”。
- **解决**：按 1.3 节将 `D:\Git\bin` 添加到用户变量 `Path` 中，重启 CMD。

### Q5：配置文件 `settings.json` 不生效

- **检查**：
  - 文件路径是否为 `C:\Users\your_user_name\.claude\settings.json`
  - JSON 格式是否有效（可用 JSON 验证器检查）
  - 修改后是否**重启了终端**

---

## 📁 最终文件结构

```text
D:\
├── Git\
│   ├── bin\bash.exe
│   └── cmd\git.exe
├── nodejs\
│   ├── node.exe
│   ├── npm.cmd
│   └── node_global\          ← npm 全局包安装目录
│       ├── claude.cmd
│       └── node_modules\@anthropic-ai\claude-code\
└── ...

C:\Users\your_user_name\
├── .claude\
│   └── settings.json         ← DeepSeek 配置
├── .claude.json              ← 可选：跳过登录验证
├── AppData\Roaming\npm\      ← 保留，用于 npx 等
└── ...
```

---

## 🎯 总结

| 步骤 | 状态 |
| --- | --- |
| 安装 Git for Windows + 注入 Git Bash 到 PATH | ✅ 完成 |
| 安装 Node.js + 注入 node/npm 到 PATH | ✅ 完成 |
| 配置 npm 全局路径到 D 盘 + 注入 node_global 到 PATH | ✅ 完成 |
| 环境变量总检查（第三步） | ✅ 完成 |
| 安装 Claude Code | ✅ 完成 |
| 配置 DeepSeek API | ✅ 完成 |

> 🚀 现在，在终端中输入 `claude` 开始使用吧！

---

*文档生成日期：2026-07-18 · 适用于 Windows 环境*
