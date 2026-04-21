\# 🛡️ Campus-NetKeeper V2 (校园网守护神 通用版)



!\[License](https://img.shields.io/badge/License-MIT-blue.svg)

!\[Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)

!\[Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)



一款基于 Python 开发的跨平台、通用型校园网/企业网 Web Portal 自动认证与掉线重连工具。摒弃了传统的硬编码密码模式，通过底层的自动化流量嗅探技术，实现真正的“一键适配、无感守护”。



\## ✨ 核心特性 (Features)



\* \*\*🌐 通用环境嗅探 (Universal Sniffing)\*\*：内置 Playwright 自动化引擎，一键呼出纯净浏览器。无论学校使用哪家网络厂商的计费系统，程序都能自动劫持并提取底层的 POST 登录负载（Payload）与请求头，生成专属的 `config.json`。

\* \*\*⚡ 毫秒级断网重连 (Silent Guardian)\*\*：基于 Requests 与多线程技术，后台以极低的网络开销轮询微软连通性测试接口。一旦察觉网络波动或强制掉线，瞬间重放抓取到的登录包，实现“掉线秒连”。

\* \*\*🖥️ 极简可视化交互 (Clean GUI)\*\*：采用 PyQt5 构建现代化图形界面，剥离繁琐配置。支持系统托盘后台运行，双击唤出，不干扰日常桌面办公与游戏体验。

\* \*\*🔒 隐私与安全 (Privacy First)\*\*：密码及配置数据仅保存在本地同目录的 `config.json` 中，不上传任何云端，配置随删随走，干净无残留。



\## 🚀 快速上手 (Quick Start)



\### 1. 运行前准备

下载最新的 Release 压缩包并解压，双击运行 `Campus-NetKeeper.exe`。

\*(首次运行界面状态提示为“待机中”，需要先获取配置)\*



\### 2. 一键抓取配置

1\. 点击界面的 \*\*“🔍 1. 一键打开浏览器获取登录配置”\*\* 按钮。

2\. 程序会唤起系统自带的 Edge 浏览器并自动跳转至网络认证页。

3\. 在弹出的浏览器中，手动输入您的账号密码并完成\*\*登录\*\*。

4\. \*\*登录成功后，直接关闭该浏览器窗口！\*\*

5\. 界面日志提示“✅ 抓包大成功！”，此时同目录下已自动生成 `config.json` 配置文件。



\### 3. 启动后台守护

点击界面的 \*\*“▶️ 2. 启动后台网络守护”\*\*。你可以点击右上角的“X”将主界面隐藏至右下角系统托盘。守护神已就绪，再也不用担心打游戏或挂机下载时突然断网了！



\## 🛠️ 开发者构建指南 (Build Instructions)



如果您想从源码运行或自行打包，请确保您的环境中已安装 Python 3.8+，并执行以下命令：



```bash

\# 1. 安装核心依赖库

pip install PyQt5 requests playwright



\# 2. 从国内源安装 Playwright 并忽略内核下载（本项目调用本地 Edge）

pip install playwright -i \[https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)



\# 3. 使用 PyInstaller 打包为单文件 EXE (需自备 tubiao.ico 图标)

python -m PyInstaller -F -w -i tubiao.ico --add-data "tubiao.ico;." xywshs.py

⚠️ 免责声明 (Disclaimer)

本项目仅供 Python 自动化学习、网络协议分析及技术交流使用。请勿将本工具用于任何高频恶意请求、内网穿透攻击或其他违反学校/企业网络安全服务条款的行为。

因使用者滥用本工具造成的网络账号封禁或其它一切法律与纪律后果，由使用者自行承担，与本项目及开发者无关。

Author    luminesunc



