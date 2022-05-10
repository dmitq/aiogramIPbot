from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from requests import get, exceptions
from folium import Map
from os import remove

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def say_hello(message: types.Message):
    await message.answer("Здравствуйте! Отправьте IP-адрес вида <b>214.145.148.31</b>, чтобы получить по нему <i>информацию</i>.", parse_mode=types.ParseMode.HTML)
@dp.message_handler()
async def get_info(message: types.Message):
    try:
        r = get(url=f'http://ip-api.com/json/{message.text}').json()
        lat = r.get('lat')
        lon = r.get('lon')
        mes = f"[IP]: {r.get('query')}\n[Страна]: {r.get('country')}\n[Регион]: {r.get('region')}\n[Город]: {r.get('city')}\n[Широта]: {lat}\n[Долгота]:{lon}\n[Провайдер]: {r.get('isp')}"
        await message.answer(mes)
        await bot.send_location(message.from_user.id, lat, lon)

        map = Map(location=[lat, lon])
        filename_html = f'{r.get("query")}_map.html'
        map.save(filename_html)
        await bot.send_document(message.from_user.id, open(filename_html, 'rb'))

        filename_txt = f'{r.get("query")}_info.txt'
        with open(f'{filename_txt}', "w+") as f:
            for key, item in r.items():
                f.write("{}: {}".format(key, item) + '\n')
        await bot.send_document(message.from_user.id, open(filename_txt, 'rb'))

        remove(filename_html)
        remove(filename_txt)

    except exceptions.ConnectionError:
        await message.answer('Не удалось подключиться')


executor.start_polling(dp)