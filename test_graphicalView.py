from django.db import connections
from django.test import TestCase
from collections import Counter


class TestGraphialView(TestCase):

    multi_db = True
    databases = {"typhimurium", "salmonella"}

    @staticmethod
    def execute(query, org):
        with connections[org].cursor() as cursor:
            cursor.execute(query)
            rows = [row[0] for row in cursor.fetchall()]
        return rows

    @staticmethod
    def calTop10(rows):
        counter = Counter(rows)
        top10 = [s for s, c in counter.most_common(10)]
        return top10
    
    @staticmethod
    def buildQuery(org, join, firstLvl, thirdLvl):
        query = f"""
            SELECT i.{thirdLvl}
            FROM "{org}_isolate" AS i
            LEFT JOIN "{org}_{join}" AS j ON i.{join}_id = j.id
            WHERE i.{thirdLvl} IS NOT NULL
            AND j.{firstLvl} IS NOT NULL
            AND i.privacy_status = 'PU';
        """
        return query
    
    @staticmethod
    def buildQueryWithView(org, join, firstLvl, thirdLvl):
        query = f"""
            SELECT v.{thirdLvl}
            FROM "{org}_isolate" AS i
            LEFT JOIN "{org}_{join}" AS j ON i.{join}_id = j.id
            LEFT JOIN "{org}_view_apcc" AS v ON i.mgt_id = v.mgt_id
            WHERE v.{thirdLvl} IS NOT NULL
            AND j.{firstLvl} IS NOT NULL
            AND i.privacy_status = 'PU';
        """
        return query

    ### Typhimurium ###
    ### MGT1, CC-MGT2, ODC10 ###
    def test_mgt1_typhi_time(self):
        FULL_QUERY = self.buildQuery("Typhimurium", "isolation", "year", "mgt1")
        expected = [19, 34, 36, 313, 0, 99, 213, 568, 2072, 2066]
        rows = self.execute(FULL_QUERY, "typhimurium")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
        
    def test_mgt1_typhi_loc(self):
        FULL_QUERY = self.buildQuery("Typhimurium", "location", "country", "mgt1")
        expected = [19, 34, 36, 313, 0, 99, 213, 2072, 302, 568]
        rows = self.execute(FULL_QUERY, "typhimurium")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ccMGT2_typhi_time(self):
        FULL_QUERY = self.buildQueryWithView("Typhimurium", "isolation", "year", "cc1_2")
        expected = [1, 11, 332, 546, 259, 491, 525, 515, 285, 257]
        rows = self.execute(FULL_QUERY, "typhimurium")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)

    def test_ccMGT2_typhi_loc(self):
        FULL_QUERY = self.buildQueryWithView("Typhimurium", "location", "country", "cc1_2")
        expected = [1, 11, 332, 515, 712, 546, 259, 491, 525, 285]
        rows = self.execute(FULL_QUERY, "typhimurium")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ODC10_typhi_time(self):
        FULL_QUERY = self.buildQueryWithView("Typhimurium", "isolation", "year", "cc2_4")
        expected = [21, 8530, 2, 1053, 162, 8555, 240, 6, 8542, 1184]
        rows = self.execute(FULL_QUERY, "typhimurium")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ODC10_typhi_loc(self):
        FULL_QUERY = self.buildQueryWithView("Typhimurium", "location", "country", "cc2_4")
        expected = [21, 8530, 32, 2, 1053, 162, 240, 8555, 6, 50]
        rows = self.execute(FULL_QUERY, "typhimurium")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    ### Salmonella ###
    ### MGT1, CC-MGT8, ODC10 ###
    def test_mgt1_salmo_time(self):
        FULL_QUERY = self.buildQuery("Salmonella", "isolation", "year", "mgt1")
        expected = [32, 0, 102, 152, 64, 15, 118, 13, 10, 24]
        rows = self.execute(FULL_QUERY, "salmonella")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_mgt1_salmo_loc(self):
        FULL_QUERY = self.buildQuery("Salmonella", "location", "country", "mgt1")
        expected = [32, 0, 118, 102, 24, 152, 22, 64, 13, 15]
        rows = self.execute(FULL_QUERY, "salmonella")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ccMGT8_salmo_time(self):
        FULL_QUERY = self.buildQueryWithView("Salmonella", "isolation", "year", "cc1_8")
        expected = [64441, 92859, 62053, 151, 48564, 164235, 37356, 55308, 94149, 43467]
        rows = self.execute(FULL_QUERY, "salmonella")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ccMGT8_salmo_loc(self):
        FULL_QUERY = self.buildQueryWithView("Salmonella", "location", "country", "cc1_8")
        expected = [92859, 30647, 63264, 64441, 148822, 48564, 49637, 62053, 151, 89849]
        rows = self.execute(FULL_QUERY, "salmonella")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ODC10_salmo_time(self):
        FULL_QUERY = self.buildQueryWithView("Salmonella", "isolation", "year", "cc2_4")
        expected = [1159, 2436, 27991, 35238, 11983, 33348, 574, 6443, 6871, 12678]
        rows = self.execute(FULL_QUERY, "salmonella")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    
    def test_ODC10_salmo_loc(self):
        FULL_QUERY = self.buildQueryWithView("Salmonella", "location", "country", "cc2_4")
        expected = [1159, 2436, 11983, 35238, 6443, 27991, 33348, 12678, 10668, 574]
        rows = self.execute(FULL_QUERY, "salmonella")
        top10 = self.calTop10(rows)
        self.assertEqual(expected, top10)
    