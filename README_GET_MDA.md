# Get MDA

This script requires a list of public US companies in csv format, with a column named 'TICKER' containing public company tickers, in the same folder to work.

### How To

Specify the starting year to download from, and optionally change directory to save outputs ('default=/data').

### Example

```bash
# Downloads and parses MDA sections from both 10Ks and 10Qs going back to Jan. 1st 2019, and saves to `./data/`
python get_mda.py --back_to_year 2019
```
