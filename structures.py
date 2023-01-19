"""
Модуль со структурными классами Transaq XML Коннектора.
Всем основным xml структурам сопоставлены питоновые объекты.
<a href="http://www.finam.ru/howtotrade/tconnector/">
Документация коннектора</a>

@author: Roma
"""
import sys
import inspect
import logging
from eulxml.xmlmap import parseString, XmlObject, load_xmlobject_from_string, \
    StringField, FloatField, DateTimeField, IntegerField, SimpleBooleanField, \
    NodeListField, ItemField, IntegerListField, NodeField
from eulxml.xmlmap.fields import Field, DateTimeMapper

LOG = logging.getLogger("transaq.connector")

# Формат дат/времени используемый Транзаком
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
# Список классов, ленивая инициализация при парсинге
_MY_CLASSES = []


def parse(xml):
    """
    Общая функция парсинга xml-структур.

    :param xml:
        Текст XML.
    :return:
        Распарсенный объект. None если не распознан.
    """
    # Корневой тег достанем
    root = parseString(xml).tag
    # Пройдемся по всем классам модуля и найдем подходящий
    for cls in _MY_CLASSES:
        if root == cls.ROOT_NAME:
            return cls.parse(xml)
    # Лабуда какая-то пришла
    LOG.error(f"Unsupported XML:\n{xml}")
    return None


# Вспомогательные классы

class NullableDateTimeMapper(DateTimeMapper):
    """
    Оберточный класс вокруг DateTimeMapper,
    возвращающий None для заданных значений,
    а не вываливающий исключение при обработке даты.
    """
    nones = ['0']

    def to_python(self, node):
        if node is None:
            return None
        if isinstance(node, (str, bytes)):
            rep = node
        else:
            rep = self.XPATH(node)
        if rep in self.nones:
            return None

        return super(NullableDateTimeMapper, self).to_python(node)


class MyXmlObject(XmlObject):
    """
    Расширение eulxml.XmlObject с методом само-парсинга
    и наглядным представлением.
    """

    @classmethod
    def parse(cls, xml):
        """Запуск парсера из XML"""
        return load_xmlobject_from_string(xml, cls)

    def __repr__(self):
        cls = self.__class__
        fields = []
        for (name, val) in inspect.getmembers(cls):
            if isinstance(val, Field):
                val = self.__getattribute__(name)
                if val:
                    fields.append("%s=%s" % (name, val))
        return "%s(%s)" % (cls.__name__, ', '.join(fields))


class Entity(MyXmlObject):
    """
    Абстрактный класс сущностей, имеет идентификатор.
    """
    # Entity id, unique in the same class
    id = IntegerField('@id')

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.id == other.id


class Packet(MyXmlObject):
    """
    Абстрактный пакет сущностей присланный серваком.
    """
    items = []


class Error(MyXmlObject):
    """
    Ошибка.
    """
    ROOT_NAME = 'error'
    text = StringField('text()')


class ConnectorVersion(MyXmlObject):
    """
    Номер версии коннектора.
    """
    ROOT_NAME = 'connector_version'
    version = StringField('text()')


class CmdResult(MyXmlObject):
    """
    Результат отправки команды (но не исполнения на серваке).
    """
    ROOT_NAME = 'result'
    success = SimpleBooleanField('@success', 'true', 'false')
    text = StringField('message')
    id = IntegerField('@transactionid')


class TimeDiffResult(MyXmlObject):
    """
    Результат запроса разницы локального времени и времени сервера.
    """
    ROOT_NAME = 'result'
    success = SimpleBooleanField('@success', 'true', 'false')
    diff = IntegerField('@diff')


# Классы xml структур Транзака

class HistoryCandle(Entity):
    """
    Свечки OHLCV (open,high,low,close).
    """
    ROOT_NAME = 'candle'
    date = DateTimeField('@date', TIME_FORMAT)
    id = hash(date)
    open = FloatField('@open')
    high = FloatField('@high')
    low = FloatField('@low')
    close = FloatField('@close')
    volume = IntegerField('@volume')
    # только ФОРТС
    open_interest = IntegerField('@oi')


class HistoryCandlePacket(Packet):
    """
    Пакет свечек |||.
    """
    ROOT_NAME = 'candles'
    # Идентификатор бумаги (постоянный внутри сессии)
    secid = IntegerField('@secid')
    # Борда (режим торгов)
    board = StringField('@board')
    # Тикер бумаги (постоянный)
    seccode = StringField('@seccode')
    # Параметр "status" показывает, осталась ли еще история
    # 0 - данных больше нет (дочерпали до дна)
    # 1 - заказанное количество выдано (если надо еще - делать еще запрос)
    # 2 - продолжение следует (будет еще порция)
    # 3 - требуемые данные недоступны (есть смысл попробовать запросить позже).s
    status = IntegerField('@status')
    period = IntegerField('@period')
    items = NodeListField('candle', HistoryCandle)


class ServerStatus(Entity):
    """
    Состояние соединения.
    """
    ROOT_NAME = 'server_status'
    connected = StringField('@connected', choices=('true', 'false', 'error'))
    timezone = StringField('@server_tz')
    # Атрибут recover – необязательный параметр. Его наличие означает, что
    # коннектор пытается восстановить потерянное соединение с сервером
    recover = SimpleBooleanField('@recover', 'true', None)
    sys_ver = IntegerField('@sys_ver')
    build = IntegerField('@build')
    text = StringField('text()')

    def __repr__(self):
        if self.connected != 'error':
            return "ServerStatus(id=%d,tz=%s,conn=%s)" % \
                   (self.id, self.timezone, self.connected)
        else:
            return "ServerStatus(ERROR, text=%s)" % self.text


class Union(Entity):
    """
    Единый Портфель (юнион).
    """
    ROOT_NAME = "union"
    id = StringField('@id')
    active = SimpleBooleanField('@remove', 'false', 'true')


class UnitedEquity(Entity):
    """
    Актуальная оценка ликвидационной стоимости Единого портфеля.
    """
    ROOT_NAME = "united_equity"
    id = StringField('@union')
    # Текущая оценка стоимости единого портфеля
    equity = FloatField('equity')


class UnitedGo(Entity):
    """
    Размер средств, заблокированных биржей (FORTS) под
    срочные позиции клиентов юниона
    """
    ROOT_NAME = "united_go"
    id = StringField('@union')
    # Размер требуемого ГО, посчитанный биржей FORTS
    go = FloatField('go')


