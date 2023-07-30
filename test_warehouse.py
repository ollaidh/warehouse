import unittest
from warehouse import *


class TestWH(unittest.TestCase):
    def setUp(self) -> None:
        self.db = [
            OrderInfo(order_id=11973, warehouse_name="Мордор", highway_cost=-70, products=[
                {
                    "product": "ломтик июльского неба",
                    "price": 450,
                    "quantity": 1
                },
                {
                    "product": "билет в Израиль",
                    "price": 1000,
                    "quantity": 3
                },
                {
                    "product": "статуэтка Ленина",
                    "price": 200,
                    "quantity": 3
                }
            ]
                      ),
            OrderInfo(order_id=62239, warehouse_name="хутор близ Диканьки", highway_cost=-15, products=[
                {
                    "product": "билет в Израиль",
                    "price": 1000,
                    "quantity": 1
                }
            ]
                      ),
            OrderInfo(order_id=85794, warehouse_name="отель Лето", highway_cost=-50, products=[
                {
                    "product": "зеленая пластинка",
                    "price": 10,
                    "quantity": 2
                }
            ]
                      ),
            OrderInfo(order_id=33684, warehouse_name="Мордор", highway_cost=-30, products=[
                {
                    "product": "билет в Израиль",
                    "price": 1000,
                    "quantity": 2
                },
                {
                    "product": "зеленая пластинка",
                    "price": 10,
                    "quantity": 1
                }
            ]
                      )
        ]

    def test_all_data_to_pandas(self):
        result = all_data_to_pandas(self.db)
        self.assertEqual([11973, 11973, 11973, 62239, 85794, 33684, 33684], result['order_id'].tolist())
        self.assertEqual(['Мордор',
                          'Мордор',
                          'Мордор',
                          'хутор близ Диканьки',
                          'отель Лето',
                          'Мордор',
                          'Мордор'], result['warehouse_name'].tolist())
        self.assertEqual(['ломтик июльского неба',
                          'билет в Израиль',
                          'статуэтка Ленина',
                          'билет в Израиль',
                          'зеленая пластинка',
                          'билет в Израиль',
                          'зеленая пластинка'], result['product'].tolist())
        self.assertEqual([450, 1000, 200, 1000, 10, 1000, 10], result['price'].tolist())
        self.assertEqual([-10, -10, -10, -15, -25, -10, -10], result['delivery_price'].tolist())
        self.assertEqual([1, 3, 3, 1, 2, 2, 1], result['quantity'].tolist())

    def test_calc_whs_rate(self):
        inp1 = OrderInfo(order_id=1, warehouse_name="WH1", highway_cost=-70, products=[
            {
                "product": "ломтик июльского неба",
                "price": 450,
                "quantity": 1
            },
            {
                "product": "билет в Израиль",
                "price": 1000,
                "quantity": 3
            },
            {
                "product": "статуэтка Ленина",
                "price": 200,
                "quantity": 3
            }
        ])
        self.assertEqual(-10, calc_whs_rate(inp1))
        inp2 = OrderInfo(order_id=2, warehouse_name="WH2", highway_cost=-100, products=[
            {
                "product": "ломтик июльского неба",
                "price": 450,
                "quantity": 1
            },
            {
                "product": "билет в Израиль",
                "price": 1000,
                "quantity": 1
            },
            {
                "product": "статуэтка Ленина",
                "price": 200,
                "quantity": 3
            }
        ])
        self.assertEqual(-20, calc_whs_rate(inp2))

    def test_products_stats(self):
        result = products_stats(all_data_to_pandas(self.db))

        self.assertEqual(1, result.at['ломтик июльского неба', 'quantity'])
        self.assertEqual(6, result.at['билет в Израиль', 'quantity'])
        self.assertEqual(3, result.at['зеленая пластинка', 'quantity'])
        self.assertEqual(3, result.at['статуэтка Ленина', 'quantity'])

        self.assertEqual(450, result.at['ломтик июльского неба', 'income'])
        self.assertEqual(6000, result.at['билет в Израиль', 'income'])
        self.assertEqual(30, result.at['зеленая пластинка', 'income'])
        self.assertEqual(600, result.at['статуэтка Ленина', 'income'])

        self.assertEqual(-10, result.at['ломтик июльского неба', 'expenses'])
        self.assertEqual(-65, result.at['билет в Израиль', 'expenses'])
        self.assertEqual(-60, result.at['зеленая пластинка', 'expenses'])
        self.assertEqual(-30, result.at['статуэтка Ленина', 'expenses'])

        self.assertEqual(440, result.at['ломтик июльского неба', 'profit'])
        self.assertEqual(5935, result.at['билет в Израиль', 'profit'])
        self.assertEqual(-30, result.at['зеленая пластинка', 'profit'])
        self.assertEqual(570, result.at['статуэтка Ленина', 'profit'])

    def test_orders_profit(self):
        df = all_data_to_pandas(self.db)
        columns_before = df.columns
        result_table, avg = orders_profit(df)

        # verify that the original df is not changed
        self.assertListEqual(list(df.columns), list(columns_before))

        self.assertEqual(985, result_table.at[62239, 'order_profit'])
        self.assertEqual(3980, result_table.at[11973, 'order_profit'])
        self.assertEqual(-30, result_table.at[85794, 'order_profit'])
        self.assertEqual(1980, result_table.at[33684, 'order_profit'])
        self.assertEqual(1728.75, avg.at['Average orders profit', 'value'])

    def test_warehouses_stats(self):
        result = warehouses_stats(all_data_to_pandas(self.db))
        perc_value1 = result.loc[(result['product'] ==
                                  'зеленая пластинка') & (result['warehouse_name'] == 'отель Лето'),
        'percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(100, perc_value1)

        perc_value2 = result.loc[(result['product'] == 'билет в Израиль')
                                 & (result['warehouse_name'] == 'хутор близ Диканьки'),
        'percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(100, perc_value2)

        perc_value3 = result.loc[(result['product'] == 'билет в Израиль') & (result['warehouse_name'] == 'Мордор'),
        'percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(83.05, perc_value3.round(2))

        perc_value4 = result.loc[(result['product'] == 'зеленая пластинка') & (result['warehouse_name'] == 'Мордор'),
        'percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(0, perc_value4)

        perc_value5 = result.loc[(result['product'] == 'статуэтка Ленина')
                                 & (result['warehouse_name'] == 'Мордор'),
        'percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(9.56, perc_value5.round(2))

        perc_value6 = result.loc[(result['product'] == 'ломтик июльского неба')
                                 & (result['warehouse_name'] == 'Мордор'),
        'percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(7.38, perc_value6.round(2))

    def test_warehouses_stats_accum_perc(self):
        wh_stats = warehouses_stats(all_data_to_pandas(self.db))
        result = warehouses_stats_accum_perc(wh_stats)
        accum_perc_value1 = result.loc[(result['product'] == 'зеленая пластинка')
                                       & (result['warehouse_name'] == 'отель Лето'),
        'accumulated_percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(100, accum_perc_value1)

        accum_perc_value2 = result.loc[(result['product'] == 'билет в Израиль')
                                       & (result['warehouse_name'] == 'хутор близ Диканьки'),
        'accumulated_percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(100, accum_perc_value2)

        accum_perc_value3 = result.loc[(result['product'] == 'билет в Израиль')
                                       & (result['warehouse_name'] == 'Мордор'),
        'accumulated_percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(83.05, accum_perc_value3.round(2))

        accum_perc_value4 = result.loc[(result['product'] == 'зеленая пластинка')
                                       & (result['warehouse_name'] == 'Мордор'),
        'accumulated_percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(100, accum_perc_value4)

        accum_perc_value5 = result.loc[(result['product'] == 'статуэтка Ленина')
                                       & (result['warehouse_name'] == 'Мордор'),
        'accumulated_percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(92.62, accum_perc_value5.round(2))

        accum_perc_value6 = result.loc[(result['product'] == 'ломтик июльского неба')
                                       & (result['warehouse_name'] == 'Мордор'),
        'accumulated_percent_profit_product_of_warehouse'].values[0]
        self.assertEqual(100, accum_perc_value6.round(2))

    def test_accum_perc_categories(self):
        wh_stats = warehouses_stats(all_data_to_pandas(self.db))
        result = accum_perc_categories(warehouses_stats_accum_perc(wh_stats))
        category1 = result.loc[(result['product'] == 'зеленая пластинка')
                               & (result['warehouse_name'] == 'отель Лето'), 'category'].values[0]
        self.assertEqual('C', category1)

        category2 = result.loc[(result['product'] == 'билет в Израиль')
                               & (result['warehouse_name'] == 'хутор близ Диканьки'), 'category'].values[0]
        self.assertEqual('C', category2)

        category3 = result.loc[(result['product'] == 'билет в Израиль') & (result['warehouse_name'] == 'Мордор'),
        'category'].values[0]
        self.assertEqual('B', category3)

        category4 = result.loc[(result['product'] == 'зеленая пластинка') & (result['warehouse_name'] == 'Мордор'),
        'category'].values[0]
        self.assertEqual('C', category4)

        category5 = result.loc[(result['product'] == 'статуэтка Ленина') & (result['warehouse_name'] == 'Мордор'),
        'category'].values[0]
        self.assertEqual('C', category5)

        category6 = result.loc[(result['product'] == 'ломтик июльского неба') & (result['warehouse_name'] == 'Мордор'),
        'category'].values[0]
        self.assertEqual('C', category6)


if __name__ == '__main__':
    unittest.main()
