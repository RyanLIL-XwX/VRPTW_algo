import unittest
from unittest.mock import patch, mock_open
import json
from io import StringIO
from Data_loader import load_data, classify_orders_by_district
from Order import Order


class TestOrderProcessing(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            "input": {
                "forceMerge": "Y",
                "handOverTimeBy": "Weight",
                "orderList": [
                    {
                        "areaId": [10785],
                        "deliveryAddress": "北京市顺义区顺平路576号",
                        "deliveryEarliestTime": "2024-01-01 20:00:00",
                        "deliveryLatestTime": "2024-01-01 20:00:00",
                        "lineId": 0,
                        "orderCode": "ROX240101000000001",
                        "pointType": 0,
                        "receivingAddress": "北京市密云县古北口镇司马台村国际休闲旅游度假区第一层101单元",
                        "receivingCity": "北京市辖区",
                        "receivingDistrict": "密云区",
                        "receivingEarliestTime": "2024-01-01 21:00:00",
                        "receivingLatestTime": "2024-01-02 07:00:00",
                        "receivingLatitude": "40.662436",
                        "receivingLongitude": "117.251497",
                        "receivingProvince": "北京市",
                        "siteSeq": 0,
                        "volume": 0.333901,
                        "weight": 0.0954,
                        "workTime": 0
                    },
                    {
                        "areaId": [10785],
                        "deliveryAddress": "北京市顺义区顺平路576号",
                        "deliveryEarliestTime": "2024-01-01 20:00:00",
                        "deliveryLatestTime": "2024-01-01 20:00:00",
                        "lineId": 0,
                        "orderCode": "ROX240101000000363",
                        "pointType": 0,
                        "receivingAddress": "北京市大兴区区西红门宏福路鸿坤生活广场",
                        "receivingCity": "北京市辖区",
                        "receivingDistrict": "大兴区",
                        "receivingEarliestTime": "2024-01-01 21:00:00",
                        "receivingLatestTime": "2024-01-02 07:00:00",
                        "receivingLatitude": "39.797382",
                        "receivingLongitude": "116.346796",
                        "receivingProvince": "北京市",
                        "siteSeq": 0,
                        "volume": 0.347923,
                        "weight": 0.099406,
                        "workTime": 0
                    }
                ],
                "vehicleType": {
                    "loadableVolume": 11.0,
                    "loadableWeight": 2.5,
                    "vehicleTypeCode": "100001"
                },
                "warehouse": {
                    "address": "北京市顺义区顺平路576号",
                    "addressId": 0,
                    "closeTime": "2024-01-02 23:00:59",
                    "latitude": "40.1196490409737",
                    "longitude": "116.60616697651679",
                    "openTime": "2023-12-31 00:00:00"
                },
                "parameter": {
                    "CenterLineDistanceLimit": 0.0,
                    "DC": 1.5,
                    "allowDistrictLimit": 3,
                    "centerLineDistanceLimit": 0.0,
                    "dC": 1.5,
                    "handoverFixedTime": 15,
                    "handoverVariableTime": 1,
                    "logOpen": 0,
                    "receivingAccessLimit": 20,
                    "receivingDistanceLimit": 100,
                    "shortestPathMode": 0,
                    "speed": 30,
                    "timeSpan": 0.0
                },
                "taskCode": "000277"
            }
        }
        self.sample_json = json.dumps(self.sample_data)

    def suppress_print(self, func, *args, **kwargs):
        with patch('sys.stdout', new=StringIO()):
            return func(*args, **kwargs)

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_load_data_file_not_found(self, mock_file):
        orders, header = self.suppress_print(load_data, "nonexistent.txt")
        self.assertIsNone(orders)
        self.assertIsNone(header)
        mock_file.assert_called_once_with("nonexistent.txt", 'r', encoding='utf-8')

    @patch("builtins.open", new_callable=mock_open, read_data="Invalid JSON")
    def test_load_data_json_decode_error(self, mock_file):
        orders, header = self.suppress_print(load_data, "sample.txt")
        self.assertIsNone(orders)
        self.assertIsNone(header)
        mock_file.assert_called_once_with("sample.txt", 'r', encoding='utf-8')

    @patch("builtins.open", new_callable=mock_open)
    def test_load_data_success(self, mock_file):
        mock_file.return_value.read.return_value = self.sample_json
        orders, header = load_data("sample.txt")
        self.assertIsNotNone(orders)
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].order_code, "ROX240101000000001")
        self.assertEqual(header["max_weight"], 2.5)
        mock_file.assert_called_once_with("sample.txt", 'r', encoding='utf-8')

    def test_classify_orders_by_district(self):
        orders = [
            Order(
                order_code="ROX240101000000001",
                receiving_address="北京市密云县古北口镇司马台村国际休闲旅游度假区第一层101单元",
                receiving_latitude="40.662436",
                receiving_longitude="117.251497",
                receiving_district="密云区",
                weight=0.0954,
                volume=0.333901,
                receiving_earliest_time="2024-01-01 21:00:00",
                receiving_latest_time="2024-01-02 07:00:00"
            ),
            Order(
                order_code="ROX240101000000363",
                receiving_address="北京市大兴区区西红门宏福路鸿坤生活广场",
                receiving_latitude="39.797382",
                receiving_longitude="116.346796",
                receiving_district="大兴区",
                weight=0.099406,
                volume=0.347923,
                receiving_earliest_time="2024-01-01 21:00:00",
                receiving_latest_time="2024-01-02 07:00:00"
            ),
            Order(
                order_code="ROX240101000000364",
                receiving_address="北京市东城区东直门南大街",
                receiving_latitude="39.946079",
                receiving_longitude="116.43794",
                receiving_district="东城区",
                weight=0.123456,
                volume=0.456789,
                receiving_earliest_time="2024-01-01 21:00:00",
                receiving_latest_time="2024-01-02 07:00:00"
            )
        ]
        classified_orders = classify_orders_by_district(orders)
        self.assertEqual(len(classified_orders["密云区"]), 1)
        self.assertEqual(len(classified_orders["大兴区"]), 1)
        self.assertEqual(len(classified_orders["东城区"]), 1)
        self.assertEqual(classified_orders["密云区"][0].order_code, "ROX240101000000001")
        self.assertEqual(classified_orders["大兴区"][0].order_code, "ROX240101000000363")
        self.assertEqual(classified_orders["东城区"][0].order_code, "ROX240101000000364")


if __name__ == '__main__':
    unittest.main()