class ClientAccount(Entity):
    """
    Данные клиентсткого аккаунта.
    """
    ROOT_NAME = 'client'
    id = StringField('@id')
    active = SimpleBooleanField('@remove', 'false', 'true')
    # Возможные типы клиента: spot (кассовый),
    # leverage (плечевой), margin_level (маржинальный),
    # mct (клиент ММА)
    type = StringField('type', choices=('spot', 'leverage', 'margin_level', 'mct'))
    # Валюта  фондового  портфеля
    currency = StringField('currency', choices=('NA', 'RUB', 'EUR', 'USD'))
    # Идентификатор рынка
    market = IntegerField('market')
    # код Единого Портфеля, в который включен данный клиент
    union = StringField('union')
    # счет FORTS клиента
    forts_acc = StringField('forts_acc')

    def __str__(self):
        return id


class Market(Entity):
    """
    Названия рынков: ММВБ, ФОРТС...
    """
    ROOT_NAME = 'market'
    id = IntegerField('@id')
    name = StringField('text()')


class MarketPacket(Packet):
    """
    Пакет с доступными рынками.
    """
    ROOT_NAME = 'markets'
    items = NodeListField('market', Market)


class CandleKind(Entity):
    """
    Периоды свечек.
    """
    ROOT_NAME = 'kind'
    id = IntegerField('id')
    name = StringField('name')
    period = IntegerField('period')


class CandleKindPacket(Packet):
    """
    Пакет с доступными периодами.
    """
    ROOT_NAME = 'candlekinds'
    items = NodeListField('kind', CandleKind)


class Security(Entity):
    """
    Ценная бумага.
    """
    ROOT_NAME = 'security'
    id = secid = IntegerField('@secid')
    active = SimpleBooleanField('@active', 'true', 'false')
    # Код инструмента
    seccode = StringField('seccode')
    # Символ категории (класса) инструмента
    instrclass = StringField('instrclass')
    # Тип бумаги
    # В качестве sectype могут встречаться следующие поля:
    # Торгуемые инструменты:
    #   SHARE - акции
    #   BOND - облигации корпоративные
    #   FUT - фьючерсы FORTS
    #   OPT - опционы
    #   GKO - гос. бумаги
    #   FOB - фьючерсы ММВБ
    # Неторгуемые (все кроме IDX приходят только с зарубежных площадок):
    #   IDX - индексы
    #   QUOTES - котировки (прочие)
    #   CURRENCY - валютные пары
    #   ADR - АДР
    #   NYSE - данные с NYSE
    #   METAL - металлы
    #   OIL – нефтяной сектор
    # Также:
    #   ERROR - в случае внутренней ошибки (не должно появляться)
    sectype = StringField('sectype', choices=('SHARE', 'BOND', 'FUT', 'OPT', 'GKO',
                                              'FOB', 'IDX', 'QUOTES', 'CURRENCY',
                                              'ADR', 'NYSE', 'METAL', 'OIL',
                                              'ERROR'))
    # Идентификатор режима торгов по умолчанию
    board = StringField('board')
    # Идентификатор рынка
    market = IntegerField('market')
    # Наименование бумаги
    name = StringField('shortname')
    # Количество десятичных знаков в цене
    decimals = IntegerField('decimals')
    # Шаг цены
    minstep = FloatField('minstep')
    # Размер лота
    lotsize = IntegerField('lotsize')
    # Делитель лота
    lotdivider = IntegerField('lotdivider')
    # Стоимость пункта цены
    point_cost = FloatField('point_cost')
    # Имя таймзоны инструмента
    timezone = StringField('sec_tz')
    # 0 - без стакана; 1 - стакан типа OrderBook; 2 - стакан типа Level2
    quotestype = IntegerField('quotestype')
    # код биржи листинга по стандарту ISO
    mic = StringField('MIC')
    # валюта номинала инструмента
    currency = StringField('currency')
    # валюта расчетов режима торгов по умолчанию
    currency_id = StringField('currencyid')
    # Флаги фичей
    credit_allowed = SimpleBooleanField('opmask/@usecredit', 'yes', 'no')
    bymarket_allowed = SimpleBooleanField('opmask/@bymarket', 'yes', 'no')
    nosplit_allowed = SimpleBooleanField('opmask/@nosplit', 'yes', 'no')
    immediate_allowed = SimpleBooleanField('opmask/@immorcancel', 'yes', 'no')
    cancelbalance_allowed = SimpleBooleanField(
        'opmask/@cancelbalance', 'yes', 'no')
    fok = SimpleBooleanField('opmask/@fok', 'yes', 'no')
    ioc = SimpleBooleanField('opmask/@ioc', 'yes', 'no')


class SecurityPacket(Packet):
    """
    Пакет со списком ценных бумаг.
    """
    ROOT_NAME = 'securities'
    items = NodeListField('security', Security)


class SecInfo(Entity):
    """
    Доп. информация по инструменту.
    """
    ROOT_NAME = 'sec_info'
    id = secid = IntegerField('@secid')
    # Полное наименование инструмента
    secname = StringField('secname')
    # Код инструмента
    seccode = StringField('seccode')
    # Идентификатор рынка
    market = IntegerField('market')
    # Единицы измерения цены
    pname = StringField('pname')
    # Дата погашения
    mat_date = DateTimeField('mat_date', TIME_FORMAT)
    # Цена последнего клиринга (только FORTS)
    clearing_price = FloatField('clearing_price')
    # Минимальная цена (только FORTS)
    minprice = FloatField('minprice')
    # Максимальная цена (только FORTS)
    maxprice = FloatField('maxprice')
    # ГО покупателя (фьючерсы FORTS, руб.)
    buy_deposit = FloatField('buy_deposit')
    # ГО продавца (фьючерсы FORTS, руб.)
    sell_deposit = FloatField('sell_deposit')
    # ГО покрытой позиции (опционы FORTS, руб.)
    bgo_c = FloatField('bgo_c')
    # ГО непокрытой позиции (опционы FORTS, руб.)
    bgo_nc = FloatField('bgo_nc')
    # Текущий НКД, руб
    accruedint = FloatField('accruedint')
    # Размер купона, руб
    coupon_value = FloatField('coupon_value')
    # Дата погашения купона
    coupon_date = DateTimeField('coupon_date', TIME_FORMAT)
    # Период выплаты купона, дни
    coupon_period = IntegerField('coupon_period')
    # Номинал облигации или акции, руб
    facevalue = FloatField('facevalue')
    # Тип опциона Call(C)/Put(P)
    put_call = StringField('put_call', choices=('C', 'P'))
    # Маржинальный(M)/премия(P)
    opt_type = StringField('opt_type', choices=('M', 'P'))
    # Базовое ГО под покупку маржируемого опциона
    bgo_buy = FloatField('bgo_buy')
    # Стоимость пункта цены
    point_cost = FloatField('point_cost')
    # Количество базового актива (FORTS)
    lot_volume = IntegerField('lot_volume')
    # Международный идентификационный код инструмента
    isin = StringField('isin')
    # Номер государственной регистрации инструмента
    reg_number = StringField('regnumber')
    # Цена досрочного выкупа облигации
    buyback_price = FloatField('buybackprice')
    # Дата досрочного выкупа облигации
    buyback_date = DateTimeField('buybackdate', TIME_FORMAT)
    # Валюта расчетов
    currency_id = StringField('currencyid')


