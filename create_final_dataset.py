import re
import csv
from collections import Counter

def extract_ending_entities(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entity_counter = Counter()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Regex for:
        # - two or more space-separated capitalized words
        # - or hyphenated/camelcase compound words (with 2+ components) where both parts are capitalized
        match = re.search(
            r'((?:[A-Z][a-z]+(?:[-][A-Z][a-z]+)*\s+){1,}[A-Z][a-z]+(?:[-][A-Z][a-z]+)*|[A-Z][a-z]+(?:[-][A-Z][a-z]+)+)$',
            line
        )

        if match:
            entity = match.group(1).strip()

            # Special handling for hyphenated words like Courier-Ok
            if '-' in entity and re.search(r'[A-Z][a-z]*-[A-Z][a-z]*', entity):
                entity_counter[entity] += 1
            elif '-' not in entity:
                entity_counter[entity] += 1

    common_entities = {k: v for k, v in entity_counter.items() if v >= 4}

    return common_entities


def load_file(file_path):
    """Load the contents of a text file and return it as a list of lines."""
    with open(file_path, 'r') as file:
        return file.readlines()


def extract_publications(no_file_path):
    """Extract publication names from no.txt (before the ':' and number)."""
    publications = []
    with open(no_file_path, 'r') as file:
        for line in file:
            match = re.match(r"([a-zA-Z\s\-]+):\s*\d+", line)  # Matches publication name before the colon and number
            if match:
                publications.append(match.group(1).strip().lower())  # Add to list, converted to lowercase
    return publications


def remove_publication_names(line, publications):
    """Remove any occurrence of publication names from the line."""
    for pub in publications:
        # Replace the publication name (case insensitive) with an empty string
        line = re.sub(r'\b' + re.escape(pub) + r'\b', '', line, flags=re.IGNORECASE)
    return line


def filter_lines(not_news_lines, publications):
    """Remove publication names from each line."""
    filtered_lines = []
    for line in not_news_lines:
        filtered_line = remove_publication_names(line, publications)
        filtered_lines.append(filtered_line)
    return filtered_lines


def write_to_csv(filtered_news_lines, filtered_not_news_lines, output_csv):
    """Write the lines from both files into a CSV with 'title' and 'news' columns."""
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['title', 'news'])
        
        for line in filtered_news_lines:
            writer.writerow([line.strip(), 1])  
        for line in filtered_not_news_lines:
            writer.writerow([line.strip(), 0]) 

    print(f"CSV file '{output_csv}' created successfully.")

def main():
    entities = extract_ending_entities('news.txt')
    sorted_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)
    for entity, count in sorted_entities:
        print(f"{entity}: {count}")

    not_news_lines = load_file('not_news.txt')
    publications = extract_publications('remove_from_not_news_titles.txt')
    filtered_not_news_lines = filter_lines(not_news_lines, publications)

    with open('not_news.txt', 'w') as file:
        file.writelines(filtered_not_news_lines)

    filtered_news_lines = load_file('news.txt')
    filtered_news_lines = filter_lines(filtered_news_lines, publications)

    write_to_csv(filtered_news_lines, filtered_not_news_lines, 'train.csv')


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
