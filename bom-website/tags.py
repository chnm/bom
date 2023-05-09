#!/usr/bin/env python3 

# Usage:
#   python3.11 tags.py

import os
import yaml
from collections import defaultdict, OrderedDict

def parse_markdown_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        # Assuming YAML front matter is enclosed between '---' lines
        yaml_content = content.split('---')[1]
        metadata = yaml.safe_load(yaml_content)
        return metadata.get('tags', [])

def get_files_with_extension(directory, extension):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_list.append(os.path.join(root, file))
    return file_list

def count_tags(directory):
    tags = defaultdict(list)
    files = get_files_with_extension(directory, '.md')
    
    for file_path in files:
        tags_in_file = parse_markdown_file(file_path)
        for tag in tags_in_file:
            tags[tag].append(file_path)

    sorted_tags = OrderedDict(sorted(tags.items(), key=lambda t: t[0]))  # Sort tags alphabetically

    return sorted_tags

def display_tags(tags):
    print("Tags:")
    for tag, files in tags.items():
        print(f"Tag: {tag} (Count: {len(files)})")
        print("Posts:")
        for file_path in files:
            print(f"- {file_path}")
        print()

# Directory path where the markdown files are located
directory = 'content/blog/'
tags = count_tags(directory)
display_tags(tags)