class SecInfoUpdate(Entity):
    """
    Обновление информации по инструменту.
    """
    ROOT_NAME = 'sec_info_upd'
    secid = IntegerField('secid')
    # Код инструмента
    seccode = StringField('seccode')
    # Идентификатор рынка
    market = IntegerField('market')
    # Минимальная цена (только FORTS)
    minprice = FloatField('minprice')
    # Максимальная цена (только FORTS)
    maxprice = FloatField('maxprice')
    # ГО покупателя (фьючерсы FORTS, руб.)
    buy_deposit = FloatField('buy_deposit')
    # ГО продавца (фьючерсы FORTS, руб.)
    sell_deposit = FloatField('sell_deposit')
    # ГО покрытой позиции (опционы FORTS, руб.)
    bgo_c = FloatField('bgo_c')
    # ГО непокрытой позиции (опционы FORTS, руб.)
    bgo_nc = FloatField('bgo_nc')
    # Базовое ГО под покупку маржируемого опциона
    bgo_buy = FloatField('bgo_buy')
    # Стоимость пункта цены
    point_cost = FloatField('point_cost')


class Quotation(Entity):
    """
    Котировки по инструменту.
    """
    ROOT_NAME = 'quotation'
    id = secid = IntegerField('@secid')
    # Идентификатор режима торгов по умолчанию
    board = StringField('board')
    # Код инструмента
    seccode = StringField('seccode')
    # Стоимость пункта цены
    point_cost = FloatField('point_cost')
    # НКД на дату торгов в расчете на одну бумагу, руб.
    accrued = FloatField('accruedintvalue')
    # Цена первой сделки
    open = FloatField('open')
    # Средневзвешенная цена
    waprice = FloatField('waprice')
    # Кол-во лотов на покупку по лучшей цене
    bid_depth = IntegerField('biddepth')
    # Совокупный спрос
    demand = IntegerField('biddeptht')
    # Заявок на покупку
    numbids = IntegerField('numbids')
    # Кол-во лотов на продажу по лучшей цене
    offer_depth = IntegerField('offerdepth')
    # Совокупное предложение
    suply = IntegerField('offerdeptht')
    # Заявок на продажу
    numoffers = IntegerField('numoffers')
    # Лучшая котировка на покупку
    best_bid = FloatField('bid')
    # Лучшая котировка на продажу
    best_offer = FloatField('offer')
    # Кол-во сделок
    numtrades = IntegerField('numtrades')
    # Объем совершенных сделок в лотах
    volume_today = IntegerField('voltoday')
    # Общее количество открытых позиций(FORTS)
    open_positions = IntegerField('openpositions')
    # Изм.открытых позиций(FORTS)
    delta_positions = IntegerField('deltapositions')
    # Цена последней сделки
    last_price = FloatField('last')
    # Время заключения последней сделки
    last_time = DateTimeField('time', TIME_FORMAT)
    # Объем последней сделки, в лотах
    last_quantity = IntegerField('quantity')
    # Изменение цены последней сделки по отношению к цене
    # последней сделки предыдущего торгового дня
    change = FloatField('change')
    # Цена последней сделки к оценке предыдущего дня
    change_wa = FloatField('priceminusprevwaprice')
    # Объем совершенных сделок, млн. руб
    value_today = FloatField('valtoday')
    # Доходность, по цене последней сделки
    yld = FloatField('yield')
    # Доходность по средневзвешенной цене
    yld_wa = FloatField('yieldatwaprice')
    # Рыночная цена по результатам торгов сегодняшнего дня
    market_price_today = FloatField('marketpricetoday')
    # Наибольшая цена спроса в течение торговой сессии
    highest_bid = FloatField('highbid')
    # Наименьшая цена предложения в течение торговой сессии
    lowest_offer = FloatField('lowoffer')
    # Максимальная цена сделки
    high = FloatField('high')
    # Минимальная цена сделки
    low = FloatField('low')
    # Цена закрытия
    close = FloatField('closeprice')
    # Доходность по цене закрытия
    close_yld = FloatField('closeyield')
    # Статус «торговые операции разрешены/запрещены»
    status = StringField('status')
    # Состояние торговой сессии по инструменту
    trade_status = StringField('tradingstatus')
    # ГО покупок/покр
    buy_deposit = FloatField('buydeposit')
    # ГО продаж/непокр
    sell_deposit = FloatField('selldeposit')
    # Волатильность
    volatility = FloatField('volatility')
    # Теоретическая цена
    theory_price = FloatField('theoreticalprice')
    # Базовое ГО под покупку маржируемого опциона
    bgo_buy = FloatField('bgo_buy')
    # Официальная текущая цена Биржи
    l_current_price = FloatField('lcurrentprice')


class QuotationPacket(Packet):
    """
    Пакет котировок.
    """
    ROOT_NAME = 'quotations'
    items = NodeListField('quotation', Quotation)


class Trade(Entity):
    """
    Сделка по инструменту на рынке (внешняя).
    """
    ROOT_NAME = 'trade'
    secid = IntegerField('@secid')
    # Наименование борда
    board = StringField('board')
    # Код инструмента
    seccode = StringField('seccode')
    # Биржевой номер сделки
    id = trade_no = StringField('tradeno')
    # Время сделки
    time = DateTimeField('time', TIME_FORMAT)
    # Цена сделки
    price = FloatField('price')
    # Объём в лотах
    quantity = IntegerField('quantity')
    # Покупка (B) / Продажа (S)
    buysell = StringField('buysell', choices=('B', 'S'))
    # кол-во открытых позиций на срочном рынке
    open_interest = IntegerField('openinterest')
    # Период торгов (O - открытие, N - торги, С - закрытие)
    trade_period = StringField('period', choices=(
        'O', 'N', 'C', 'F', 'B', 'T', 'L'))


class TradePacket(Packet):
    """
    Пакет сделок с рынка.
    """
    ROOT_NAME = 'alltrades'
    items = NodeListField('trade', Trade)


class Quote(Entity):
    """
    Глубина рынка по инструменту.
    """
    ROOT_NAME = 'quote'
    id = secid = IntegerField('@secid')
    # Идентификатор режима торгов по умолчанию
    board = StringField('board')
    # Код инструмента
    seccode = StringField('seccode')
    # Цена
    price = FloatField('price')
    # Источник котировки (маркетмейкер)
    source = StringField('source')
    # Доходность облигаций
    yld = IntegerField('yield')
    # Количество бумаг к покупке
    buy = IntegerField('buy')
    # Количество бумаг к продаже
    sell = IntegerField('sell')


