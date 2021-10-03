import unittest


def suite():
    from .test_calendar_smoke import CalendarSmokeTest, EpochSmokeTest, MonthSmokeTest, DaySmokeTest, MoonSmokeTest
    from .test_campaign_smoke import CampaignSmokeTest
    from .test_character_smoke import CharacterSmokeTest, JournalSmokeTest
    from .test_event_smoke import EventSmokeTest, EventCategorySmokeTest
    from .test_main_smoke import MainSmokeTest
    from .test_map_smoke import MapSmokeTest, MapNodeSmokeTest, MapNodeTypeSmokeTest
    from .test_media_smoke import MediaSmokeTest
    from .test_party_smoke import PartySmokeTest
    from .test_random_smoke import DiceSetSmokeTest, RandomTableSmokeTest, RandomTableEntrySmokeTest
    from .test_session_smoke import SessionSmokeTest
    from .test_user_smoke import UserSmokeTest
    from .test_wiki_smoke import WikiSmokeTest

    suite = unittest.TestSuite()

    suite.addTests(unittest.makeSuite(CalendarSmokeTest))
    suite.addTests(unittest.makeSuite(EpochSmokeTest))
    suite.addTests(unittest.makeSuite(MonthSmokeTest))
    suite.addTests(unittest.makeSuite(DaySmokeTest))
    suite.addTests(unittest.makeSuite(MoonSmokeTest))
    suite.addTests(unittest.makeSuite(CampaignSmokeTest))
    suite.addTests(unittest.makeSuite(CharacterSmokeTest))
    suite.addTests(unittest.makeSuite(JournalSmokeTest))
    suite.addTests(unittest.makeSuite(EventSmokeTest))
    suite.addTests(unittest.makeSuite(EventCategorySmokeTest))
    suite.addTests(unittest.makeSuite(MainSmokeTest))
    suite.addTests(unittest.makeSuite(MapSmokeTest))
    suite.addTests(unittest.makeSuite(MapNodeSmokeTest))
    suite.addTests(unittest.makeSuite(MapNodeTypeSmokeTest))
    suite.addTests(unittest.makeSuite(MediaSmokeTest))
    suite.addTests(unittest.makeSuite(DiceSetSmokeTest))
    suite.addTests(unittest.makeSuite(RandomTableSmokeTest))
    suite.addTests(unittest.makeSuite(RandomTableEntrySmokeTest))
    suite.addTests(unittest.makeSuite(PartySmokeTest))
    suite.addTests(unittest.makeSuite(SessionSmokeTest))
    suite.addTests(unittest.makeSuite(UserSmokeTest))
    suite.addTests(unittest.makeSuite(WikiSmokeTest))

    return suite
