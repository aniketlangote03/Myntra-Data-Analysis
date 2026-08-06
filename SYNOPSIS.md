# Project Synopsis: Myntra Men's Jeans Data Analysis

An end-to-end data analytics project focused on analyzing Myntra's men's jeans product catalog to uncover pricing strategies, brand performance, promotional discount structures, and customer engagement patterns.

---

## 1. Project Overview & Objective

* **Business Objective:** Transform raw, scraped product listings of men's jeans on Myntra into actionable business intelligence. The goal is to optimize pricing structures, design effective discount campaigns, identify high-performing brand partners, and maximize customer engagement/satisfaction.
* **Core Analytics Pipeline:** Spanned data loading, data quality assessment, robust cleaning (handling duplicates/format errors), Exploratory Data Analysis (EDA), advanced composite scoring models, and interactive dashboard engineering.

---

## 2. Dataset & Features

* **Data Source:** Web scraped catalog listings of men's jeans on Myntra.
* **Volume:** 
  * **Raw Records:** 52,120 products
  * **Cleaned Records:** 31,527 products (371 unique brands)
* **Features Analysed:**
  1. `brand_name` (Categorical): Brand name of the jeans.
  2. `pants_description` (Categorical): Title / product catalog description.
  3. `price` (Numerical): Final discounted selling price in Indian Rupees (₹).
  4. `MRP` (Numerical): Maximum Retail Price in Indian Rupees (₹).
  5. `discount_percent` (Numerical): Discount percentage represented as a decimal (0.0 to 1.0).
  6. `ratings` (Numerical): Average customer rating on a scale of 1.0 to 5.0.
  7. `number_of_ratings` (Numerical): Total count of customer reviews/ratings.

---

## 3. Modular Notebook-by-Notebook Pipeline

The project is structured into **five sequential Jupyter Notebooks** located in the `notebooks/` directory:

### Notebook 1: Data Loading (`01_Data_Loading.ipynb`)
* Established directory paths and successfully loaded the raw dataset from `data/myntra_dataset_ByScraping.csv`.
* Performed initial inspection of the DataFrame size (52,120 rows, 7 columns), column data types, and high-level summaries.

### Notebook 2: Data Quality Assessment (`02_Data_Quality_Assessment.ipynb`)
* Inspected for missing values (none found) and identified data quality issues.
* Uncovered **17,047 exact duplicates** resulting from scraping overlap.
* Identified format anomalies in `discount_percent` where values exceeded `1.0` (e.g., raw percent numbers instead of decimals) due to scraper inconsistency.
* Highlighted significant price outliers to be examined.

### Notebook 3: Data Cleaning (`03_Data_Cleaning.ipynb`)
* Removed the 17,047 exact duplicate rows (reducing dataset to 35,073 rows).
* Removed 3,546 records with faulty discount formats (discount percent > 1.0), yielding a final, high-integrity dataset of **31,527 records**.
* Validated and cast data types, saving the clean output to `data/myntra_cleaned.csv`.

### Notebook 4: Exploratory Data Analysis (`04_Exploratory_Data_Analysis.ipynb`)
* Conducted descriptive statistical analysis showing:
  * **Average Price:** ₹1,697 | **Median Price:** ₹1,484 (right-skewed distribution).
  * **Core Catalog Range:** 50% of the products are priced in the mid-range of ₹899 to ₹1,829.
  * **Customer Satisfaction:** High overall average rating of 3.98/5.
* Explored brand listing volume and brand engagement. Identified **Roadster**, **HIGHLANDER**, and **United Colors of Benetton** as engagement leaders.
* Categorized catalog into price segments: Budget (≤ ₹1,000), Mid-Range (₹1,001–2,000), Premium (₹2,001–4,000), and Luxury (> ₹4,000).