class QuotePacket(Packet):
    """
    Пакет обновлений стакана.
    """
    ROOT_NAME = 'quotes'
    items = NodeListField('quote', Quote)


class BaseOrder(Entity):
    """
    Базовый класс ордеров (обычных и стопов) с общими аттрибутами.
    """
    # идентификатор транзакции сервера Transaq
    id = IntegerField('@transactionid')
    # Биржевой номер заявки
    order_no = StringField('orderno')
    # идентификатор бумаги
    secid = IntegerField('secid')
    # Идентификатор борда
    board = StringField('board')
    # Код инструмента
    seccode = StringField('seccode')
    # Цена
    price = FloatField('price')
    # Время регистрации заявки биржей
    time = DateTimeField('time', TIME_FORMAT)
    # Идентификатор клиента
    client = StringField('client')
    # Код юниона
    union = StringField('union')
    # Cтатус заявки
    status = StringField('status')
    # Покупка (B) / Продажа (S)
    buysell = StringField('buysell', choices=('B', 'S'))
    # Дата экспирации (только для ФОРТС)
    exp_date = DateTimeField('expdate', TIME_FORMAT)
    # Примечание
    broker_ref = StringField('brokerref')
    # Время регистрации заявки сервером Transaq (только для условных заявок)
    accept_time = DateTimeField('accepttime', TIME_FORMAT)
    # До какого момента действительно
    valid_before = DateTimeField('validbefore', TIME_FORMAT)
    # Количество лотов
    quantity = IntegerField('quantity')
    # Время снятия заявки, 0 для активных
    withdraw_time = DateTimeField('withdrawtime', TIME_FORMAT)
    withdraw_time.mapper = NullableDateTimeMapper(TIME_FORMAT)
    # Сообщение биржи в случае отказа выставить заявку
    result = StringField('result')


class Order(BaseOrder):
    """Базовый класс ордера"""
    ROOT_NAME = 'order'
    # Биржевой номер заявки
    origin_order_no = StringField('origin_orderno')
    # Объем заявки в валюте инструмента
    value = FloatField('value')
    # НКД
    accrued_int = FloatField('accruedint')
    # Код поставки (значение биржи, определяющее правила расчетов)
    settle_code = StringField('settlecode')
    # Неудовлетворенный остаток объема заявки в лотах (контрактах)
    balance = IntegerField('balance')
    # Скрытое количество в лотах
    hidden = IntegerField('hidden')
    # Доходность
    yld = IntegerField('yield')
    # Условие
    condition = StringField('condition')
    # Цена для условной заявки, либо обеспеченность в процентах
    condition_value = FloatField('conditionvalue')
    # С какого момента времени действительна
    valid_after = DateTimeField('valid_after', TIME_FORMAT)
    # Максимальная комиссия по сделкам заявки
    max_commission = FloatField('maxcomission')


class StopOrder(BaseOrder):
    """Стоп заявка"""
    ROOT_NAME = 'stoporder'
    # номер заявки Биржевой регистрационный номер заявки,
    # выставленной на рынок в результате исполнения cтопа
    order_no = StringField('activeorderno')
    # Идентификатор трейдера, который отменил стоп
    canceller = StringField('canceller')
    # Биржевой  регистрационный  номер  сделки,
    # явившейся основанием для перехода стопа в текущее состояние
    alltrade_no = StringField('alltradeno')
    # Афтар заявки
    author = StringField('author')
    # Привязка к стандартной заявке
    linked_order_no = StringField('linkedorderno')
    # У стопов почему то нет времени активации
    time = None


class StopLoss(StopOrder):
    """Стоп лосс ордер"""
    # Использование кредита
    use_credit = SimpleBooleanField('stoploss/@usecredit', 'yes', 'no')
    # Цена активации
    activation_price = FloatField('stoploss/activationprice')
    # Рыночное исполнение
    bymarket = ItemField('bymarket')
    # Защитное время удержания цены
    # (когда цены на рынке лишь кратковременно достигают уровня цены активации,
    # и вскоре возвращаются обратно)
    guard_time = DateTimeField('stoploss/guardtime', TIME_FORMAT)
    # Примечание
    broker_ref = StringField('stoploss/brokerref')
    # Количество лотов
    quantity = IntegerField('stoploss/quantity')
    # Цена исполнения (отменяет bymarket)
    price = FloatField('stoploss/orderprice')


class TakeProfit(StopOrder):
    """Тейк профит ордер"""
    # Цена активации
    activation_price = FloatField('takeprofit/activationprice')
    # Защитное время удержания цены
    # (когда цены на рынке лишь кратковременно достигают уровня цены активации,
    # и вскоре возвращаются обратно)
    guard_time = DateTimeField('takeprofit/guardtime', TIME_FORMAT)
    # Достигнутый максимум
    extremum = FloatField('takeprofit/extremum')
    # Уровень исполнения?
    level = FloatField('takeprofit/level')
    # Коррекция
    # Позволяет выставить на Биржу заявку,
    # закрывающую позицию в момент окончания тренда на рынке.
    correction = FloatField('takeprofit/correction')
    # Защитный спрэд
    # Для определения цены заявки, исполняющей TP на покупку,
    # защитный спрэд прибавляется к цене рынка.
    # Для определения цены заявки, исполняющей TP на продажу,
    # защитный спрэд вычитается из цены рынка.
    guard_spread = FloatField('takeprofit/guardspread')
    # Примечание
    broker_ref = StringField('takeprofit/brokerref')
    # Количество лотов
    quantity = IntegerField('takeprofit/quantity')


class ClientOrderPacket(Packet):
    """
    Пакет текущих заявок клиента.
    """
    ROOT_NAME = 'orders'

    @classmethod
    def parse(cls, xml):
        result = ClientOrderPacket()
        result.items = []
        root = parseString(xml)
        assert root.tag == ClientOrderPacket.ROOT_NAME
        for child in root:
            if child.tag == Order.ROOT_NAME:
                result.items.append(Order(child))
            elif child.tag == StopOrder.ROOT_NAME:
                for subchild in child:
                    if subchild.tag == 'stoploss':
                        result.items.append(StopLoss(child))
                    elif subchild.tag == 'takeprofit':
                        result.items.append(TakeProfit(child))
        return result


