import httpx
import asyncio
import platform
from datetime import datetime, timedelta

URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")


async def main(index_day):
    data_list_requests = []
    for i in range(index_day):
        d = datetime.now() - timedelta(days=i)
        formatted_date = d.strftime("%d.%m.%Y")
        try:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={formatted_date}')
            data_list_requests.append(response)
        except HttpError as err:
            print(err)
            return None
        await asyncio.sleep(1)  # Затримка 1 секунда між запитами.
    return data_list_requests


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    selected_days = int(input("Введіть кількість днів для запиту курсів (не більше 10): "))

    if 0 < selected_days <= 10:
        currency_rates = asyncio.run(main(selected_days))
        print(currency_rates)
    else:
        print("Помилка: Кількість днів має бути від 1 до 10.")
