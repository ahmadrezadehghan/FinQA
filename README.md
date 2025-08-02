
```markdown
# FinQA: Fine-Tuning GPT-3.5 for Structured Question Answering on Telegram Financial Data

This repository contains all code, data, and manuscript drafts for **FinQA**, a pipeline that  
1. Collects and normalizes high-frequency Telegram finance messages  
2. Clusters them into coherent subdomains  
3. Augments and fine-tunes GPT-3.5 for question answering  

---

## 📂 Repository Structure

```

web\_perper/
├── AhmadezaDehghanian\_Paper\_V1..V3.docx/.pdf   # Drafts of the manuscript
├── blockdiag.png                               # Architecture overview diagram
├── data gathering/                             # Telegram & news scraping + raw data
│   ├── fetch\_financial\_news\_2025.py
│   ├── telegramdata.py
│   └── processed\_telegram\_data\_normalizedV\*.xlsx
├── final.csv                                   # Consolidated dataset sample
├── mapbuilder.py                               # Geographic / network visualizations
├── normalizing/                                # Text-normalization scripts & outputs
│   ├── normalize.py
│   └── normalized\_output.xlsx
├── normal\_merged/                              # Post-normalization merge scripts
│   └── merge\_all\_python.py
├── oldV/                                       # Legacy experiments and backups
│   └── synthetic\_qas\_\*.py
├── paper/                                      # Per-channel raw Excel exports
│   └── \*.xlsx
├── raw\_data\_excels/                            # Unprocessed channel exports
│   └── \*.xlsx
├── training/                                   # Train/test splits, EDA, fine-tuning code
│   ├── Clustered/                             # Stratified CSV splits by cluster
│   ├── EDA.py                                 # Exploratory data analysis
│   └── finetuning/                            # SFT JSONL prep & `finetune.py`
└── README.md                                   # ← You are here

````

---

## 🛠 Setup & Dependencies

All Python scripts were developed and tested with **Python 3.8+**. We recommend creating a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
````

Typical dependencies include:

* `pandas`, `numpy` — data tables
* `scikit-learn` — TF-IDF & K-Means clustering
* `openai` — supervised fine-tuning via API
* `matplotlib`, `seaborn` — plotting (EDA)
* `telethon` — Telegram data scraping
* `requests`, `beautifulsoup4` — optional news scraping

Add any missing packages to `requirements.txt`.

---

## 🚀 Reproducing the Pipeline

1. **Data Gathering**

   ```bash
   cd "data gathering"
   python fetch_financial_news_2025.py        # optional: pulls news headlines
   python telegramdata.py                     # scrapes Telegram channels
   ```

   Output: raw `.xlsx` and `.csv` exports in this folder.

2. **Normalization**

   ```bash
   cd ../normalizing
   python normalize.py --input ../data\ gathering/processed_telegram_data.xlsx \
                       --output normalized_output.xlsx
   ```

   Output: cleaned messages ready for clustering.

3. **Merging & Clustering**

   ```bash
   cd ../normal_merged
   python merge_all_python.py                 # merges normalized batches
   # then run your clustering notebook or script
   ```

4. **Data Augmentation & JSONL Prep**

   ```bash
   cd ../oldV
   python synthetic_qas_openai.py             # generate synthetic QA pairs
   ```

   Validate and combine with expert pairs, then convert to JSONL with your custom script.

5. **Fine-Tuning**

   ```bash
   cd ../training/finetuning
   python finetune.py --training_file file.jsonl \
                     --model gpt-3.5 \
                     --epochs 4 \
                     --lr 0.1
   ```

6. **Evaluation & EDA**

   ```bash
   cd ../training
   python EDA.py                               # generates figures under eda_outputs1/
   ```

---

## 📄 Manuscript & Figures

* Drafts: `AhmadezaDehghanian_Paper_V*.docx`
* Final PDF: `AhmadezaDehghanian_Paper_V3.pdf`
* Architecture diagram: `blockdiag.png`
* High-resolution figures are located under `training/eda_outputs1/` and top-level `Figure_*.png`.

---

## 🤝 Contributing & Support

For questions on data formats, file naming, or reproducibility, please contact:

**Seyed Ahmadreza Dehghanian**
Graduate Student, Yazd University
📧 [ahmadrzdeh@gmail.com](mailto:ahmadrzdeh@gmail.com)

Pull requests and issue reports are welcome—please follow the repository’s coding conventions.

---

## 📜 License

This work is released under the MIT License. See [LICENSE](LICENSE) for details.
Data collected from publicly accessible Telegram channels; users must comply with Telegram’s Terms of Service.

```

```