class ClientTrade(Entity):
    """
    Клиентская сделка (т.е. успешно выполненная заявка).
    """
    ROOT_NAME = 'trade'
    # Id бумаги
    secid = IntegerField('secid')
    # Номер сделки на бирже
    id = trade_no = StringField('tradeno')
    # Номер заявки на бирже
    order_no = StringField('orderno')
    # Идентификатор борда
    board = StringField('board')
    # Код инструмента
    seccode = StringField('seccode')
    # Идентификатор клиента
    client = StringField('client')
    # Код юниона
    union = StringField('union')
    # B - покупка, S - продажа
    buysell = StringField('buysell', choices=('B', 'S'))
    # Время сделки
    time = DateTimeField('time', TIME_FORMAT)
    # Примечание
    broker_ref = StringField('brokerref')
    # Объем сделки
    value = FloatField('value')
    # Комиссия
    commission = FloatField('comission')
    # Цена
    price = FloatField('price')
    # Кол-во инструмента в сделках в штуках
    items = IntegerField('items')
    # Количество лотов
    quantity = IntegerField('quantity')
    # Доходность
    yld = IntegerField('yield')
    # НКД
    accrued_int = FloatField('accruedint')
    # тип сделки: ‘T’ – обычная ‘N’ – РПС ‘R’ – РЕПО ‘P’ – размещение
    trade_type = StringField('tradetype', choices=('T', 'N', 'R', 'P'))
    # Код поставки
    settle_code = StringField('settlecode')
    # Текущая позиция по инструменту
    current_position = IntegerField('currentpos')
    # Признак внебиржевой сделки, 1 или поле отсутсвует
    bypass = IntegerField('bypass')
    # Площадка (execution place)
    venue = StringField('venue')


class ClientTradePacket(Packet):
    """
    Пакет клиентских сделок, совершенных за сессию.
    """
    ROOT_NAME = 'trades'
    items = NodeListField('trade', ClientTrade)


class ClientPositionBase(Entity):
    """
    Базовый класс позиции.
    """
    # Идентификатор клиента
    client = StringField('client')
    # Идентификатор портфеля
    union = StringField('union')


class ClientPosition(ClientPositionBase):
    """
    Базовый класс позиции MOEX.
    """
    # Внутренний код рынка
    market = IntegerField('market')
    # Регистр учета
    register = StringField('register')
    # Наименование вида средств
    name = StringField('shortname')
    # Код вида средств
    asset = StringField('asset')
    # Входящий остаток
    saldo_in = FloatField('saldoin')
    # Текущее сальдо
    saldo = FloatField('saldo')
    # Куплено
    bought = FloatField('bought')
    # Продано
    sold = FloatField('sold')
    # В заявках на покупку
    order_buy = FloatField('ordbuy')
    # В заявках на продажу
    order_sell = FloatField('ordsell')


class MoneyPosition(ClientPosition):
    """Денежная позиция"""
    ROOT_NAME = 'money_position'
    #  Код актива
    id = asset = StringField('asset')
    # Код валюты
    currency = StringField("currency")
    # Внутренние коды доступных рынков
    market = IntegerListField('markets/market')
    # В условных заявках на покупку
    order_buy_cond = FloatField('ordbuycond')
    # Сумма списанной комиссии
    commission = FloatField('comission')
    # В заявках на продажу - отсутствует
    ord_sell = 0


class SecurityPosition(ClientPosition):
    """Клиентская позиция"""
    ROOT_NAME = 'sec_position'
    # Код инструмента
    id = secid = IntegerField('secid')
    # Код инструмента
    seccode = asset = StringField('seccode')
    # Неснижаемый остаток
    saldo_min = FloatField('saldomin')
    # Текущая оценка стоимости позиции, в валюте
    # инструмента
    amount = FloatField('amount')
    # Текущая оценка стоимости позиции, в рублях
    equity = FloatField('equity')


class FortsClientPosition(ClientPositionBase):
    """
    Базовый класс позиции FORTS.
    """
    # Внутренние коды доступных рынков
    markets = IntegerListField('markets/market')
    # Наименование вида средств
    name = StringField('shortname')


class FortsSecurityPosition(FortsClientPosition):
    """Клиентская позиция ФОРТС"""
    ROOT_NAME = "forts_position"
    # Код инструмента
    id = secid = IntegerField('secid')
    # Код инструмента
    seccode = StringField('seccode')
    # Входящая позиция по инструменту
    startnet = IntegerField('startnet')
    # В заявках на покупку
    openbuys = IntegerField('openbuys')
    # В заявках на продажу
    opensells = IntegerField('opensells')
    # Текущая позиция по инструменту
    totalnet = IntegerField('totalnet')
    # Куплено
    todaybuy = IntegerField('todaybuy')
    # Продано
    todaysell = IntegerField('todaysell')
    # Маржа для маржируемых опционов
    optmargin = FloatField('optmargin')
    # Вариационная маржа
    varmargin = FloatField('varmargin')
    # Опционов в заявках на  исполнение
    expirationpos = IntegerField('expirationpos')
    # Объем использованого спот-лимита на продажу
    usedsellspotlimit = FloatField('usedsellspotlimit')
    # Текущий спот-лимит на продажу, установленный Брокером
    sellspotlimit = FloatField('sellspotlimit')
    # Нетто-позиция по всем инструментам данного спота
    netto = FloatField('netto')
    # Коэффициент ГО для спота
    kgo = FloatField('kgo')


class FortsCollaterals(FortsClientPosition):
    """Обеспечение FORTS"""
    ROOT_NAME = "forts_collaterals"
    # Текущие<
    current = FloatField('current')
    # Заблокировано<
    blocked = FloatField('blocked')
    # Свободные
    free = FloatField('free')


class FortsMoneyPosition(FortsCollaterals):
    """Денежная позиция ФОРТС"""
    ROOT_NAME = "forts_money"
    # Опер. маржа
    varmargin = FloatField("varmargin")


class SpotLimits(FortsClientPosition):
    """Спот лимиты ФОРТС"""
    ROOT_NAME = "spot_limit"
    # Текущий лимит
    buy_limit = FloatField('buylimit')
    # Заблокировано лимита
    buy_limit_used = FloatField('buylimitused')


class UnitedLimitsUpdate(Entity):
    """Оценка портфеля"""
    ROOT_NAME = "united_limits"
    # Код портфеля
    id = union = StringField("@union")
    # Входящая оценка стоимости единого портфеля
    open_equity = FloatField("open_equity")
    # Текущая оценка стоимости единого портфеля
    equity = FloatField("equity")
    # Начальные требования
    requirements = FloatField("requirements")
    # Свободные средства
    free = FloatField("free")
    # Вариационная маржа FORTS
    vm = FloatField("vm")
    # Финансовый результат последнего клиринга FORTS
    finres = FloatField("finres")
    # Размер требуемого ГО, посчитанный биржей FORTS
    go = FloatField("go")


