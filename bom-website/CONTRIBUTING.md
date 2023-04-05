# CONTRIBUTING

This is not a conventional CONTRIBUTING file and is intended to provide documentation for the Death by Numbers team adding or editing content on the website. If you are an external collaborator wishing to contribute to the project, please reach out to the PI Jessica Otis.

## Blog posts

These instructions are primarily about moving text from Google Docs to GitHub. **It is not recommended to draft your posts entirely in GitHub: there is no auto-saving or undoing.** If you are writing everything in Markdown, the process will be a bit more straightforward. If so, there are many Markdown editors available for Microsoft, Google, and Apple devices, including web-based editors.

Quick links: 

- [Markdown syntax guide](https://markdownguide.org)
- [Death by Numbers website](https://deathbynumbers.org)
- [Images folder](https://github.com/chnm/bom/tree/main/bom-website/static/images)
- [Blog posts folder](https://github.com/chnm/bom/tree/main/bom-website/content/blog)

To create a new blog post, the following steps will get you going: 

1. Create a new branch. There are multiple ways to do this, but the easiest is to navigate to the `content/blog/` folder. Then, in the upper-left in the dropdown that says `main`, click the dropdown and in the text box that appears fill out a name for the branch. Keep the name all lowercase and place dashes where you might include spaces. 

![Adding a branch.](/docs/new_branch.png)

2. Before adding your post, make sure to grab the YAML header for the post. You can use any existing YAML from a post, or use the following template: 

```yaml
---
title: ""
date: ""
author: 
	- fname lname
tags: 
	- tag1
	- tag2
categories: 
	- category
---
```

1. After the branch exists, you can add files. From the `content/blog` folder, select either "Add new file" or "Upload file" from the upper-right. If you add a new file, GitHub will open a simple text editor for you to work in.
2. First, provide a file name in the top line. The file name should follow the convention `YYYY-MM-DD-short-title.md`, where the date appears as YEAR-MONTH-DAY. If MONTH or DAY is a single integer, it should include a leading zero (e.g., April will be `04`, September will be `09`, the sixth day of a month will be `06`, and so on). 

![Creating new files.](/docs/new_file.png)

3. Add your YAML block at the top of the document. Fill in the appropriate values for each metadata item. Remember you can consult the [website](https://deathbynumbers.org/blog/) for a list of current tags and categories.
4. Copy your text over from the document you drafted your original post. Paste this into the Github text editor. You may need to turn on "soft wrap" from the dropdown in the upper-right of the document editor. Double check your paragraph spacing and ensure the Markdown formatting is correct throughout the document. Refer to [this Markdown documentation]() for information about markdown formatting.

![Docuemnt editing.](/docs/creating-editing.png)

5. Commit the document by navigating to "Commit new file" on the bottom of the page. GitHub will ask you for a short commit message (you can ignore the long description text field), double-check that you're committing to the correct branch, and then select "Commit new file." 

![Committing files.](/docs/committing.png)

6. If you need to edit a post, navigate to the post file in `content/blog` and select the pencil icon in the far upper-right. GitHub will open the text editor and you will follow the same steps in (5) to commit the changes. 

### Including Images

If your post includes an image, you'll use the Hugo short code `figure` to embed these. Copy and paste the following template for inserting figures: 

```html
{{< figure sec="/images/" caption="" alt="" >}}
```

Images can be uploaded directly from GitHub by dragging-and-dropping the image into the `bom-website/static/images` folder. When you add an image, GitHub will follow the same commit path that you used for creating a document and ask for a commit message. Note that the file name cannot be changed when you drop it in to upload, so be sure that you've renamed your file on your desktop before uploading. 

Once your image is uploaded, navigate back to your blog post in `content/blog`, select the pencil icon to edit the document, and paste in the figure shortcode above. Add the name of your image file after the `/image/` in `src`, and add a caption and alt text. Caption text will appear below the image in the post, and alt text will be for accessibility. Please be as descriptive as possible with the alt text.

When you think your post is ready to preview on the development site, ping @hepplerj on Slack.

## Submitting Issues

Enhancements, bugs, and other tasks related to the website are tracked on [GitHub Issues](https://github.com/chnm/bom/issues). You should feel free to create Issues at will.
