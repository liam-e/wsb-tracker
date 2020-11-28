import datetime as dt
import os
import sys
import markdown

os.chdir(sys.path[0])


def markdown_to_html(input_file):
    with open(input_file, "r") as f:
        return markdown.markdown(f.read())


def generate_sentiment_html(now, debug=False):
    with open("data/sentiment/html/sentiment_header_snippet.html", "r") as f:
        header_snippet = f.read()

    with open("data/sentiment/html/sentiment_footer_snippet.html", "r") as f:
        footer_snippet = f.read()

    root_path = "public_html/finance/res/img/sentiment"

    html_root_path = "../res/img/sentiment"

    html_content = f"\n<header>\n<h1>Reddit stock sentiment</h1>\n<p id='timestamp'>Last updated: {now.strftime('%A %d %B, %Y at %I:%M:%S %p')}</p>\n</header>\n"

    for root, subdirs, files in os.walk(root_path):
        for subdir in subdirs:
            subheading = " ".join(subdir.title().split("_"))
            html_content += f"\n<h3>{subheading}</h3>\n"
            for root2, subdirs2, files2 in os.walk(f"{root_path}/{subdir}"):
                for file in files2:
                    if file.startswith("current"):
                        img_path = f"{html_root_path}/{subdir}/{file}"
                        img_name = f"{subdir.title()} {img_path.split('_')[-2].title()} plot"
                        img_tag = f"<div class='imgbox'><img class='center-fit' src='{img_path}' alt='{img_name}'/></div>\n"
                        html_content += img_tag

    html = header_snippet + html_content + footer_snippet

    with open("public_html/finance/sentiment/index.html", "w") as f:
        if not debug:
            f.write(html)


def generate_ohlc_html(now, debug=False):
    with open("data/sentiment/html/ohlc_header_snippet.html", "r") as f:
        header_snippet = f.read()

    with open("data/sentiment/html/ohlc_footer_snippet.html", "r") as f:
        footer_snippet = f.read()

    root_path = "public_html/finance/res/img/ohlc"

    html_root_path = "../res/img/ohlc"

    html_content = f"\n<header>\n<h1>Daily Briefing</h1>\n<h2>Showing candlestick graphs for now.</h2>\n" \
                   f"<p id='timestamp'>Last updated: {now.strftime('%A %d %B, %Y at %I:%M:%S %p')}</p>\n</header>\n"

    for root, subdirs, files in os.walk(root_path):
        for subdir in subdirs:
            subheading = " ".join(subdir.title().split("_"))
            html_content += f"\n<h3>{subheading}</h3>\n"
            for root2, subdirs2, files2 in os.walk(f"{root_path}/{subdir}"):
                for file in files2:
                    img_path = f"{html_root_path}/{subdir}/{file}"
                    img_name = f"{subdir.title()} {img_path.split('_')[-2].title()} plot"
                    img_tag = f"<div class='imgbox'><img class='center-fit' src='{img_path}' alt='{img_name}'/></div>\n"
                    html_content += img_tag

    html = header_snippet + html_content + footer_snippet

    with open("public_html/finance/daily_briefing/index.html", "w") as f:
        if not debug:
            f.write(html)


if __name__ == "__main__":
    generate_sentiment_html(dt.datetime.now())