class PositionPacket(Packet):
    """
    Пакет со списком позиций по инструментам.
    """
    ROOT_NAME = 'positions'

    @classmethod
    def parse(cls, xml):
        result = PositionPacket()
        result.items = []
        root = parseString(xml)
        assert root.tag == PositionPacket.ROOT_NAME
        for child in root:
            if child.tag == MoneyPosition.ROOT_NAME:
                result.items.append(MoneyPosition(child))
            elif child.tag == SecurityPosition.ROOT_NAME:
                result.items.append(SecurityPosition(child))
            elif child.tag == FortsSecurityPosition.ROOT_NAME:
                result.items.append(FortsSecurityPosition(child))
            elif child.tag == FortsCollaterals.ROOT_NAME:
                result.items.append(FortsCollaterals(child))
            elif child.tag == FortsMoneyPosition.ROOT_NAME:
                result.items.append(FortsMoneyPosition(child))
            elif child.tag == SpotLimits.ROOT_NAME:
                result.items.append(SpotLimits(child))
            elif child.tag == UnitedLimitsUpdate.ROOT_NAME:
                result.items.append(UnitedLimitsUpdate(child))
        return result


class ClientLimitsForts(Entity):
    """
    Лимиты клиента на срочном рынке.
    """
    ROOT_NAME = 'clientlimits'
    # Идентификатор клиента
    id = client = StringField('@client')
    # стоимостной лимит открытых позиций (СЛОП срочн.рынок ММВБ)
    cbplimit = FloatField('cbplimit')
    # стоимостная оценка текущих чистых позиций (СОЧП срочн. рынок ММВБ)
    cbplused = FloatField('cbplused')
    # СОЧП с учетом активных заявок (срочный рынок ММВБ)
    cbplplanned = FloatField('cbplplanned')
    # Вар. маржа срочного рынка ММВБ
    fob_varmargin = FloatField('fob_varmargin')
    # Обеспеченность срочного портфеля (FORTS)
    coverage = FloatField('coverage')
    # Коэффициент ликвидности(FORTS)
    liquidity_c = FloatField('liquidity_c')
    # Доход(FORTS)
    profit = FloatField('profit')
    # Деньги текущие
    money_current = FloatField('money_current')
    # Деньги заблокированные
    money_reserve = FloatField('money_reserve')
    # Деньги свободные
    money_free = FloatField('money_free')
    # Премии по опционам(FORTS)
    options_premium = FloatField('options_premium')
    # Биржевой сбор(FORTS)
    exchange_fee = FloatField('exchange_fee')
    # Вар. маржа текущая (FORTS)
    forts_varmargin = FloatField('forts_varmargin')
    # Операционная маржа
    varmargin = FloatField('varmargin')
    # Перечисленная в пром.клиринге вариационная маржа(FORTS)
    pclmargin = FloatField('pclmargin')
    # Вар. маржа по опционам(FORTS)
    options_vm = FloatField('options_vm')
    # Лимит на покупку спот
    spot_buy_limit = FloatField('spot_buy_limit')
    # Лимит на покупку спот использованный
    used_spot_buy_limit = FloatField('used_spot_buy_limit')
    # Залоги текущие
    collat_current = FloatField('collat_current')
    # Залоги заблокированные
    collat_blocked = FloatField('collat_blocked')
    # Залоги свободные
    collat_free = FloatField('collat_free')


class ClientPortfolio(Entity):
    """
    Клиентский портфель Т+, основная рабочая структура для фондовой секции.
    """
    ROOT_NAME = 'portfolio_tplus'
    # Идентификатор клиента
    id = client = StringField('@client')
    # Фактическая обеспеченность
    coverage_fact = FloatField('coverage_fact')
    # Плановая обеспеченность
    coverage_plan = FloatField('coverage_plan')
    # Критическая обеспеченность
    coverage_crit = FloatField('coverage_crit')
    # Входящая оценка портфеля без дисконта
    open_equity = FloatField('open_equity')
    # Текущая оценка портфеля без дисконта
    equity = FloatField('equity')
    # Плановое обеспечение (оценка ликвидационной стоимости портфеля)
    cover = FloatField('cover')
    # Плановая начальная маржа (оценка портфельного риска)
    init_margin = FloatField('init_margin')
    # Прибыль/убыток по входящим позициям
    pnl_income = FloatField('pnl_income')
    # Прибыль/убыток по сделкам
    pnl_intraday = FloatField('pnl_intraday')
    # Фактическое плечо портфеля Т+
    leverage = FloatField('leverage')
    # Фактический уровень маржи портфеля Т+
    margin_level = FloatField('margin_level')

    class _Money(MyXmlObject):
        # Входящая денежная позиция
        open_balance = FloatField('open_balance')
        # Затрачено на покупки
        bought = FloatField('bought')
        # Выручено от продаж
        sold = FloatField('sold')
        # Исполнено
        settled = FloatField('settled')
        # Текущая денежная позиция
        balance = FloatField('balance')
        # Уплачено комиссии
        tax = FloatField('tax')

        class _ValuePart(MyXmlObject):
            # Регистр учёта
            register = StringField('@register')
            # Входящая денежная позиция
            open_balance = FloatField('open_balance')
            # Потрачено на покупки
            bought = FloatField('bought')
            # Выручка от продаж
            sold = FloatField('sold')
            # Исполнено
            settled = FloatField('settled')
            # Текущая денежная позиция
            balance = FloatField('balance')

        value_parts = NodeListField('value_part', _ValuePart)

    money = NodeField('money', _Money)

    class _Security(MyXmlObject):
        # Id инструмента
        secid = IntegerField('@secid')
        # Id рынка
        market = IntegerField('market')
        # Обозначение инструмента
        seccode = StringField('seccode')
        # Текущая цена
        price = FloatField('price')
        # Входящая позиция, штук
        open_balance = IntegerField('open_balance')
        # Куплено, штук
        bought = IntegerField('bought')
        # Продано, штук
        sold = IntegerField('sold')
        # Текущая позиция, штук
        balance = IntegerField('balance')
        # Заявлено купить, штук
        buying = IntegerField('buying')
        # Заявлено продать, штук
        selling = IntegerField('selling')
        # Вклад бумаги в плановое обеспечение
        cover = FloatField('cover')
        # Плановая начальная маржа (риск)
        init_margin = FloatField('init_margin')
        # Cтавка риска для лонгов
        riskrate_long = FloatField('riskrate_long')
        # Cтавка риска для шортов
        riskrate_short = FloatField('riskrate_short')
        # Прибыль/убыток по входящим позициям
        pnl_income = FloatField('pnl_income')
        # Прибыль/убыток по сделкам
        pnl_intraday = FloatField('pnl_intraday')
        # Максимальная покупка, в лотах
        max_buy = IntegerField('maxbuy')
        # Макcимальная продажа, в лотах
        max_sell = IntegerField('maxsell')

        class _ValuePart(MyXmlObject):
            # Входящая позиция, штук
            register = StringField('@register')
            # Входящая позиция, штук
            open_balance = IntegerField('open_balance')
            # Куплено, штук
            bought = IntegerField('bought')
            # Продано, штук
            sold = IntegerField('sold')
            # Исполнено
            settled = IntegerField('settled')
            # Текущая позиция, штук
            balance = IntegerField('balance')
            # Заявлено купить, штук
            buying = IntegerField('buying')
            # Заявлено продать, штук
            selling = IntegerField('selling')

        value_parts = NodeListField('value_part', _ValuePart)

    securities = NodeListField('security', _Security)


