import json
import re
import os

input_base_dir = "dataset"
news_output_path = "news_titles.txt"
non_news_output_path = "non_news_titles.txt"

news_titles = []
non_news_titles = []

def clean_title(title, extracted_from, media_name, top_k_domain_names):

    for source in extracted_from:
        if source:
            title = re.sub(re.escape(source.strip()), '', title, flags=re.IGNORECASE).strip()

    if media_name:
        title = re.sub(re.escape(media_name), '', title, flags=re.IGNORECASE).strip()

    for domain in top_k_domain_names:
        if domain:
            title = re.sub(re.escape(domain), '', title, flags=re.IGNORECASE).strip()

    return title

def has_fewer_than_three_words(title):
    return len(title.split()) < 4


for root, dirs, files in os.walk(input_base_dir):
    if root == input_base_dir:
        continue

    news_titles = []
    non_news_titles = []

    jsonl_files = [os.path.join(root, f) for f in files if f.endswith(".jsonl")]
    for file_path in jsonl_files:
        with open(file_path, "r", encoding="utf-8") as infile:
            for line_number, line in enumerate(infile, 1):
                try:
                    item = json.loads(line)
                    is_news = item.get("is_news_article", False)

                    links = item.get("source_metadata", {}).get("links", [])
                    extracted_from = item.get("media-metadata", {}).get("extracted-from", "").split(",") if item.get("media-metadata") else []
                    raw_top_k_domains = item.get("source_metadata", {}).get("stats", {}).get("domain_dist", {}).get("top_k_domains", [])
                    top_k_domain_names = [d[0].strip() for d in raw_top_k_domains if isinstance(d, list) and len(d) > 0]

                    media_name = item.get("media_name", "")
                    if not isinstance(links, list):
                        continue

                    for link in links:
                        title = link.get("title", "").strip()

                        if "https://" in title:
                            title = title.split("https://")[0].strip()
                        if "http://" in title:
                            title = title.split("http://")[0].strip()
                        if "..." in title:
                            title = title.split("...")[0].strip()
                        if "|" in title:
                            title = title.split("|")[0].strip()
                        if " - " in title:
                            title = title.split(" - ")[0].strip()

                        title = clean_title(title, extracted_from, media_name, top_k_domain_names)

                        if has_fewer_than_three_words(title):
                            continue

                        if title:
                            if is_news:
                                news_titles.append(title)
                            else:
                                non_news_titles.append(title)

                except json.JSONDecodeError:
                    continue

    folder_name = os.path.basename(root)
    news_output_folder_path = os.path.join(input_base_dir, folder_name, "news.txt")
    non_news_output_folder_path = os.path.join(input_base_dir, folder_name, "not_news.txt")
    news_titles = set(news_titles)
    non_news_titles = set(non_news_titles)

    common_titles = news_titles.intersection(non_news_titles)

    news_titles -= common_titles
    non_news_titles -= common_titles
    os.makedirs(os.path.dirname(news_output_folder_path), exist_ok=True)
    os.makedirs(os.path.dirname(non_news_output_folder_path), exist_ok=True)

    with open(news_output_folder_path, "w", encoding="utf-8") as f:
        f.write("\n".join(news_titles))

    with open(non_news_output_folder_path, "w", encoding="utf-8") as f:
        f.write("\n".join(non_news_titles))

    print(f"\n✅ Done processing folder: {folder_name}")
    print(f"News article titles: {len(news_titles)} saved to '{news_output_folder_path}'")
    print(f"Non-news article titles: {len(non_news_titles)} saved to '{non_news_output_folder_path}'")

