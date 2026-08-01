import os
import json
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger
from astrbot.api.message_components import Image, At, Plain

WELCOME_MSG = "四亿史诗，以你成篇！"
LEAVE_MSG = "退群了"
CUSTOM_SUMMARY = "有问题联系主人：1938649156"

class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._patch_image_to_dict()
        # 配置数据存储路径：在插件目录下的 data/welcome_config.json
        self.config_dir = os.path.join(os.path.dirname(__file__), "data")
        self.config_file = os.path.join(self.config_dir, "welcome_config.json")
        self._ensure_config_dir()
        # 加载配置
        self.welcome_config = self._load_config()
        logger.info("✅ 图片外显文字补丁已应用，欢迎语配置使用 JSON 文件存储")

    def _ensure_config_dir(self):
        """确保 data 目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def _load_config(self) -> dict:
        """从 JSON 文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载欢迎配置失败: {e}")
                return {}
        return {}

    def _save_config(self):
        """保存配置到 JSON 文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.welcome_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存欢迎配置失败: {e}")

    # ---------- 图片补丁 ----------
    def _patch_image_to_dict(self):
        original_to_dict = Image.to_dict
        def patched_to_dict(self):
            result = original_to_dict(self)
            if 'data' not in result:
                result['data'] = {}
            result['data']['summary'] = CUSTOM_SUMMARY
            result['data']['sub'] = CUSTOM_SUMMARY
            result['data']['title'] = CUSTOM_SUMMARY
            result['data']['desc'] = CUSTOM_SUMMARY
            logger.info(f"📸 图片段序列化后数据: {result}")
            return result
        Image.to_dict = patched_to_dict

    # ---------- 欢迎语配置管理 ----------
    async def get_welcome(self, group_id: int) -> str:
        return self.welcome_config.get(str(group_id), WELCOME_MSG)

    async def set_welcome(self, group_id: int, msg: str):
        self.welcome_config[str(group_id)] = msg
        self._save_config()

    async def del_welcome(self, group_id: int) -> bool:
        if str(group_id) in self.welcome_config:
            del self.welcome_config[str(group_id)]
            self._save_config()
            return True
        return False

    # ---------- 测试指令 ----------
    @filter.command("测试图片")
    async def test_image(self, event: AstrMessageEvent):
        img_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        img = Image.fromBase64(img_b64)
        yield event.chain_result([Plain("测试图片："), img])

    # ---------- 欢迎语管理命令 ----------
    @filter.command("setwelcome")
    async def set_welcome_cmd(self, event: AstrMessageEvent):
        """用法：/setwelcome [群号] 欢迎语（群号可省略，默认为当前群）"""
        text = event.get_plain_text()
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            yield event.plain_result("❌ 用法：/setwelcome [群号] 欢迎语")
            return

        rest = parts[1].strip()
        first_word = rest.split(maxsplit=1)
        if first_word and first_word[0].isdigit():
            group_id = int(first_word[0])
            msg = first_word[1].strip() if len(first_word) > 1 else ""
        else:
            group_id = event.get_group_id()
            msg = rest

        if not msg:
            yield event.plain_result("❌ 欢迎语不能为空")
            return

        # 权限控制（建议开启，需自己实现 _is_admin）
        # if not await self._is_admin(event, group_id):
        #     yield event.plain_result("❌ 只有群管理员或Bot主人可以设置欢迎语")
        #     return

        await self.set_welcome(group_id, msg)
        yield event.plain_result(f"✅ 群 {group_id} 的欢迎语已设置为：{msg}")

    @filter.command("delwelcome")
    async def del_welcome_cmd(self, event: AstrMessageEvent):
        """用法：/delwelcome [群号]（若省略则删除当前群设置）"""
        text = event.get_plain_text()
        parts = text.split(maxsplit=1)
        if len(parts) > 1 and parts[1].strip().isdigit():
            group_id = int(parts[1].strip())
        else:
            group_id = event.get_group_id()

        # if not await self._is_admin(event, group_id):
        #     yield event.plain_result("❌ 权限不足")
        #     return

        if await self.del_welcome(group_id):
            yield event.plain_result(f"✅ 群 {group_id} 的欢迎语已恢复默认")
        else:
            yield event.plain_result(f"ℹ️ 群 {group_id} 未设置自定义欢迎语")

    @filter.command("listwelcome")
    async def list_welcome_cmd(self, event: AstrMessageEvent):
        """列出所有已设置的自定义欢迎语"""
        if not self.welcome_config:
            yield event.plain_result("ℹ️ 当前没有设置任何自定义欢迎语")
            return
        lines = [f"群 {gid}: {msg}" for gid, msg in self.welcome_config.items()]
        yield event.plain_result("📋 当前自定义欢迎语列表：\n" + "\n".join(lines))

    # ---------- 入群/退群通知 ----------
    async def on_event(self, event: AstrMessageEvent):
        raw = event.raw_event
        if raw.get("post_type") != "notice":
            return

        notice_type = raw.get("notice_type")
        group_id = raw.get("group_id")
        user_id = raw.get("user_id")
        self_id = raw.get("self_id")

        if user_id == self_id:
            return

        if notice_type == "group_increase":
            logger.info(f"👋 检测到入群: 群 {group_id}, 用户 {user_id}")
            welcome = await self.get_welcome(group_id)
            yield event.chain_result([At(qq=user_id), Plain(" " + welcome)])

        elif notice_type == "group_decrease":
            sender_name = event.get_sender_name()
            msg = f"{sender_name}({user_id}) {LEAVE_MSG}" if sender_name else f"{user_id} {LEAVE_MSG}"
            logger.info(f"🚪 [退出通知] 群 {group_id} {msg}")
            yield event.plain_result(msg)

    async def terminate(self):
        logger.info("🛑 插件已卸载")