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
        logger.info("✅ 图片外显文字补丁已应用 (to_dict 添加字段)")

    def _patch_image_to_dict(self):
        """修改 Image.to_dict，在返回的 data 中添加 summary 等字段"""
        original_to_dict = Image.to_dict

        def patched_to_dict(self):
            result = original_to_dict(self)
            # 确保 data 存在
            if 'data' not in result:
                result['data'] = {}
            # 添加多个可能的字段名，提高兼容性
            result['data']['summary'] = CUSTOM_SUMMARY
            result['data']['sub'] = CUSTOM_SUMMARY
            result['data']['title'] = CUSTOM_SUMMARY
            result['data']['desc'] = CUSTOM_SUMMARY
            # 打印日志便于调试（info 级别）
            logger.info(f"📸 图片段序列化后数据: {result}")
            return result

        Image.to_dict = patched_to_dict

    # ---------- 测试指令（可选） ----------
    @filter.command("测试图片")
    async def test_image(self, event: AstrMessageEvent):
        """发送一张测试图片，用于验证外显文字"""
        # 1x1 灰色图片 base64
        img_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        img = Image.fromBase64(img_b64)
        yield event.chain_result([Plain("测试图片："), img])

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
            yield event.chain_result([At(qq=user_id), Plain(" " + WELCOME_MSG)])

        elif notice_type == "group_decrease":
            sender_name = event.get_sender_name()
            msg = f"{sender_name}({user_id}) {LEAVE_MSG}" if sender_name else f"{user_id} {LEAVE_MSG}"
            logger.info(f"🚪 [退出通知] 群 {group_id} {msg}")
            yield event.plain_result(msg)

    async def terminate(self):
        logger.info("🛑 插件已卸载")