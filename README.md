# astrbot_plugin_welcome
📦 插件名称
astrbot_plugin_welcome

📖 功能简介
这是一个为 AstrBot（桌面版/源码版） 设计的增强插件，专为 QQ 群聊（通过 llbot 适配器）提供三个核心功能：

👋 入群欢迎：当有新成员加入群聊时，自动 @ 该成员并发送自定义欢迎语。

🚪 退群通知：当有成员退出群聊时，机器人发送通知（显示昵称和 QQ 号）。

🖼️ 图片外显文字自定义：自动为机器人发送的所有图片消息（如群管、点歌等插件生成的图片）强制添加一段指定的“外显文字”（摘要），显示在图片下方。

⚙️ 配置选项
所有配置均集中在 main.py 开头的全局变量中，您可以直接用文本编辑器修改：

python
WELCOME_MSG = "四亿史诗，以你成篇！"        # 入群欢迎语（可改）
LEAVE_MSG = "退群了"                       # 退群通知语（可改）
CUSTOM_SUMMARY = "有问题联系主人：1938649156"  # 所有图片的外显文字（可改）
修改后保存文件，重新加载插件即可生效，无需重启整个程序。

📂 安装方法（桌面版）
找到数据目录：

Windows：C:\Users\你的用户名\AppData\Roaming\AstrBot\ 或 %USERPROFILE%\.astrobot\

创建插件文件夹：

在数据目录下新建 plugins 文件夹（若没有）。

在 plugins 内新建 astrbot_plugin_welcome 文件夹。

放入两个文件：

metadata.yaml（元数据）

main.py（插件主代码，使用上面提供的最终版）

重启 AstrBot 桌面版（完全退出再打开），插件会自动加载。

🧪 验证是否成功
启动后，日志（或控制台）会显示：

text
✅ 图片外显文字补丁已应用
测试入群：用另一个 QQ 号加群，机器人会 @ 你并发送欢迎语。

测试退群：让群内某成员退群，机器人会发送通知。

测试图片外显文字：让机器人发送一张图片（例如输入“图”指令），查看图片消息下方的文字是否为“有问题联系主人：1938649156”。

🔧 技术实现说明
事件监听：通过重写 Star.on_event 方法，解析 OneBot 协议的 notice 事件，识别 group_increase 和 group_decrease。

图片补丁：对 Image.fromFileSystem 和 Image.fromURL 进行猴子补丁，强制写入 summary 字段。

兼容性：不依赖外部库（Redis 等），轻量运行。

❓ 常见问题
问题	解决方法
插件加载失败（no attribute 'on_notice' 等）	使用最终版的 on_event 方式，已适配多种 AstrBot 版本。
入群/退群无响应	检查事件名称是否为 group_increase / group_decrease（OneBot 标准）。如果适配器不同，可修改 raw.get("notice_type") 中的字符串。
退群时昵称显示为空	退群时成员已不在群，无法获取名片，因此只显示 QQ 号，这是正常现象。
图片外显文字未改变	确保图片是通过 Image.fromFileSystem 或 fromURL 发送的；如果插件内部直接构造字典，则需手动设置 summary。
📌 附加说明
本插件无需额外安装依赖（requirements.txt 可为空）。

支持 AstrBot ≥ 4.0 版本，理论兼容所有适配器（OneBot、QQ官方等）。

如需要入群冷却功能，可参考之前的 Redis 方案，但当前版本已移除以保持轻量。
