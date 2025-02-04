import aiohttp


class BotRepository:
    BOT_API_URL = "http://bot"

    async def trigger_mailing_run(self, mailing_id: int):
        async with aiohttp.ClientSession(base_url=self.BOT_API_URL) as session:
            resp = await session.post(f"/api/mailing/{mailing_id}")
            assert resp.status == 200, await resp.text()

