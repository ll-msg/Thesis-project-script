from django.db import connections
from django.test import TestCase
from MGTdb_shared.views.FuncsAuxAndDb.mergeCcOdc import get_merges
import datetime
from Typhimurium.models import Isolation, Location, Project, Mgt, User



class TestMergeCcs(TestCase):
    multi_db = True
    databases = { 'default', 'typhimurium' }

    def setUp(self):
        cursor = connections['typhimurium'].cursor()

        # add to isolates
        location = Location.objects.create(
            id=188,
            continent="Europe",
            country="Ireland",
            state=None,
            postcode=None
        )

        isolation = Isolation.objects.create(
            id=7131,
            source="human",
            type=None,
            host=None,
            disease=None,
            date=None,
            month=None,
            year=2017
        )

        user = User.objects.create(userId=1)

        project = Project.objects.create(id=1, user=user)

        mgt = Mgt.objects.create(id=5738)



        cursor.execute("""
            INSERT INTO "Typhimurium_isolate" (
                "identifier", "privacy_status", "server_status", "assignment_status",
                "file_forward", "file_reverse", "file_alleles",
                "date_created", "date_modified", "isolation_id", "location_id",
                "project_id", "mgt_id", "mgt1", "serovar", "tmpFn_alleles",
                "file_assembly", "isQuery"
            )
            VALUES (%s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s)
        """, [
            'SRR1164551', 'PU', 'C', 'A',
            '', '', '',
            datetime.datetime(2019, 7, 25, 3, 43, 23),
            datetime.datetime(2019, 7, 25, 3, 50, 35),
            isolation.id, location.id, project.id, mgt.id, 19,
            None, '', '', False
        ])

        # add to cc2_2
        cursor.execute("""
            INSERT INTO "Typhimurium_cc2_2" ("identifier", "merge_timestamp", "date_created", "date_modified", "merge_id_id")
            VALUES (%s, %s, %s, %s, %s)
        """, [12996, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None])

        cursor.execute("""
            INSERT INTO "Typhimurium_cc2_2" ("identifier", "merge_timestamp", "date_created", "date_modified", "merge_id_id")
            VALUES (%s, %s, %s, %s, %s)
        """, [4308, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), 12996])


        # add to cc2_4
        cursor.execute("""
            INSERT INTO "Typhimurium_cc2_4" ("identifier", "merge_timestamp", "date_created", "date_modified", "merge_id_id")
            VALUES (%s, %s, %s, %s, %s)
        """, [460, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None])
        cursor.execute("""
            INSERT INTO "Typhimurium_cc2_4" ("identifier", "merge_timestamp", "date_created", "date_modified", "merge_id_id")
            VALUES (%s, %s, %s, %s, %s)
        """, [240, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), 460])


    # single regular case: cc1 -> cc2 
    def test_single_merge(self):
        
        isolate = (
            649, 'SRR1164551', 'C', 'A', None, 19, 5738, 2, 2, 0, 11, 11, 0, 120, 105, 0, 2551, 2382, 0, 3826, 3688, 0, 
            4824, 4527, 0, 5341, 5314, 0, 5700, 5619, 0, 1, 255, 1, 1535, 13, 3179, 12, 4299, 13, 203, 4527, 300, 5314, 
            None, 5619, None, 5619, None, 5619, None, 5619, None, 5619, 460, 188, 'North America', 'USA', 'MN', None, 7131, 
            'Bos taurus', None, None, None, datetime.date(2009, 3, 2), 2009, 3
        )

        expected_isolate = (240,)

        list_colsInfo = [{"table_name": "cc2_4", "db_col": 54}]
        isolates = [isolate]

        result = get_merges(list_colsInfo, isolates, "Typhimurium")

        self.assertEqual(result[0], expected_isolate)
    
    def test_more_single(self):

        isolate = (
            15886, 'ERR1948294', 'C', 'A', None, 19, 14651, 1, 1, 0, 1, 1, 0, 1001, 1, 1, 5806, 5258, 1, 1, 1, 0, 11567, 10532, 
            1, 13645, 13036, 1, 14546, 13823, 1, 1, 255, 1, 1535, 1, 319, 4222, None, 1, 7294, 1, 3543, 12358, None, 13324, None, 
            13324, None, 12996, None, 1, 19102, 1, 11563, 265, 'Europe', 'Ireland', None, None, 2769, 'human', None, None, None, None, 2017, None
        )

        expected_isolate = (4308,)

        list_colsInfo = [{"table_name": "cc2_2", "db_col": 49}]
        isolates = [isolate]

        result = get_merges(list_colsInfo, isolates, "Typhimurium")

        self.assertEqual(result[0], expected_isolate)


    # no merge
    def test_no_merge(self):
        isolate = (
            8755, 'ERR170649', 'C', 'A', None, None, 558, 2, 2, 0, 11, 11, 0, 27, 27, 0, 118, 115, 0, 145, 141, 0, 194, 179, 0, 
            73, 215, 0, 578, 751, 0, 1, 255, 1, 1535, 13, 3179, 12, 4299, 141, None, 179, None, 215, None, 248, None, 248, None, 
            248, None, 248, 29434, 240, 460, 295, 'Europe', 'United Kingdom', ' Scotland', None, 2876, 'bovine', None, None, None, 
            None, 1995, None
        )

        expected_isolate = (248,)
        list_colsInfo = [{"table_name": "cc2_2", "db_col": 47}]
        isolates = [isolate]

        result = get_merges(list_colsInfo, isolates, "Typhimurium")
        self.assertEqual(result[0], expected_isolate)

    # null value
    def test_null_value(self):
        isolate = (
            8755, 'ERR170649', 'C', 'A', None, None, 558, 2, 2, 0, 11, 11, 0, 27, 27, 0, 118, 115, 0, 145, 141, 0, 194, 179, 0,
            73, 215, 0, 578, 751, 0, 1, 255, 1, 1535, 13, 3179, 12, 4299, 141, None, 179, None, 215, None, 248, None, 248, None, 248, None, 248, None,
            None, None, 240, 460, 295, 'Europe', 'United Kingdom', ' Scotland', None, 2876, 'bovine', None, None, None, None, 1995, None
        )

        expected_isolate = (None,)
        list_colsInfo = [{"table_name": "cc2_4", "db_col": 54}]
        isolates = [isolate]

        result = get_merges(list_colsInfo, isolates, "Typhimurium")
        self.assertEqual(result[0], expected_isolate)
