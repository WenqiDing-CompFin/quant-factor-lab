# Quant Factor Lab

**A-share + US equities** factor research bench.  
End-to-end educational pipeline for learning quant methods and building a Financial Engineering (金工 / MFE) application portfolio.

Repo: https://github.com/WenqiDing-CompFin/quant-factor-lab

[中文说明](#中文) · [English](#english)

---

<a id="english"></a>
## English

### What this repo demonstrates
1. **Factor selection from first principles** — economic story → definition → empirical tests  
2. **Single-factor research** — Rank IC, ICIR, quantile-layer returns  
3. **Factor correlation** — avoid stacking redundant signals  
4. **Multi-factor combination** — direction-aligned z-score blend  
5. **Cost-aware long-only backtest** — turnover + bps cost proxy  
6. **Interactive visualization** — Streamlit dashboards (A-share & US)  

Both markets share one research stack under `src/quantlab/`. Demos use **reproducible synthetic panels** with planted weak signals so GitHub visitors can run offline. Swap data loaders later without rewriting IC / backtest code.

### Quickstart — US module

```bash
cd quant-factor-lab
pip install -r requirements.txt
pip install -e .

python scripts/us_01_build_demo_data.py
python scripts/us_02_select_and_test_factors.py
python scripts/us_03_multi_factor_backtest.py
streamlit run app/streamlit_us.py
```

### Quickstart — A-share module

```bash
python scripts/01_build_demo_data.py
python scripts/02_select_and_test_factors.py
python scripts/03_multi_factor_backtest.py
streamlit run app/streamlit_app.py
```

### Learn in order
| Lesson | Topic |
|---|---|
| [`lessons/01_what_is_a_factor.md`](lessons/01_what_is_a_factor.md) | What is a factor? |
| [`lessons/02_selecting_factors.md`](lessons/02_selecting_factors.md) | How to select factors |
| [`lessons/03_single_factor_test.md`](lessons/03_single_factor_test.md) | IC & quantile tests |
| [`lessons/04_us_module.md`](lessons/04_us_module.md) | US equities track |

### Project layout
```text
configs/            # ashare_demo.yaml, us_demo.yaml
lessons/            # teaching notes
scripts/            # A-share + US pipeline entrypoints
app/                # streamlit_app.py (CN) · streamlit_us.py (US)
src/quantlab/
  data/             # synthetic A-share & US panels
  factors/          # catalog + compute
  research/         # IC / layers / correlation
  backtest/         # monthly long-only engine
  portfolio/        # multi-factor combine
```

### Roadmap
- [x] Phase 1: A-share teaching pipeline + dashboard  
- [x] Phase 3: US equities parallel module (same research API)  
- [x] Factor correlation heatmap (US dashboard / scripts)  
- [ ] Industry / size neutralization  
- [ ] Real-data adapters (akshare / CRSP-style / Yahoo)

### Disclaimer
For education and research methodology demonstration only. Not investment advice. Synthetic data is not a claim about live market premia.

---

<a id="中文"></a>
## 中文

### 这是什么
从零学习因子选股的完整实验台：**A 股 + 美股** 两套可运行模块，同一套研究代码（选因子 → IC/分层 → 相关 → 多因子合成 → 扣成本回测 → Streamlit 可视化），适合金工 / MFE 申请作品集。

### 美股怎么跑
见上文 **Quickstart — US module**，或读 [`lessons/04_us_module.md`](lessons/04_us_module.md)。

### 给申请材料的一句话
> Built a market-agnostic cross-sectional factor research pipeline (selection → IC/ICIR → quantile sorts → correlation diagnostics → multi-factor portfolio → cost-aware backtest) with interactive dashboards for both China A-shares and US equities.
