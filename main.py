import aiohttp
import argparse
import asyncio
import datetime

URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


class HttpError(Exception):
    pass


async def request(session, url: str):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result
            else:
                raise HttpError(f"Error status: {resp.status} for {url}")
    except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
        raise HttpError(f'Connection error: {url}', str(err))


async def main(shift_days: int, selected_currencies: list) -> list:
    data_list_requests = []
    async with aiohttp.ClientSession() as session:
        for i in range(shift_days):
            previous_date = datetime.datetime.now() - datetime.timedelta(days=i)
            formatted_date = previous_date.strftime("%d.%m.%Y")
            url = URL + formatted_date
            try:
                response = await request(session, url)
                data_list_requests.append(response)
            except HttpError as err:
                print(err)
                return None
        return get_currency_rates(data_list_requests, selected_currencies)


def parser_PB_json(pb_request: list) -> list:
    parsed_PB_data = []
    for data in pb_request:
        date = data["date"]
        currencies = {}
        for item in data["exchangeRate"]:
            if item["currency"] in ["EUR", "USD"]:
                currencies[item["currency"]] = {
                    "sale": item["saleRate"],
                    "purchase": item["purchaseRate"]
                }
        if currencies:
            parsed_PB_data.append({date: currencies})
    return parsed_PB_data


def get_currency_rates(data: list, selected_currencies: list) -> list:
    result = parser_PB_json(data)
    return result[-len(selected_currencies):]


def output_currency_rates(result: list):
    print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Отримати курси EUR та USD ПриватБанку за останні дні.")
    parser.add_argument("days", type=int, help="Кількість днів для запиту курсів (не більше 10)")
    args = parser.parse_args()

    if 0 < args.days <= 10:
        selected_currencies = ["EUR", "USD"]
        result = asyncio.run(main(args.days, selected_currencies))
        output_currency_rates(result)
    else:
        print("Помилка: Кількість днів має бути від 1 до 10.")
