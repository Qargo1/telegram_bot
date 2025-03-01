import requests
from lxml import etree
from datetime import date


# Пользовательское исключение
class APIException(Exception):
    pass


# Класс для работы с курсами валют
class CurrencyValue:
    def __init__(self):
        self.today = date.today().strftime('%d/%m/%Y')
        self.url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={self.today}"
        self.data = self.load_currency_data()
        
        # Добавляем рубль ТОЛЬКО если его нет в списке
        if not any(item['name'].lower() in ['рубль', 'российский рубль', 'rur', 'rub'] for item in self.data):
            self.data.append({
                'name': 'Российский рубль',
                'nominal': '1',
                'value': '1.00'
            })
            
        print("\n\n", self.data, "\n\n")
        

    def load_currency_data(self):
        response = requests.get(self.url)
        response.encoding = 'windows-1251'
        tree = etree.fromstring(response.content)
        data = []
        for item in tree.xpath('//Valute'):
            data.append({
                'name': item.xpath('./Name/text()')[0],
                'nominal': item.xpath('./Nominal/text()')[0],
                'value': item.xpath('./Value/text()')[0]
            })
        return data

    def safe_float(self, value):
        try:
            return float(str(value).replace(',', '.'))
        except ValueError:
            raise APIException(f"Неверный числовой формат: {value}")

    def get_currency_rate(self, currency_name):
        # Нормализация названия валюты
        normalized_name = currency_name.lower().replace('российский ', '')
        
        # Обработка рубля
        if normalized_name in ['рубль', 'рur', 'rub']:
            return {
                'nominal': 1.0,
                'value': 1.0
            }
        
        # Поиск валюты в данных ЦБ
        for item in self.data:
            if item['name'].lower().replace('российский ', '') == normalized_name:
                return {
                    'nominal': self.safe_float(item['nominal']),
                    'value': self.safe_float(item['value'])
                }
        
        raise APIException(f"Валюта '{currency_name}' не найдена в списке доступных")

    def convert_currency(self, base_currency, target_currency, amount):
        # Если конвертируем рубль в другую валюту
        if base_currency.lower() in ['рубль', 'российский рубль', 'rur', 'rub']:
            target_rate = self.get_currency_rate(target_currency)
            return round(amount / target_rate['value'] * target_rate['nominal'], 2)
        
        # Если конвертируем другую валюту в рубль
        elif target_currency.lower() in ['рубль', 'российский рубль', 'rur', 'rub']:
            base_rate = self.get_currency_rate(base_currency)
            return round(amount * base_rate['value'] / base_rate['nominal'], 2)
        
        # Конвертация между другими валютами
        else:
            base_rate = self.get_currency_rate(base_currency)
            target_rate = self.get_currency_rate(target_currency)
            return round(
                (amount * base_rate['value'] / base_rate['nominal']) 
                / (target_rate['value'] / target_rate['nominal']), 
                2
            )

    def get_currency_list(self):
        # Добавляем рубль в список доступных валют
        currencies = [item['name'] for item in self.data]
        return ', '.join(currencies)