class CreditAbility(MyXmlObject):
    """
    Режим кредитования.
    """
    ROOT_NAME = 'overnight'
    # Ночной
    overnight = SimpleBooleanField('@status', 'true', 'false')
    # Дневной
    intraday = SimpleBooleanField('@status', 'false', 'true')


class MarketOrderAbility(MyXmlObject):
    """
    Возможность рыночных заявок.
    """
    ROOT_NAME = 'marketord'
    # Id бумаги
    secid = IntegerField('@secid')
    # Код бумаги
    seccode = StringField('@seccode')
    # Флаг доступности
    permitted = SimpleBooleanField('@permit', 'yes', 'no')


class HistoryTick(Trade):
    """
    Тиковые исторические данные, получаемые после команды subscribe_ticks.
    Дублирует Trade. Разница только в возможности получать старые сделки.
    """
    ROOT_NAME = 'tick'
    secid = IntegerField('secid')
    time = DateTimeField('tradetime', TIME_FORMAT)


class HistoryTickPacket(Packet):
    """
    Пакет старых тиков.
    """
    ROOT_NAME = 'ticks'
    items = NodeListField('tick', HistoryTick)


class Board(Entity):
    """
    Режим торгов (борда). Сочетание типа торгов и рынка.
    TQBR - T+ для акций.
    """
    ROOT_NAME = 'board'
    # Идентификатор режима торгов
    id = StringField('@id')
    # Наименование режима торгов
    name = StringField('name')
    # Внутренний код рынка
    # 1 - ММВБ
    market = IntegerField('market')
    # Тип режима торгов 0=FORTS, 1=Т+, 2=Т0
    type = IntegerField('type')

    def __str__(self):
        return self.name


class BoardPacket(Packet):
    """
    Справочник режимов торгов.
    """
    ROOT_NAME = 'boards'
    items = NodeListField('board', Board)


class SecurityPit(MyXmlObject):
    """
    Питы - параметры инструмента в нестандартных режимах торгов.
    """
    ROOT_NAME = 'pit'
    board = StringField('@board')
    seccode = StringField('@seccode')
    market = IntegerField('market')
    decimals = IntegerField('decimals')
    minstep = FloatField('minstep')
    lotsize = IntegerField('lotsize')
    lotdivider = IntegerField('lotdivider')
    point_cost = FloatField('point_cost')


class SecurityPitPacket(Packet):
    """
    Пакет питов.
    """
    ROOT_NAME = 'pits'
    items = NodeListField('pit', SecurityPit)


class ClientLimitsTPlus(Entity):
    """
    Максимальная покупка/продажа для Т+.
    """
    ROOT_NAME = 'max_buy_sell_tplus'
    # Идентификатор клиента
    id = client = StringField('@client')

    class _Security(MyXmlObject):
        # Id бумаги
        secid = IntegerField('@secid')
        # Внутренний код рынка
        market = IntegerField('market')
        # Код инструмента
        seccode = StringField('seccode')
        # Максимум купить (лотов)
        max_buy = IntegerField('maxbuy')
        # Максимум продать (лотов)
        max_sell = IntegerField('maxsell')

    securities = NodeListField('security', _Security)


class TextMessage(Entity):
    """
    Текстовые сообщения, которые можно передавать через Транзак.
    """
    ROOT_NAME = 'message'
    # Дата
    id = date = StringField('date')
    # Срочность
    urgent = SimpleBooleanField('urgent', 'Y', 'N')
    # Отправитель
    sender = StringField('from')
    # Содержимое
    text = StringField('text')


class TextMessagePacket(Packet):
    """
    Пакет сообщений.
    """
    ROOT_NAME = 'messages'
    items = NodeListField('message', TextMessage)


# class ClientPortfolioMCT(MyXmlObject):
#     """
#     Клиентский портфель MCT/MMA.
#     """
#     ROOT_NAME = 'portfolio_mct'
#     # Идентификатор клиента
#     id = client = StringField('@client')
#     # Валюта портфеля клиента
#     currency = StringField('portfolio_currency')
#     # Величина капитала
#     capital = FloatField('capital')
#     # Использование капитала факт
#     utilization_fact = FloatField('utilization_fact')
#     # Использование капитала план
#     utilization_plan = FloatField('utilization_plan')
#     # Фактическая обеспеченность
#     coverage_fact = FloatField('coverage_fact')
#     # Плановая обеспеченность
#     coverage_plan = FloatField('coverage_plan')
#     # Входящее сальдо
#     open_balance = FloatField('open_balance')
#     # Cуммарная комиссия
#     tax = FloatField('tax')
#     # Прибыль/убыток по входящим позициям
#     pnl_income = FloatField('pnl_income')
#     # Прибыль/убыток по сделкам
#     pnl_intraday = FloatField('pnl_intraday')
#
#     # TODO Доделать портфель mct
#     class _Security(MyXmlObject):
#         pass


class NewsHeader(MyXmlObject):
    """
    Новостной заголовок.
    """
    ROOT_NAME = 'news_header'
    id = IntegerField('id')
    time = DateTimeField('timestamp', TIME_FORMAT)
    source = StringField('source')
    title = StringField('title')


class NewsBody(MyXmlObject):
    """
    Тело новости.
    """
    ROOT_NAME = 'news_body'
    id = IntegerField('id')
    text = StringField('text')


