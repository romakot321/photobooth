import aiohttp
import os


class BotRepository:
    BOT_API_URL = os.getenv("BOT_API_URL", "http://bot")

    async def trigger_mailing_run(self, mailing_id: int):
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.post(f"/api/mailing/{mailing_id}")
            assert resp.status == 200, await resp.text()

    async def trigger_mailing_test(
            self,
            chat_id: int,
            text: str,
            buttons: list[dict] | None = None,
            image_filename: str | None = None,
            video_filename: str | None = None,
    ):
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.post(
                f"/api/mailing/test",
                json={"chat_id": chat_id, "text": text, "buttons": buttons, "image_filename": image_filename,
                      "video_filename": video_filename}
            )
            assert resp.status == 200, await resp.text()

    async def get_mailing_messages_count(self, mailing_id: int) -> int:
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.get(f"/api/mailing/{mailing_id}/progress")
            assert resp.status == 200, await resp.text()
            return int(await resp.text())

    async def get_mailing_sended_chat_ids(self, mailing_id: int) -> list[int]:
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.get(f"/api/mailing/{mailing_id}/chats")
            assert resp.status == 200, await resp.text()
            return await resp.json()

    async def pause_mailing_sending(self, mailing_id: int, value: bool):
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.post(f"/api/mailing/{mailing_id}/pause?value={value}")
            assert resp.status == 200, await resp.text()

