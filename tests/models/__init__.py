import unittest


def suite():
    from .test_calendar_model import CalendarModelTest, EpochModelTest, MonthModelTest, DayModelTest, MoonModelTest
    from .test_campaign_model import CampaignModelTest
    from .test_character_model import CharacterModelTest, JournalModelTest
    from .test_event_model import EventModelTest, EventCategoryModelTest
    from .test_main_model import MainModelTest
    from .test_map_model import MapModelTest, MapNodeModelTest, MapNodeTypeModelTest
    from .test_media_model import MediaModelTest
    from .test_mixins import LinkGeneratorTest, PermissionTemplateTest, ProfilePictureTest, \
        SimpleChangeTrackerTest, SimplePermissionCheckerTest
    from .test_party_model import PartyModelTest
    from .test_session_model import SessionModelTest
    from .test_user_model import UserModelTest
    from .test_wiki_model import WikiModelTest

    suite = unittest.TestSuite()

    suite.addTests(unittest.makeSuite(CalendarModelTest))
    suite.addTests(unittest.makeSuite(EpochModelTest))
    suite.addTests(unittest.makeSuite(MonthModelTest))
    suite.addTests(unittest.makeSuite(DayModelTest))
    suite.addTests(unittest.makeSuite(MoonModelTest))
    suite.addTests(unittest.makeSuite(CampaignModelTest))
    suite.addTests(unittest.makeSuite(CharacterModelTest))
    suite.addTests(unittest.makeSuite(JournalModelTest))
    suite.addTests(unittest.makeSuite(EventModelTest))
    suite.addTests(unittest.makeSuite(EventCategoryModelTest))
    suite.addTests(unittest.makeSuite(MainModelTest))
    suite.addTests(unittest.makeSuite(MapModelTest))
    suite.addTests(unittest.makeSuite(MapNodeModelTest))
    suite.addTests(unittest.makeSuite(MapNodeTypeModelTest))
    suite.addTests(unittest.makeSuite(MediaModelTest))
    suite.addTests(unittest.makeSuite(LinkGeneratorTest))
    suite.addTests(unittest.makeSuite(PermissionTemplateTest))
    suite.addTests(unittest.makeSuite(ProfilePictureTest))
    suite.addTests(unittest.makeSuite(SimpleChangeTrackerTest))
    suite.addTests(unittest.makeSuite(SimplePermissionCheckerTest))
    suite.addTests(unittest.makeSuite(PartyModelTest))
    suite.addTests(unittest.makeSuite(SessionModelTest))
    suite.addTests(unittest.makeSuite(UserModelTest))
    suite.addTests(unittest.makeSuite(WikiModelTest))

    return suite