class MultiPortfolio(MyXmlObject):
    """
    Клиентский мультивалютный портфель.
    """
    ROOT_NAME = 'mc_portfolio'
    # Идентификатор клиента
    id = client = StringField('@client')
    # Код портфеля
    union = StringField('@union')
    # Входящая оценка единого портфеля
    open_equity = FloatField('open_equity')
    # Текущая оценка единого портфеля
    equity = FloatField('equity')
    # Прибыль/убыток общий
    pl = FloatField('pl')
    # Размер требуемого ГО, посчитанный биржей FORTS
    go = FloatField('go')
    # Плановый размер обеспечения
    cover = FloatField('cover')
    # Плановый риск (размер начальных требований)
    init_req = FloatField('init_req')
    # Размер минимальных требований
    maint_req = FloatField('maint_req')
    # Нереализов. прибыль/убыток
    unrealized_pnl = FloatField('unrealized_pnl')
    # # Корреляционный вычет планового риска
    # chrgoff_ir = FloatField('chrgoff_ir')
    # # Корреляционный вычет минимальных требований
    # chrgoff_mr = FloatField('chrgoff_mr')
    # # Стоимость портфеля нормативная
    # reg_equity = FloatField('reg_equity')
    # # Плановая начальная маржа нормативная
    # reg_ir = FloatField('reg_ir')
    # # Минимальная маржа нормативная
    # reg_mr = FloatField('reg_mr')
    # # Вариационная маржа FORTS
    # vm = FloatField('vm')
    # # Финансовый результат последнего клиринга FORTS
    # finres = FloatField('finres')

    class _Currency(MyXmlObject):
        # Код валюты
        id = currency = StringField("@currency")
        # Кросс-курс
        cross_rate = FloatField('cross_rate')
        # Входящая денежная позиция
        open_balance = FloatField('open_balance')
        # Текущая денежная позиция
        balance = FloatField('balance')
        # Оценка текущей стоимости
        equity = FloatField('equity')
        # Вклад в плановое обеспечение
        cover = FloatField('cover')
        # Плановый риск
        init_req = FloatField('init_req')
        # Минимальные требования
        maint_req = FloatField('maint_req')
        # Нереализованная прибыль/убыток
        unrealized_pnl = FloatField('unrealized_pnl')

    currencies = NodeListField('portfolio_currency', _Currency)

    class _Money(MyXmlObject):
        # Наименование денежного раздела
        name = StringField('@name')
        # Код валюты
        currency = StringField('@currency')
        # Код базового актива
        asset = StringField('asset')
        # Балансовая цена инвалютной денежной
        # позиции,руб
        balance_prc = FloatField('balance_prc')
        # Входящая денежная позиция
        open_balance = FloatField('open_balance')
        # Затрачено на покупки
        bought = FloatField('bought')
        # Выручено от продаж
        sold = FloatField('sold')
        # # Исполнено
        # settled = FloatField('settled')
        # Текущая денежная позиция
        balance = FloatField('balance')
        # Сумма плановых покупок
        blocked = FloatField('blocked')
        # Сумма плановых продаж
        estimated = FloatField('estimated')
        # Удержано комиссии
        fee = FloatField('fee')
        # Вариационная маржа [FORTS или
        # фьючерсы MMA]
        vm = FloatField('vm')
        # Фин. результат последнего клиринга [ФОРТС]
        finres = FloatField('finres')
        # Вклад в плановое обеспечение
        cover = FloatField('cover')

        class _ValuePart(MyXmlObject):
            # Регистр учёта
            register = StringField('@register')
            # Входящая денежная позиция
            open_balance = FloatField('open_balance')
            # Потрачено на покупки
            bought = FloatField('bought')
            # Выручка от продаж
            sold = FloatField('sold')
            # # Исполнено
            # settled = FloatField('settled')
            # Текущая денежная позиция
            balance = FloatField('balance')
            # Сумма плановых покупок
            blocked = FloatField('blocked')
            # Сумма плановых продаж
            estimated = FloatField('estimated')

        value_parts = NodeListField('value_part', _ValuePart)

    moneys = NodeListField('money', _Money)

    class _Asset(MyXmlObject):
        # Код базового актива
        code = StringField('@code')
        # Наименование базового актива
        name = StringField('@name')
        # Код валюты
        currency = StringField('currency')
        # Стоимость входящей позиции
        open_balance = FloatField('open_balance')
        # Потрачено на покупки
        bought = FloatField('bought')
        # Выручка от продаж
        sold = FloatField('sold')
        # Стоимость текущей позиция
        balance = FloatField('balance')
        # Сумма плановых покупок
        blocked = FloatField('blocked')
        # Сумма плановых продаж
        estimated = FloatField('estimated')
        # Ставка перекрытия
        setoff_rate = FloatField('setoff_rate')
        # Плановый риск
        init_req = FloatField('init_req')
        # Минимальная маржа
        maint_req = FloatField('maint_req')

    assets = NodeListField('asset', _Asset)

    class _Security(MyXmlObject):
        # Id инструмента
        secid = IntegerField('@secid')
        # Id рынка
        market = IntegerField('market')
        # Обозначение инструмента
        seccode = StringField('seccode')
        # Код базового актива
        asset = StringField('asset')
        # Код валюты
        currency = StringField('currency')
        # Входящая цена
        price_in = FloatField('price_in')
        # Текущая цена
        price = FloatField('price')
        # Входящая нетто-позиция, штук
        open_balance = IntegerField('open_balance')
        # Куплено, штук
        bought = IntegerField('bought')
        # Продано, штук
        sold = IntegerField('sold')
        # Текущая нетто-позиция, штук
        balance = IntegerField('balance')
        # Балансовая цена
        balance_prc = FloatField('balance_prc')
        # Нереализов. прибыль/убыток
        unrealized_pnl = FloatField('unrealized_pnl')
        # Заявлено купить, штук
        buying = IntegerField('buying')
        # Заявлено продать, штук
        selling = IntegerField('selling')
        # Оценка текущей стоимости
        equity = FloatField('equity')
        # Вклад в плановое обеспечение
        cover = FloatField('cover')
        # # Стоимость в обеспечении портфеля нормативная
        # reg_equity = FloatField('reg_equity')
        # Cтавка риска для лонгов, %
        riskrate_long = FloatField('riskrate_long')
        # Cтавка риска для шортов, %
        riskrate_short = FloatField('riskrate_short')
        # Ставка резерва для лонгов, %
        reserate_long = FloatField('reserate_long')
        # Ставка резерва для шортов, %
        reserate_short = FloatField('reserate_short')
        # Прибыль/убыток общий
        pl = FloatField('pl')
        # Прибыль/убыток по входящим позициям
        pnl_income = FloatField('pnl_income')
        # Прибыль/убыток по сделкам
        pnl_intraday = FloatField('pnl_intraday')
        # Максимальная покупка, в лотах
        max_buy = IntegerField('maxbuy')
        # Макcимальная продажа, в лотах
        max_sell = IntegerField('maxsell')
        # Индивидуальный шорт-лимит
        borrowed = IntegerField('borrowed')

        class _ValuePart(MyXmlObject):
            # Входящая позиция, штук
            register = StringField('@register')
            # Входящая позиция, штук
            open_balance = IntegerField('open_balance')
            # Куплено, штук
            bought = IntegerField('bought')
            # Продано, штук
            sold = IntegerField('sold')
            # # Исполнено
            # settled = IntegerField('settled')
            # Текущая позиция, штук
            balance = IntegerField('balance')
            # Заявлено купить, штук
            buying = IntegerField('buying')
            # Заявлено продать, штук
            selling = IntegerField('selling')

        value_parts = NodeListField('value_part', _ValuePart)

    securities = NodeListField('security', _Security)


_MY_CLASSES = list(filter(lambda o: inspect.isclass(o) and
                          issubclass(o, (Entity, MyXmlObject)),
                          sys.modules[__name__].__dict__.values()))
