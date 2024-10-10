#!/bin/bash
# The following script is a helper for generating a new Hugo post with the correct YAML front matter
# and placed into its correct directory. It prompts for the post title, author, tags, and category.

# Function to prompt for input with a default value
prompt() {
  local prompt_text=$1
  local default_value=$2
  read -p "$prompt_text [$default_value]: " input
  echo "${input:-$default_value}"
}

# Prompt for post details
title=$(prompt "Enter the post title" "New Post")
slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '-' | tr -cd '[:alnum:]-')
author=$(prompt "Enter the author(s)" "Author Name")
tags=$(prompt "Enter the tags (comma-separated)" "tag1, tag2")
category=$(prompt "Enter the category (analysis, context, methodologies, announcements)" "analysis")

# Validate category
case "$category" in
  analysis|context|methodologies|announcements)
    ;;
  *)
    echo "Invalid category. Please choose from analysis, context, methodologies, or announcements."
    exit 1
    ;;
esac

# Create the post directory based on the category
post_dir="content/$category/$slug"
mkdir -p "$post_dir"

# Create the index.md file with the YAML header
cat <<EOF > "$post_dir/index.md"
---
title: "$title"
slug: "$slug"
date: $(date +"%Y-%m-%dT%H:%M:%S%z")
author: "$author"
tags: [$(echo "$tags" | sed 's/,/, /g')]
category: "$category"
---
EOF

echo "New post created at $post_dir/index.md"