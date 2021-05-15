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


def open_rss_link(source, limit, json, verbose):
    """
    Main function: receive link and params from bash, parse news and print them (and logs)
    :param source: link to take news
    :param limit: how many news tp return
    :param json: choose output format
    :param verbose: choose place to print logs
    :return: print news to stdout
    """

    # Receive link and start parsing
    try:
        content = feedparser.parse(source)
    except Exception:
        raise URLError("Bad link, please try again")

    if verbose:
        # Choose the output for logs and configure a logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout), ]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("logs.log"), ]
        )
    logger = logging.getLogger()

    logger.info(f"Starting reading link {source}")

    if limit and limit <= len(content.entries):
        # Set how many news to print
        logger.info(f"Would read only {limit} number of news")
        number_of_news_to_show = limit
    else:
        number_of_news_to_show = len(content.entries)

    if json:
        # Convert news to json format
        logger.info(f"Convert news in json format")
        json_dict = {}
        newslist = []
        newsdict = {}

        for news in content.entries[:number_of_news_to_show]:
            if "title" in news.keys():
                json_dict["Title"] = news.title

            if "summary" in news.keys():
                json_dict["Summary"] = news.summary

            if "description" in news.keys():
                json_dict["Summary"] = news.description

            if "published" in news.keys():
                json_dict["Date"] = news.published

            if "storyimage" in news.keys():
                json_dict["Main_image"] = news.storyimage

            if "media_content" in news.keys():
                json_dict["Image"] = news.media_content

            if "tags" in news.keys():
                if "term" in news.tags:
                    json_dict["Tags"] = news.tags[0]["term"]

            if "link" in news.keys():
                json_dict["News link"] = news.link

            newslist.append(json_dict.copy())

        newsdict["news"] = newslist

        print(jsn.dumps(newsdict, indent=1))

    else:
        # Print news to stdout
        for news in content.entries[:number_of_news_to_show]:
            if "title" in news.keys():
                print("\n")
                print(f"Title: {news.title}")

            if "published" in news.keys():
                print(f"Date: {news.published}")

            if "summary" in news.keys():
                print(f"Summary: {news.summary}")

            if "description" in news.keys():
                print(f"Summary: {news.description}")
                print("\n")

            if "storyimage" in news.keys():
                print("\n\n")
                print(f"Main_image: {news.storyimage}")

            if "media_content" in news.keys():
                print("\n\n")
                print(f"Image: {news.media_content}")

            if "tags" in news.keys():
                if "term" in news.tags:
                    print(f"Tags: {news.tags[0]}")

            if "link" in news.keys():
                print(f"Link: {news.link}")
                print("****************************************")

    logger.info(f"End of reading")


def main():
    # Parse arguments from command line
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
    argum = parser.parse_args()

    # Call main function with parsed arguments
    open_rss_link(argum.source, argum.limit, argum.json, argum.verbose)


if __name__ == "__main__":
    # Run the reader
    main()
