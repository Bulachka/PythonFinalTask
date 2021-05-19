"""
Main module. Receive input info from bash, parse it and print result to stdout.
"""

import argparse
import json as jsn
import logging
import logging.handlers
import sys
from urllib.error import URLError

import feedparser

NEWS_PARTS = ("title", "published", "summary", "description", "storyimage", "media_content", "link")


def set_logger(verbose):
    """
    Choose the output for logs and configure a logger
    :param verbose: If True, prints logs not to the file, but to stdout
    :return: configured logger
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), ] if verbose else [logging.FileHandler("logs.log"), ]
    )
    logger = logging.getLogger()
    return logger


def set_limit(content, limit):
    """
    Set how many numbers of new to print
    :param content: parsed link with rss news
    :param limit: user's parameter, that limit number of news to be printed;
    could be int or None (in case of None return value will be equal total number of news)
    :return: number of news to print or exit from the program, if limit <= 0
    """
    number_of_news_to_show = len(content.entries)
    if limit is not None:
        if limit <= 0:
            print("Please insert haw many news you want to read (more than 0)")
            sys.exit()
        elif limit <= len(content.entries):
            number_of_news_to_show = limit
    return number_of_news_to_show


def printing_parsing_news(content, number_of_news_to_show):
    """
    Print parsed news to bash
    :param content: parsed link with rss news
    :param number_of_news_to_show: limit number of news for parsing
    """
    print("\n" + content.feed.title + "\n")
    for news in content.entries[:number_of_news_to_show]:
        for item in NEWS_PARTS:
            if item in news.keys():
                print(item.capitalize() + ": " + str(news[item]))
        print("\n")


def printing_parsing_news_in_json(content, number_of_news_to_show):
    """
    Parse news to a dictionary, convert it to json format and print it to bash
    :param content: parsed link with rss news
    :param number_of_news_to_show: limit number of news for parsing
    """

    json_dict = {}
    newslist = []
    newsdict = {}

    for news in content.entries[:number_of_news_to_show]:
        for item in NEWS_PARTS:
            if item in news.keys():
                json_dict[item.capitalize()] = news[item]
        newslist.append(json_dict.copy())
    newsdict["news"] = newslist
    print(jsn.dumps(newsdict, indent=1))


def open_rss_link(source, verbose):
    """
    Receive link with RSS news and try to parse it, print logs
    :param source: link to take news
    :param verbose: choose place to print logs
    :return: parsed content from link. If now link, raise ValueError. If link is invalid, raise URLError
    """

    logger = set_logger(verbose)

    # Receive link and start parsing
    try:
        content = feedparser.parse(source)
        if not source:
            raise ValueError
        logger.info(f"Starting reading link {source}")
    except URLError as e:
        logger.error(f"Error {e} raised with trying to open link {source}")
        return print("Bad link, please try again")
    except ValueError as e:
        logger.error(f"Error {e} raised with trying to open link {source}")
        return print("Please insert rss link")

    return content


def parse_command_line_arguments():
    """
    :return: parsed arguments, received from command line
    """

    parser = argparse.ArgumentParser(description="Pure Python command-line RSS reader")
    parser.add_argument(
        "--version", action="version", version="Version 1.0.1", help="Print version info"
    )
    parser.add_argument("source", type=str, help="RSS URL")
    parser.add_argument(
        "--limit", type=int, help="Limit news topics if this parameter provided"
    )
    parser.add_argument(
        "--json", action="store_true", help="Print result as JSON in stdout"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Outputs verbose status messages"
    )
    arguments = parser.parse_args()
    return arguments


def main():
    """
    Receive parsed arguments, call functions to set logger and number of news to show, choose format
    for of news to print (json or not) and call valid function fpr printing, print logs.
    """

    arguments = parse_command_line_arguments()

    logger = set_logger(arguments.verbose)

    content = open_rss_link(arguments.source, arguments.verbose)

    number_of_news_to_show = set_limit(content, arguments.limit)

    if arguments.limit:
        logger.info(f"Would read only {arguments.limit} number of news")

    if arguments.json:
        logger.info(f"Convert news in json format")
        printing_parsing_news_in_json(content, number_of_news_to_show)
    else:
        printing_parsing_news(content, number_of_news_to_show)

    logger.info(f"End of reading")


if __name__ == "__main__":
    # Run the reader
    main()
