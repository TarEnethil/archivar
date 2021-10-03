import unittest


def suite():
    from .test_app_helpers import AppHelperTest, AppDecoratorsTest, AppProcessorsTest, AppValidatorsTest
    from .test_calendar_helpers import CalendarHelperTest
    from .test_campaign_helpers import CampaignHelperTest
    from .test_character_helpers import CharacterHelperTest, JournalHelperTest
    from .test_event_helpers import EventHelperTest
    from .test_main_helpers import MainHelperTest
    from .test_map_helpers import MapHelperTest
    from .test_media_helpers import MediaHelperTest
    from .test_party_helpers import PartyHelperTest
    from .test_random_helpers import RandomHelperTest
    from .test_session_helpers import SessionHelperTest
    from .test_user_helpers import UserHelperTest
    from .test_wiki_helpers import WikiHelperTest

    suite = unittest.TestSuite()

    suite.addTests(unittest.makeSuite(AppHelperTest))
    suite.addTests(unittest.makeSuite(AppDecoratorsTest))
    suite.addTests(unittest.makeSuite(AppProcessorsTest))
    suite.addTests(unittest.makeSuite(AppValidatorsTest))
    suite.addTests(unittest.makeSuite(CalendarHelperTest))
    suite.addTests(unittest.makeSuite(CampaignHelperTest))
    suite.addTests(unittest.makeSuite(CharacterHelperTest))
    suite.addTests(unittest.makeSuite(JournalHelperTest))
    suite.addTests(unittest.makeSuite(EventHelperTest))
    suite.addTests(unittest.makeSuite(MainHelperTest))
    suite.addTests(unittest.makeSuite(MapHelperTest))
    suite.addTests(unittest.makeSuite(MediaHelperTest))
    suite.addTests(unittest.makeSuite(PartyHelperTest))
    suite.addTests(unittest.makeSuite(RandomHelperTest))
    suite.addTests(unittest.makeSuite(SessionHelperTest))
    suite.addTests(unittest.makeSuite(UserHelperTest))
    suite.addTests(unittest.makeSuite(WikiHelperTest))

    return suite
