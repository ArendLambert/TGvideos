import asyncio
from aiogram import Bot, Dispatcher
from utils.config import TOKEN
from handlers import commands, admin


async def start_main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(commands.router, admin.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start_main())

