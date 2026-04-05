# 🚀 REVIVE Deal Analyzer - Setup Guide

## Quick Start (5 minutes)

### Option 1: Online (Recommended - No Installation Needed)

1. **Go to:** https://streamlit.io/cloud
2. **Click:** "Create app"
3. **Connect your GitHub** (or ask me to deploy it)
4. **Upload the file:** `revive_app.py`
5. **Done!** App is live and shareable

### Option 2: Local Computer (Your Desktop)

#### Step 1: Install Python (if not already installed)
- **Mac/Linux:** Open Terminal, run: `python3 --version`
- **Windows:** Download from https://python.org

#### Step 2: Install Required Tools
```bash
pip install streamlit pandas
```

#### Step 3: Run the App
```bash
streamlit run revive_app.py
```

Your app opens at: `http://localhost:8501`

---

## How to Use (2 minutes)

### For Each New Deal:

1. **Enter Monthly Overhead** (if you have it)
   - Rent, staff, utilities, etc.
   - Leave at $0 if you just want gross profit

2. **Enter Their Order:**
   - How many skins? (Volume)
   - What price are you asking?
   - Any discount? (0% = no discount)
   - Payment terms (When do they pay you?)

3. **Click: ANALYZE DEAL**

4. **Read the Result:**
   - 💵 Your profit
   - 🔴/🟡/🟢 Risk level
   - ✅/⚠️/❌ Recommendation

5. **Optional:** Save the deal to compare multiple scenarios

---

## Understanding Your Results

### Three Things That Matter:

**1. Net Profit ($)**
- Money you actually keep after all costs
- Green number = good deal
- Red number = don't do it

**2. Margin (%)**
- Percentage of revenue that's profit
- 50%+ = excellent
- 30-50% = good
- <30% = risky

**3. Risk Level (Color)**
- 🟢 Green = Safe, move forward
- 🟡 Yellow = Be careful, negotiate
- 🔴 Red = Avoid unless you must

---

## Real-World Examples

### Example 1: Retailer offers 5K units at your asking price
```
Volume: 5,000
Price: $4.50/unit
Discount: 0%
Payment: Net 30

RESULT: $13,490 profit (60% margin)
DECISION: ✅ EXCELLENT - Take it
```

### Example 2: Brand wants 10K units with 10% discount
```
Volume: 10,000
Price: $4.25/unit (default for 10K)
Discount: 10% (they negotiate down)
Payment: Net 45

Your actual price: $3.83/unit
Cost per unit: $1.70
Profit per unit: $2.13
Total profit: $21,300
DECISION: ✅ GOOD - Proceed
```

### Example 3: Large order but tough terms
```
Volume: 25,000
Price: $3.90 (standard)
Discount: 15%
Payment: Net 90

Your actual price: $3.31/unit
Cost per unit: $1.56
Profit per unit: $1.75
Total profit: $43,750
BUT: $4,125 tied up for 90 days
DECISION: ⚠️ NEGOTIATE - Ask for Net 60 or prepayment
```

---

## Pricing Reference (Built Into App)

Your costs by volume (automatically calculated):

| Volume | Cost/Unit | Standard Price | Margin |
|--------|-----------|----------------|--------|
| 5,000 | $1.80 | $4.50 | 60% |
| 10,000 | $1.70 | $4.25 | 60% |
| 15,000 | $1.65 | $4.13 | 60% |
| 20,000 | $1.58 | $3.95 | 60% |
| 25,000 | $1.56 | $3.90 | 60% |
| 30,000 | $1.50 | $3.75 | 60% |
| 35,000 | $1.48 | $3.70 | 60% |
| 40,000 | $1.46 | $3.65 | 60% |
| 45,000 | $1.44 | $3.60 | 60% |
| 50,000 | $1.42 | $3.55 | 60% |

**Key insight:** All tiers are highly profitable. Even at 50K units, you keep 60% margin.

---

## Troubleshooting

### "Command not found: streamlit"
- You haven't installed Streamlit yet
- Run: `pip install streamlit`

### "ModuleNotFoundError: No module named 'pandas'"
- Run: `pip install pandas`

### App won't load
- Make sure you're in the right folder (where `revive_app.py` is saved)
- Try: `streamlit run revive_app.py` again

### Lost my saved deals
- They're stored in your browser session
- Export to JSON before closing to keep them

---

## Tips for Success

1. **Always include monthly overhead** - This shows true profitability
2. **Save every deal** - Build a history to see which customers are best
3. **Use for negotiations** - Show customers the margin impact of their requests
4. **Export weekly** - Keep backups of your scenario analysis
5. **Update costs if they change** - The app uses your 2024 pricing data

---

## Next Steps

- **Immediate:** Run the app, test with 2-3 deals
- **Week 1:** Use it for all incoming RFQs
- **Week 2:** Share results with your sales team
- **Month 1:** Review which deals were actually most profitable (actuals vs. forecast)

---

## Need Help?

If something doesn't work:
1. Check Python version: `python3 --version` (needs 3.8+)
2. Reinstall: `pip install --upgrade streamlit pandas`
3. Run again: `streamlit run revive_app.py`

If you want to modify the app or add features, just ask!

---

**Version:** 1.0 (Built for REVIVE, 2024)
**Last Updated:** April 2024
