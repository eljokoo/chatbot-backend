import asyncio
import pprint

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re

# Some inspiration and code from https://github.com/trancethehuman/entities-extraction-web-scraper - amazing tutorial


def remove_unwanted_tags(html_content, unwanted_tags=["script", "style"]):
    """
    This removes unwanted HTML tags from the given HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()

    return str(soup)

def get_part_links(html_content):
    """
    This function extracts all the part links from the given HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return str(soup.find_all("a", {"class": "nf__part__detail__title"}))


def extract_tags(html_content, tags: list[str]):
    """
    This takes in HTML content and a list of tags, and returns a string
    containing the text content of all elements with those tags, along with their href attribute if the
    tag is an "a" tag.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text_parts = []
    img = ""

    for tag in tags:
        elements = soup.find_all(tag)
        for element in elements:
            # If the tag is an image, append its src and alt text
            if tag == "img":
                src = element.get('src')
                alt = element.get('alt', '').strip()
                if src:
                    if alt:
                        text_parts.append(f"{alt} ({src})")
                    else:
                        text_parts.append(src)
            elif tag == "a" and element.get('id') == "MagicZoom-PartImage-Images":
                img = element.get('href')  
            else:
                text_parts.append(element.get_text())

    return ' '.join(text_parts), img


def remove_unessesary_lines(content):
    # Split content into lines
    lines = content.split("\n")

    # Strip whitespace for each line
    stripped_lines = [line.strip() for line in lines]

    # Filter out empty lines
    non_empty_lines = [line for line in stripped_lines if line]

    # Remove duplicated lines (while preserving order)
    seen = set()
    deduped_lines = [line for line in non_empty_lines if not (
        line in seen or seen.add(line))]

    # Join the cleaned lines without any separators (remove newlines)
    cleaned_content = "".join(deduped_lines)

    return cleaned_content


async def ascrape_playwright(url, tags: list[str] = ["h1", "h2", "h3", "span"]) -> str:
    """
    An asynchronous Python function that uses Playwright to scrape
    content from a given URL, extracting specified HTML tags and removing unwanted tags and unnecessary
    lines. This is used for the individual part websites.
    """
    print("Started scraping...")
    results = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=False, args=['--start-maximized'], slow_mo=1000)
        try:
            context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36")
            page = await context.new_page()
            await page.goto(url)

            page_source = await page.content()

            text, img = extract_tags(remove_unwanted_tags(
                page_source), tags)

            results = remove_unessesary_lines(text)
            # print("Content scraped")
            # print("Results are these\n", results)
        except Exception as e:
            results = f"Error: {e}"
        await browser.close()
    return results, img


async def ascrape_brand_part_websites(url: str, appliance_name: str):
    """
    This function scrapes the brand part websites from the general appliance part website.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=False, args=['--start-maximized'], slow_mo=1000)
        try:
            context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36")
            page = await context.new_page()
            await page.goto(f"{url}{appliance_name}-Parts.htm")

            page_source = await page.content()

            print(page_source, "page source")

            results = remove_unessesary_lines(extract_tags(remove_unwanted_tags(
                page_source), ["a"]))
            print("Content scraped")
        except Exception as e:
            results = f"Error: {e}"
        await browser.close()

    print(results, "results are these")

    # Extract all substrings that start with '(' and end with ')'
    results = re.findall(rf'\((/[^)]+?-{appliance_name}-Parts\.htm)\)', results)

    print(results, "results are these filtered")
    
    return results

async def ascrape_brand_part_websites_links(url: str, appliance_name: str, brand_name: str):
    """
    This function scrapes the links of the specific types of parts of a certain brand for a certain appliance.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=False, args=['--start-maximized'], slow_mo=1000)
        try:
            context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36")
            page = await context.new_page()
            await page.goto(f"{url}{brand_name}-{appliance_name}-Parts.htm")

            page_source = await page.content()

            results = remove_unessesary_lines(extract_tags(remove_unwanted_tags(
            page_source), ["a"]))
            print("Content scraped")
        except Exception as e:
            results = f"Error: {e}"
        await browser.close()

    # print(results, "results are these")

    # Extract all substrings that start with '(' and end with ')'
    results = re.findall(rf'\((\/{brand_name}-{appliance_name}-(?![^)]*Models)[^)]+?\.htm)\)', results)

    print(results, "results are these filtered")

    return results

async def ascrape_part_websites(url: str):
    """
    This function scrapes the websites of the parts listed on a given url.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=False, args=['--start-maximized'], slow_mo=1000)
        try:
            context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36")
            page = await context.new_page()
            await page.goto(url)

            page_source = await page.content()

            part_links = extract_tags(get_part_links(page_source), ["a"])

            results = re.findall(rf'\((\/[^)?]+)(?:\?[^)]+)?\)', part_links)
        except Exception as e:
            results = f"Error: {e}"
        await browser.close()

    print(results, "results are these")

    return results

async def ascrape_part_websites_links(url: str, appliance_name: str):
    """
    This function scrapes the all the websites of all the parts for a certain appliance by using the above helper functions.
    """
    brand_parts = await ascrape_brand_part_websites(url, appliance_name)

    part_links = []
    for brand_part in brand_parts:
        brand_name = brand_part[1:].split(f"-{appliance_name}-Parts.htm")[0]

        brand_part_links = await ascrape_brand_part_websites_links(url, appliance_name, brand_name)

        if len(brand_part_links) == 0:
            part_links.append(await ascrape_part_websites(f'{url}{brand_name}-{appliance_name}-Parts.htm'))
            print(brand_name, part_links, "part links are these")
            continue

        for brand_part_link in brand_part_links:
            part_links.append(await ascrape_part_websites(f'{url}{brand_part_link}'))
            print(brand_name, part_links, "part links are these")

    # Write the part links to a file
    with open(f"{appliance_name}-part-links.txt", "w") as text_file:
        text_file.write(str(part_links))

# TESTING
if __name__ == "__main__":
    async def ascrape_routine():
        await ascrape_part_websites_links("https://www.partselect.com/", "Fridge")
        await ascrape_part_websites_links("https://www.partselect.com/", "Dishwasher")

    pprint.pprint(asyncio.run(ascrape_routine()))
