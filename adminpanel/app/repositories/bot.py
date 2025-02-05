import aiohttp


class BotRepository:
    BOT_API_URL = "http://localhost:8002"

    async def trigger_mailing_run(self, mailing_id: int):
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.post(f"/api/mailing/{mailing_id}")
            assert resp.status == 200, await resp.text()

    async def trigger_mailing_test(self, chat_id: int, text: str):
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.post(f"/api/mailing/test", json={"chat_id": chat_id, "text": text})
            assert resp.status == 200, await resp.text()

