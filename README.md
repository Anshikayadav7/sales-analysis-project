# Sales Performance Analysis

A Python data analysis project on the Superstore sales dataset (9,994 order lines, January 2014 to December 2017). It cleans the data, calculates sales and profit insights, and produces charts for revenue, product performance and monthly trends. An interactive dashboard is included, and the cleaned CSV can be loaded straight into Power BI.

**Tools:** Python, Pandas, NumPy, Matplotlib, Power BI (optional)

## Project structure

```
sales-analysis-project/
├── sales_analysis.py            # main script: clean, analyse, chart
├── requirements.txt             # Python dependencies
├── README.md
├── data/
│   ├── raw/Sample - Superstore.csv      # original dataset
│   └── processed/sales_clean.csv        # cleaned output (created by the script)
├── outputs/
│   ├── insights.md              # insights calculated from the data
│   └── charts/                  # 8 PNG charts
└── dashboard/
    └── sales_dashboard.html     # interactive dashboard (open in a browser)
```

## How to run

1. Install Python 3.9 or newer.
2. Open a terminal in the project folder.
3. (Recommended) create a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:  .venv\Scripts\activate
   # macOS/Linux:  source .venv/bin/activate
   ```
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the analysis:
   ```bash
   python sales_analysis.py
   ```
   To use a different copy of the Superstore CSV:
   ```bash
   python sales_analysis.py --input "path/to/file.csv"
   ```

The script prints the insights in the terminal and writes `data/processed/sales_clean.csv`, `outputs/insights.md` and the charts in `outputs/charts/`.

## What the script does

1. **Loads and validates** the CSV, with a clear error if the file or required columns are missing.
2. **Cleans the data:** removes duplicates, parses dates, standardises text, formats postal codes, and checks numeric columns.
3. **Adds derived columns:** ship days, year, month, profit margin and discount band.
4. **Calculates insights** for revenue, profit, categories, regions, segments, products and discounts.
5. **Creates charts** and saves them as PNG files.

The dataset was already clean (no missing values or duplicates), so the cleaning step is light.

## Key findings

All figures are calculated from the data by the script (see `outputs/insights.md`).

- **Overview:** $2.30M in sales and $286,397 in profit (12.5% margin) from 5,009 orders and 793 customers, Jan 2014 to Dec 2017.
- **Yearly sales (growth vs previous year):** 2014: $484,247; 2015: $470,533 (-2.8%); 2016: $609,206 (+29.5%); 2017: $733,215 (+20.4%).
- **Seasonality:** best month was Nov 2017 ($118,448), weakest was Feb 2014 ($4,520). October to December brings 38% of all sales.
- **Categories:** Technology $836,154 sales, 17.4% margin; Furniture $742,000 sales, 2.5% margin; Office Supplies $719,047 sales, 17.0% margin.
- **Weakest category by margin:** Furniture at 2.5%, against 17.4% for Technology.
- **Regions:** West $725,458 sales, 14.9% margin; East $678,781 sales, 13.5% margin; Central $501,240 sales, 7.9% margin; South $391,722 sales, 11.9% margin.
- **Segments:** Consumer $1.16M sales, 11.5% margin; Corporate $706,146 sales, 13.0% margin; Home Office $429,653 sales, 14.0% margin.
- **Loss-making sub-categories:** Tables (-$17,725 profit on $206,966 sales); Bookcases (-$3,473 profit on $114,880 sales); Supplies (-$1,189 profit on $46,674 sales).
- **Most profitable sub-categories:** Copiers ($55,618); Phones ($44,516); Accessories ($41,937).
- **Profit margin by discount level:** No discount: 29.5%; 1-20%: 11.9%; 21-40%: -15.3%; Over 40%: -77.4%.
- **Heavy discounting:** 13.9% of order lines were discounted by more than 20%, and together they made -$135,376 in profit on $362,770 in sales.
- **Top 5 products by sales:** Canon imageCLASS 2200 Advanced Copier ($61,600); Fellowes PB500 Electric Punch Plastic Comb Binding Machine with Manual Bind ($27,453); Cisco TelePresence System EX90 Videoconferencing Unit ($22,638); HON 5400 Series Task Chairs for Big and Tall ($21,871); GBC DocuBind TL300 Electric Binding System ($19,823).
- **Top 5 products by profit:** Canon imageCLASS 2200 Advanced Copier ($25,200); Fellowes PB500 Electric Punch Plastic Comb Binding Machine with Manual Bind ($7,753); Hewlett Packard LaserJet 3310 Copier ($6,984); Canon PC1060 Personal Laser Copier ($4,571); HP Designjet T520 Inkjet Large Format Printer - 24" Color ($4,095).
- **5 biggest loss-making products:** Cubify CubeX 3D Printer Double Head Print (-$8,880); Lexmark MX611dhe Monochrome Laser Printer (-$4,590); Cubify CubeX 3D Printer Triple Head Print (-$3,840); Chromcraft Bull-Nose Wood Oval Conference Tables & Bases (-$2,876); Bush Advantage Collection Racetrack Conference Table (-$1,934).
- **Product breadth:** 301 of 1,850 products lost money overall.

## Charts

| Chart | File |
|---|---|
| Revenue by year | `outputs/charts/01_revenue_by_year.png` |
| Monthly sales trend | `outputs/charts/02_monthly_sales_trend.png` |
| Seasonality by year | `outputs/charts/03_seasonality_by_year.png` |
| Sales and profit by category and region | `outputs/charts/04_sales_profit_category_region.png` |
| Top 10 products by sales and profit | `outputs/charts/05_top_products.png` |
| Profit by sub-category | `outputs/charts/06_profit_by_subcategory.png` |
| Profit margin by discount level | `outputs/charts/07_discount_vs_margin.png` |
| Profit heatmap, region by category | `outputs/charts/08_profit_heatmap.png` |

![Monthly sales trend](outputs/charts/02_monthly_sales_trend.png)
![Profit margin by discount level](outputs/charts/07_discount_vs_margin.png)

## Power BI

Load `data/processed/sales_clean.csv` with Get Data > Text/CSV and build visuals from it: a line chart of sales by month, bar charts by category and region, KPI cards, and slicers for year, region, category and segment.

## Notes and limitations

- The dataset is a well-known sample dataset, not data from a real company.
- Findings describe patterns in this data only. Discount effects show association, not proven cause.
- `dashboard/sales_dashboard.html` loads Chart.js from a CDN, so it needs an internet connection.
