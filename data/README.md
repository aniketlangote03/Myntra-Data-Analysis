# Dataset

## Source

Product listings scraped from **Myntra.com** — Men's Jeans category.

| File | Description | Records |
|------|-------------|---------|
| `myntra_dataset_ByScraping.csv` | Raw scraped data | 52,120 |
| `myntra_cleaned.csv` | After deduplication and discount cleaning | 31,527 |

## Collection Details

- **Category:** Men's Jeans
- **Collection method:** Web scraping of public product listing pages
- **Columns:** `brand_name`, `pants_description`, `price`, `MRP`, `discount_percent`, `ratings`, `number_of_ratings`

## Data Quality Notes

- No missing values in the raw dataset.
- **17,047 duplicate rows** removed during cleaning.
- **3,546 rows** with `discount_percent > 1` removed — these reflect an inconsistent scraper format (values 1.1–64.0) that cannot be reliably converted to decimal discounts.

## Usage

This dataset is provided for **educational and portfolio purposes only**. Use in accordance with Myntra's terms of service. Do not use for commercial scraping or redistribution without permission.

## Regenerating Clean Data

Run notebooks in order:

1. `notebooks/01_Data_Loading.ipynb`
2. `notebooks/02_Data_Quality_Assessment.ipynb`
3. `notebooks/03_Data_Cleaning.ipynb`

Notebook 3 exports `myntra_cleaned.csv`, which is used by notebooks 4–5, the dashboard, and chart scripts.
