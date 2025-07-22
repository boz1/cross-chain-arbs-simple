## Description

This repository provides code and data for exploring cross‑chain arbitrage matches exported from Dune, following the methodology described in [Cross‑Chain Arbitrage: The Next Frontier of MEV in Decentralized Finance](https://arxiv.org/abs/2501.17335). We implement a simple pipeline to:

1. **Load & preprocess** raw match data from multiple chains.
2. **Filter** candidate matches by:
   - **Cyclic asset flow** (swap on Chain A → swap back on Chain B)
   - **Marginal‑difference** ≤ 0.5 %
   - **Temporal‑window** ≤ 3600 s
   - **Entity link**
3. **Deduplicate** overlapping candidate pairs by ranking first on smallest marginal difference, then on shortest time gap.
4. **Export** the final, deduplicated list of cross‑chain swaps for further analysis.

## Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/boz1/cross-chain-arbs-simple
   cd cross-chain-arbs-simple
   ```

2. **Install dependencies**

   ```bash
   pip install pandas numpy matplotlib
   ```

3. **Run the filtering script**
   ```bash
   python filter_swaps.py
   ```
   This will read all CSVs in `data/raw/`, apply the 0.5 % / 3600 s heuristic, deduplicate overlaps, and write `filtered_cross_chain_swaps.csv` to `data/output/`.
4. **Inspect results**
   
   Use the notebook (`notbook.ipynb`) to explore the data.

## Citation

If you use this repository or its data in your work, please cite:

```bibtex
@misc{öz2025crosschainarbitragefrontiermev,
  title        = {Cross-Chain Arbitrage: The Next Frontier of MEV in Decentralized Finance},
  author       = {Burak Öz and Christof Ferreira Torres and Christoph Schlegel and Bruno Mazorra and Jonas Gebele and Filip Rezabek and Florian Matthes},
  year         = {2025},
  eprint       = {2501.17335},
  archivePrefix= {arXiv},
  primaryClass = {cs.CR},
  url          = {https://arxiv.org/abs/2501.17335},
}
```