### Notebook 5: Advanced Business Insights (`05_Advanced_Business_Insights.ipynb`)
* Formulated and computed composite scores to rank brands objectively (applied to brands with ≥ 20 products for statistical reliability):
  1. **Value Score:** A weighted metric highlighting high-quality, competitively priced, and discounted brands.
  2. **Business Performance Score:** A holistic metric combining rating, engagement volume, value score, and discount depth.
* Evaluated discount strategies and identified the mid-price segment as the key driver of both catalog volume and customer engagement.

---

## 4. Key Scoring Methodologies

To rank brands objectively, composite scoring models were built using Min-Max Normalization:

### A. Value Score Formula
Designed to find brands that deliver the best combination of quality and affordability.
$$\text{Value Score} = (0.40 \times \text{Rating Score}) + (0.30 \times \text{Discount Score}) + (0.30 \times \text{Price Score})$$
* *Rating Score:* $\frac{\text{avg\_rating}}{\max(\text{avg\_rating})}$
* *Discount Score:* $\frac{\text{avg\_discount}}{\max(\text{avg\_discount})}$
* *Price Score:* $\frac{\min(\text{avg\_price})}{\text{avg\_price}}$ (rewards lower average price)

### B. Business Performance Score Formula
Designed to rank brand value for merchandising prioritization:
* **Average Rating (Normalized):** 35% weight
* **Ratings per Product (Normalized):** 30% weight (engagement efficiency)
* **Value Score (Normalized):** 20% weight
* **Average Discount (Normalized):** 15% weight

---

## 5. Main Findings & Actionable Answers

* **Q: Which brands offer the best Value for Money?**
  * **A:** MarvelQ, AngelFab, Metronaut, SZN, and HARDSODA lead the Value Score. They provide high satisfaction and attractive discounts without inflating the price.
* **Q: Which brands dominate customer engagement?**
  * **A:** **Roadster** dominates total review volume (high catalog volume), whereas **HIGHLANDER** leads in engagement efficiency (highest reviews/ratings count per product listing).
* **Q: What is the optimal price segment?**
  * **A:** The **Mid-Price Segment (₹1,001–₹2,000)** is the core of Myntra's catalog, containing the highest count of listings and capturing the vast majority of customer reviews.
* **Q: Which brands should Myntra prioritize?**
  * **A:** **HIGHLANDER**, **HARDSODA**, **Sztori**, and **THE BEETEL HOUSE** score highest on the Business Performance Score, representing the highest partnership potential.

---

## 6. Deliverables & Interactive Dashboards

1. **Interactive HTML Dashboard (`dashboard/index.html`):** 
   * A standalone web page powered by Plotly.js and a Python-transformed dataset (`dashboard_data.json`).
   * Displays 7 live KPIs, price/discount distributions, scatter plots of 2,000 sampled items, and sortable brand ranking tables.
2. **Streamlit App Dashboard (`dashboard/app.py`):**
   * Real-time dashboard with sidebar filters allowing users to filter by price range, brand product thresholds, and scoring metrics.
3. **Power BI Dashboard Concept:**
   * Executive reporting design for stakeholders.
4. **Automated Document Generator (`reports/generate_deliverables.py`):**
   * Python automation script generating a 7-section MS Word Report (`Myntra_Data_Analysis_Report.docx`), an Executive PDF Export, and a structured slide presentation (`Myntra_Data_Analysis_Presentation.pptx`).

---

## 7. Strategic Recommendations

1. **Leverage Performance Leaders:** Prioritize HIGHLANDER, HARDSODA, and Sztori for homepage banners, curated collections, and joint-marketing promotions.
2. **Optimize Mid-Price Core:** Expand inventory and variety within the ₹1,001–2,000 price range, as it represents the highest customer demand and participation.
3. **Re-evaluate Premium Discounting:** Focus premium jeans promotions on "exclusivity" and "superior fit" rather than heavy discount cuts (which erode luxury brand equity).
4. **Benchmark via Value Leaders:** Study supply chain and pricing of Value Score leaders (MarvelQ, AngelFab) to replicate affordable-yet-high-satisfaction models.
