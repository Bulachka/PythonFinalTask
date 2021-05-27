import json
import os
import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import patch

import data_for_tests as td
from main_reader import rss_reader as rs

NEWSLINK = "https://news.yahoo.com/rss/"


class TestMainReader(unittest.TestCase):
    """
    Tests for effective parsing links, making news dictionaries, printing news in json and normal format,
    setting and working limits of the numbers of news.
    """

    #  Tests for function "open_rss_link"
    @patch("builtins.print", autospec=True, side_effect=print)
    def test_bad_link(self, mock_print):
        # Test URLError is raising and user-friendly message is printing to stdout, if we give a bad link
        bad_link = "https://news.yaom/rss/"
        rs.open_rss_link(bad_link, verbose=None)
        message = mock_print.call_args_list[0].args[0]
        self.assertEqual(message, "Bad link, please try again")

    @patch("builtins.print", autospec=True, side_effect=print)
    def test_no_link(self, mock_print):
        # Test ValueError is raising and user-friendly message is printing to stdout, if we give a bad link
        rs.open_rss_link("", verbose=None)
        message = mock_print.call_args_list[0].args[0]
        self.assertEqual(message, "Please insert rss link")

    # def test_normal_link(self):
    #     # Test parsing of the normal ling Yahoo NEWSLINK goes good and we receive expected header
    #     content = rs.open_rss_link("fake_rss_site.txt", verbose=None)
    #     self.assertTrue(content.feed.title, "CNN.com - RSS Channel - App Travel Section")

    # Tests for function "printing_parsing_news"
    @patch("builtins.print", autospec=True, side_effect=print)
    def test_normal_print(self, mock_print):
        # Test we have print as expected
        rs.printing_parsing_news(td.TEST_NEWSDICT, 1)
        message_head = mock_print.call_args_list[0].args[0]
        news_title = mock_print.call_args_list[1].args[0]
        image_link = "[2]: https://s.yimg.com/uu/api/res/1.2/r2_zN5_cWprvslSqTT.njw--~B" \
                     "/aD0xNzg5O3c9MjY4MzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org" \
                     "/dcbad8ec369d25ebf86d76f5170c8e76 (image)\n"
        self.assertEqual(message_head, "\nFeed: Yahoo News - Latest News & Headlines")
        self.assertEqual(news_title, "\nTitle: Retired cop put in chokehold takes police case to high court")
        self.assertEqual(mock_print.call_args_list[6].args[0], image_link)

    @patch("builtins.print", autospec=True, side_effect=print)
    def test_limit_really_limit_one(self, mock_print):
        # Test number of output lines is equal limit * 6 (number of lines in one news WITHOUT logs no json)
        rs.printing_parsing_news(td.TEST_NEWSDICT, 1)
        news = mock_print.call_args_list
        self.assertEqual(len(news), (1 * 6) + 1)

    @patch("builtins.print", autospec=True, side_effect=print)
    def test_limit_really_three(self, mock_print):
        # Test number of output lines is equal limit * 6 (number of lines in one news WITHOUT logs no json)
        rs.printing_parsing_news(td.TEST_NEWSDICT, 3)
        news = mock_print.call_args_list
        self.assertEqual(len(news), (3 * 6) + 1)

    # Tests for function "printing_news_in_json"
    @patch("builtins.print", autospec=True, side_effect=print)
    def test_printing_parsing_news_in_json(self, mock_print):
        # Test output have the first key of our json dictionary ("source"), which is not present in the regular output
        rs.printing_news_in_json(td.TEST_NEWSDICT, 1)
        first_row = mock_print.call_args_list[0].args[0]
        self.assertTrue("source" in first_row)

    # Tests for function "set_limit"
    def test_limit_is_not_passed(self):
        # Test case user do not pass any limit
        len_news = 7
        limit = None
        number_of_news_to_show = rs.set_limit(len_news, limit)
        self.assertEqual(number_of_news_to_show, len_news)

    def test_limit_is_small(self):
        # Test case user pass limit that smaller than total number of news (3)
        len_news = 7
        limit = 2
        number_of_news_to_show = rs.set_limit(len_news, limit)
        self.assertEqual(number_of_news_to_show, 2)

    def test_limit_is_big(self):
        # Test case user pass limit that bigger than total number of news (3), should set number_of_news_to_show as
        # maximum, means len(content.entries)
        len_news = 7
        limit = 100500
        number_of_news_to_show = rs.set_limit(len_news, limit)
        self.assertEqual(number_of_news_to_show, len_news)

    def test_limit_is_invalid(self):
        # Test case user pass 0 or negative int, should print user-friendly message and exit
        len_news = 7
        limit = -1
        with self.assertRaises(SystemExit):
            rs.set_limit(len_news, limit)

    # Test for function "make_news_dictionary"
    def test_made_newsdict(self):
        # Test all data from FeedParserDict parse correctly, including entries and especially images links
        content = mock.MagicMock()
        content.entries = td.TEST_ENTRIES
        content.feed.title = NEWSLINK
        content.feed.published = "Fri, 21 May 2021 12:51:18 -0400"
        source = "https://news.yahoo.com/rss/"
        newsdict = rs.make_news_dictionary(source, content)
        self.assertEqual(newsdict["source"], source)
        self.assertEqual(newsdict["main_title"], content.feed.title)
        self.assertEqual(newsdict["news"][0]["Title"], "On-duty police officer sexually assaulted by gas station "
                                                       "manager, Georgia cops say")
        self.assertEqual(newsdict["news"][0]["Image"], "https://s.yimg.com/uu/api/res/1.2/A3riyROEGQuSpO0M838c0g--~B"
                                                       "/aD02NDE7dz0xMTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com"
                                                       "/en/lexington_herald_leader_mcclatchy_articles_314"
                                                       "/d453d37647ec075638a8bc71a3e80ce0")
        self.assertEqual(newsdict["news"][1]["Title"], "Heroic Dog Who Lost Her Snout Saving Two Girls Years Ago "
                                                       "Passes Away in the Philippines")

    # Test for function "date_compare"
    def test_date_compare_true(self):
        # Pass two equal dates
        user_date = datetime.strptime("20210521", '%Y%m%d')
        self.assertTrue(rs.date_compare("Fri, 21 May 2021 12:51:18 -0400", user_date))

    def test_date_compare_false(self):
        # Pass two non equal dates
        user_date = datetime.strptime("20210521", '%Y%m%d')
        self.assertFalse(rs.date_compare("Fri, 21 February 2021 12:51:18 -0400", user_date))

    # Tests for function "parsing_user_date"
    @patch("builtins.print", autospec=True, side_effect=print)
    def test_invalid_date(self, mock_print):
        # Test ValueError was cached and user-friendly message is printing to stdout, if we give a bad date
        rs.parsing_user_date("12345")
        message = mock_print.call_args_list[0].args[0]
        self.assertEqual(message, "Invalid date, please insert date like '14100715'")

    @patch("builtins.print", autospec=True, side_effect=print)
    def test_no_cashed_news(self, mock_print):
        # Test AttributeError was cached and user-friendly message is printing to stdout, if we give a bad date
        with mock.patch("main_reader.rss_reader.find_cashed_news") as cashMock:
            cashMock.side_effect = AttributeError(mock.Mock)
            rs.parsing_user_date("20210101")
            message = mock_print.call_args_list[0].args[0]
            self.assertEqual(message, "No news from this date")

    def test_return_valid_cashed_dict_with_valid_len_news(self):
        # Test take newsdict from find_cashed_news, valid count it's len_news and return it
        with mock.patch("main_reader.rss_reader.find_cashed_news") as cashMock:
            cashMock = td.TEST_NEWSDICT
            newsdict, len_news = rs.parsing_user_date("20210521")
            self.assertEqual(len_news, len(newsdict["news"]))

    # Test for function "write_cash"
    def test_cash_writing(self):
        # Test our dict are in cash file
        rs.write_cash(td.TEST_NEWSDICT)
        cash_file_name = os.path.join(os.getcwd(), "cashed_news.txt")
        with open(cash_file_name, "r") as cash_file:
            lines = cash_file.readlines()
            last_line = lines[-1]
            check_dict = json.loads(last_line)
            self.assertEqual(check_dict, td.TEST_NEWSDICT)

    # Tests for function "find_cashed_news"
    def test_news_find_by_date_only(self):
        # Test for valid user date
        user_date = datetime.strptime("20210521", '%Y%m%d')
        self.assertTrue(rs.find_cashed_news(user_date))

    def test_news_find_by_date_and_link(self):
        # Test for valid user date and source
        user_date = datetime.strptime("20210521", '%Y%m%d')
        self.assertTrue(rs.find_cashed_news(user_date, source=NEWSLINK))

    def test_news_not_find_by_date_and_link(self):
        # Test for invalid user date and source - AttributeError is raising
        user_date = datetime.strptime("14100521", '%Y%m%d')
        with self.assertRaises(AttributeError):
            rs.find_cashed_news(user_date, source=NEWSLINK)


if __name__ == "__main__":
    unittest.main()