from pydantic import BaseModel
import json
import pathlib
import pandas as pd


class ProductInfo(BaseModel):
    # one product
    product: str
    price: int
    quantity: int


class OrderInfo(BaseModel):
    # one order
    order_id: int
    warehouse_name: str
    highway_cost: int
    products: list[ProductInfo]


def parse_json(json_data: str) -> list[OrderInfo]:
    # parse input json data
    db = [OrderInfo.model_validate_json(json.dumps(item)) for item in json.loads(json_data)]
    return db


def all_data_to_pandas(orders: list[OrderInfo]) -> pd.DataFrame:
    result = pd.DataFrame()
    result['order_id'] = [order.order_id for order in orders for _ in order.products]
    result['warehouse_name'] = [order.warehouse_name for order in orders for _ in order.products]
    result['product'] = [prod.product for order in orders for prod in order.products]
    result['price'] = [prod.price for order in orders for prod in order.products]
    result['delivery_price'] = [calc_whs_rate(order) for order in orders for _ in order.products]
    result['quantity'] = [prod.quantity for order in orders for prod in order.products]

    return result


def calc_whs_rate(order: OrderInfo) -> int:
    # calculate delivery cost for the specified order
    number_of_items = 0
    for product in order.products:
        number_of_items += product.quantity
    return order.highway_cost // number_of_items


def warehouses_rates(orders: list[OrderInfo]) -> pd.DataFrame:
    # TASK 1: calculate delivery cost for all warehouses
    warehouses = {}
    for order in orders:
        if order.warehouse_name not in warehouses:
            warehouses[order.warehouse_name] = calc_whs_rate(order)

    data = {
        'warehouses': [key for key in warehouses.keys()],
        'rates': [value for _, value in warehouses.items()]
    }
    wh_rates = pd.DataFrame(data)
    wh_rates = wh_rates.set_index('warehouses')
    return wh_rates


def products_stats(data: pd.DataFrame) -> pd.DataFrame:
    # TASK 2: calculate info for each unique product: name, quantity, income, expenses, profit
    # TODO: Verify input pd.DataFrame
    data['income'] = data['price'] * data['quantity']
    data['expenses'] = data['quantity'] * data['delivery_price']
    data['profit'] = data['income'] + data['expenses']
    data = data.drop(['order_id', 'warehouse_name', 'price', 'delivery_price'], axis=1)

    data = data.groupby('product', as_index=False).sum()
    data = data.set_index('product')
    return data


def orders_profit(data: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    # TASK 3: calculate profit for each order and average profit for all orders
    # TODO: Verify input pd.DataFrame
    result = pd.DataFrame(data)
    result['order_profit'] = (result['price'] + result['delivery_price']) * result['quantity']
    result = result.groupby('order_id').agg(order_profit=('order_profit', 'sum'))
    avg_profit = result['order_profit'].mean()
    data_avg_profit = {
        'parameter': ['Average orders profit'],
        'value': avg_profit
    }
    data_avg = pd.DataFrame(data_avg_profit)
    data_avg = data_avg.set_index('parameter')
    return result, data_avg


def warehouses_stats(data: pd.DataFrame) -> pd.DataFrame:
    # TASK 4: get warehouse - product info and calculate product profit percentage for each warehouse
    # TODO: Verify input pd.DataFrame
    data_modif = data.copy()
    data_modif['profit'] = (data_modif['price'] + data_modif['delivery_price']) * data_modif['quantity']
    warehouse_profit = data_modif.groupby('warehouse_name')['profit'].sum()
    data_modif = data_modif.groupby(['warehouse_name', 'product'])['profit'].sum()
    data_modif = data_modif.reset_index().merge(warehouse_profit, on='warehouse_name',
                                                suffixes=('_product', '_warehouse'))
    data_modif['percent_profit_product_of_warehouse'] =\
        (data_modif['profit_product'] / data_modif['profit_warehouse']) * 100
    return data_modif


def warehouses_stats_accum_perc(data: pd.DataFrame) -> pd.DataFrame:
    # TASK 5: Calculate accumulated percent
    # TODO: Verify input pd.DataFrame
    data_modif = data.sort_values(by='percent_profit_product_of_warehouse', ascending=False).groupby \
        ('warehouse_name', sort=False)
    data_modif = data_modif.apply(pd.DataFrame).reset_index(drop=True)
    data_modif['accumulated_percent_profit_product_of_warehouse'] = data_modif.groupby('warehouse_name')[
        'percent_profit_product_of_warehouse'].cumsum()
    return data_modif


def accum_perc_categories(data: pd.DataFrame) -> pd.DataFrame:
    # TASK 6: Get categories based on accumulated percent
    # TODO: Verify input pd.DataFrame
    data_modif = data.copy()
    data_modif['category'] = data_modif['accumulated_percent_profit_product_of_warehouse'] \
        .apply(lambda x: 'A' if x <= 70 else ('B' if x <= 90 else 'C'))
    return data_modif


if __name__ == '__main__':
    results_folder = pathlib.Path(__file__).parent.resolve() / 'results'
    results_folder.mkdir(parents=True, exist_ok=True)

    json_path = pathlib.Path(__file__).parent.resolve() / 'trial_task.json'

    with open(json_path) as f:
        db = parse_json(f.read())

    # create pd.DataFrame table with all initial json data
    all_table = all_data_to_pandas(db)

    # calculate delivery rate for each warehouse & save result to csv file
    whs_rates = warehouses_rates(db)
    whs_rates.to_csv(results_folder / '01_whs_rates.csv', encoding='utf-8')

    # calculate statistics for each product & save result to csv file
    product_statistics = products_stats(all_table)
    product_statistics.to_csv(results_folder / '02_products_statistics.csv', encoding='utf-8')

    # calculate profit for each order, average profit for all orders & save result to csv file
    orders_profits, average_orders_profit = orders_profit(all_table)
    orders_profits.to_csv(results_folder / '03_orders_profits.csv', encoding='utf-8')
    average_orders_profit.to_csv(results_folder / '04_average_orders_profit.csv', encoding='utf-8')

    # calculate warehouses statistics & save result to csv file
    wh_statistics = warehouses_stats(all_table)
    wh_statistics.to_csv(results_folder / '05_wh_statistics.csv', encoding='utf-8')

    # calculate accumulated percent for warehouses & save result to csv file
    wh_stats_accum_perc = warehouses_stats_accum_perc(wh_statistics)
    wh_stats_accum_perc.to_csv(results_folder / '06_wh_stats_accum_perc.csv', encoding='utf-8')

    # calculate categories based on accum percent & save result to csv file
    categories = accum_perc_categories(wh_stats_accum_perc)
    categories.to_csv(results_folder / '07_wh_categories.csv', encoding='utf-8')

