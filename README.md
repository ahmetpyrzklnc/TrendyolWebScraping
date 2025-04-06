# Trendyol Milla Scraper

A web scraper developed to automatically download product images from Trendyol Milla store.

## Categories and Links

### 1. Pants Category
- **URL**: https://www.trendyol-milla.com/sr?wb=143760,101476,148061,103500,165523,103124&lc=70&qt=trendyolmilla&st=trendyolmilla&os=1
- **Total Pages**: 39
- **Image Directory**: `scraped_images_trendyol_pants`

### 2. Jeans Category
- **URL**: https://www.trendyol-milla.com/sr?wb=101476,103500,165523,143760,148061&lc=120&qt=trendyolmilla&st=trendyolmilla&os=1
- **Total Pages**: 30
- **Image Directory**: `scraped_images_trendyol_jeans`

### 3. Shirts Category
- **URL**: https://www.trendyol-milla.com/sr?wb=101476,103500,143760,148061,165523,103124&lc=75&qt=trendyolmilla&st=trendyolmilla&os=1
- **Total Pages**: 48
- **Image Directory**: `scraped_images_trendyol_shirts`

## Features

- Separate image storage directories for each category
- Automatic page navigation
- Download all images from product detail pages
- Automatic thumbnail clicking and image downloading
- Error handling and retry mechanisms
- Anti-bot detection features

## Requirements

- Python 3.x
- Selenium WebDriver
- Chrome browser
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the project:
```bash
git clone [repo-url]
cd trendyolMilla
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install Chrome WebDriver and add it to PATH

## Usage

To run the script for each category:

```bash
python trendyol_scraper.py
```

The script automatically:
1. Scrapes all pages in the specified category
2. Opens each product's detail page
3. Downloads all images
4. Saves downloaded images to category-specific directories

## Notes

- Do not close the browser while the script is running
- Ensure you have a stable internet connection
- Run separately for each category
- The script automatically retries in case of errors

## License

This project is licensed under the MIT License. See the `LICENSE` file for details. 