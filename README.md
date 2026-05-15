# Loan Amortization Revealer

Your bank shows you the **EMI**. It never shows how much of that EMI is **just interest** for the first several years. This script does.

## The Problem

On a ₹50L home loan at **8.5%** for **20 years**:
- **Month 1 EMI**: ₹43,391  
- **Interest**: ₹35,417 *(82% of EMI)*  
- **Principal**: ₹7,974 *(only 18% reduces debt)*  

This script makes that hidden math **visible**.

## Required Data:

- **Loan Amount** (e.g., 5000000)
- **Annual Interest Rate** (e.g., 8.5)
- **Tenure in Months** (e.g., 240 for 20 years)
## Optional Data:

**Prepay Months: Specific months to check early closure costs (e.g., 12 36 60)**

## What it Outputs

- ✅ **Exact EMI** (standard formula)  
- ✅ **Month-by-month table** (Principal vs Interest split)  
- ✅ **Crossover Month**: When principal finally exceeds interest  
- ✅ **Total interest paid** + cost %  
- ✅ **Prepayment analysis** (early closure costs + 2% penalty)  

## How to Run

**Interactive mode:**
```bash
python loan_amortization.py
```

**Command-line mode:**
```bash
python loan_amortization.py --loan 5000000 --rate 8.5 --tenure 240 --prepay 12 60 120
```

## Arguments

| Arg | Description | Example |
|-----|-------------|---------|
| `--loan / -l` | Loan amount in ₹ | `5000000` |
| `--rate / -r` | Annual interest rate (%) | `8.5` |
| `--tenure / -t` | Tenure in months | `240` |
| `--prepay / -p` | Months to check closure cost | `12 60 120` |

## Sample Output
LOAN AMORTIZATION REVEALER
============================================================
Monthly EMI: ₹43,391.13 | Total Interest: ₹54.14 L (108.28%)
============================================================

Month │ EMI │ Principal │ Interest │ Balance
───────┼──────────────┼──────────────┼──────────────┼────────────────
1 │ 43,391.13 │ 7,974.13 │ 35,417.00 │ 4,992,025.87
...
>>> │ 43,391.13 │ 21,945.67 │ 21,445.46 │ 3,768,546.34 ← ★ PRINCIPAL > INTEREST
...
240 │ 43,391.13 │ 43,341.47 │ 49.66 │ 0.00

🔄 CROSSOVER POINT: Month 131 (10y 11m)
Principal component finally exceeds interest component!                                ---

**Perfect for Level 1**: Variables, loops, conditionals, f-string formatting, argparse, and real-world financial math. [cite:1]
