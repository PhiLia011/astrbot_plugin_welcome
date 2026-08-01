# astrbot_plugin_welcome
📦 插件名称
astrbot_plugin_welcome

📖 功能简介
新增功能
指令：

/setwelcome [群号] 欢迎语 —— 为指定群设置欢迎语（群号可省略，默认为当前群）

/delwelcome [群号] —— 删除指定群的自定义欢迎语（恢复默认）

/listwelcome —— 列出所有已设置的自定义欢迎语

入群事件：根据当前群号自动查询配置，若有则发送自定义欢迎语，否则使用全局默认 WELCOME_MSG

持久化：所有配置保存在插件目录下的 data/welcome_config.json，修改即时生效，重启后保留

保留原有功能
图片外显文字补丁（_patch_image_to_dict）

退群通知（group_decrease）

测试图片指令（测试图片）

⚙️ 配置选项
所有配置均集中在 main.py 开头的全局变量中，您可以直接用文本编辑器修改：

python
WELCOME_MSG = "四亿史诗，以你成篇！"        # 入群欢迎语（可改）
LEAVE_MSG = "退群了"                       # 退群通知语（可改）
CUSTOM_SUMMARY = "有问题联系主人：1938649156"  # 所有图片的外显文字（可改）
修改后保存文件，重新加载插件即可生效，无需重启整个程序

📂 安装方法（桌面版）
找到数据目录：

Windows：C:\Users\你的用户名\AppData\Roaming\AstrBot\ 或 %USERPROFILE%\.astrobot\

创建插件文件夹：

在数据目录下新建 plugins 文件夹（若没有）

在 plugins 内新建 astrbot_plugin_welcome 文件夹

放入两个文件：

metadata.yaml

main.py

重载插件或重启 AstrBot 桌面版，插件会自动加载

🧪 验证是否成功
启动后，日志（或控制台）会显示：

text
✅ 图片外显文字补丁已应用

🔧 技术实现说明
事件监听：通过重写 Star.on_event 方法，解析 OneBot 协议的 notice 事件，识别 group_increase 和 group_decrease

图片补丁：对 Image.fromFileSystem 和 Image.fromURL 进行猴子补丁，强制写入 summary 字段

兼容性：不依赖外部库（Redis 等），轻量运行

❓ 常见问题
问题	解决方法
插件加载失败（no attribute 'on_notice' 等）	使用最终版的 on_event 方式，已适配多种 AstrBot 版本
入群/退群无响应	检查事件名称是否为 group_increase / group_decrease（OneBot 标准）。如果适配器不同，可修改 raw.get("notice_type") 中的字符串
退群时昵称显示为空	退群时成员已不在群，无法获取名片，因此只显示 QQ 号，这是正常现象
图片外显文字未改变	确保图片是通过 Image.fromFileSystem 或 fromURL 发送的；如果插件内部直接构造字典，则需手动设置 summary
📌 附加说明
本插件无需额外安装依赖（requirements.txt 可为空）

支持 AstrBot ≥ 4.0 版本，理论兼容所有适配器（OneBot、QQ官方等）

如需要入群冷却功能，可参考之前的 Redis 方案，但当前版本已移除以保持轻量
