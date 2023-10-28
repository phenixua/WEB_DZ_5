import aiohttp
import asyncio
import platform
from datetime import datetime, timedelta

URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


# Власна помилка для обробки HTTP-помилок
class HttpError(Exception):
    pass


# Асинхронна функція для виконання HTTP-запитів
async def request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                raise HttpError(f"Error status: {response.status} for {url}")


# Головна асинхронна функція
async def main(index_day):
    data_list_requests = []
    for i in range(index_day):
        # Обчислюємо дату на `i` днів назад від поточної дати
        d = datetime.now() - timedelta(days=i)
        # Форматуємо дату у відповідний рядок
        formatted_date = d.strftime("%d.%m.%Y")
        try:
            # Виконуємо HTTP-запит для отримання курсів на вказану дату
            response = await request(f'{URL}{formatted_date}')
            data_list_requests.append(response)
        except HttpError as err:
            # Обробляємо помилку та виводимо її на екран
            print(err)
            return None
        # Робимо паузу на 1 секунду між запитами
        await asyncio.sleep(1)
    # Повертаємо сформовані дані про курси валют
    return format_currency_data(data_list_requests)


# Функція для форматування отриманих даних
def format_currency_data(data_list):
    formatted_data = []
    for data in data_list:
        date = data["date"]
        currencies = {}
        for item in data["exchangeRate"]:
            currency = item["currency"]
            if currency in ["EUR", "USD"]:
                sale_rate = item["saleRate"]
                purchase_rate = item["purchaseRate"]
                currencies[currency] = {"sale": sale_rate, "purchase": purchase_rate}
        if currencies:
            formatted_data.append({date: currencies})
    return formatted_data


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Очікуємо введення кількості днів для запиту курсів
    selected_days = int(input("Введіть кількість днів для запиту курсів (не більше 10): "))

    if 0 < selected_days <= 10:
        # Викликаємо головну асинхронну функцію і виводимо результат
        currency_rates = asyncio.run(main(selected_days))
        print(currency_rates)
    else:
        print("Помилка: Кількість днів має бути від 1 до 10.")
