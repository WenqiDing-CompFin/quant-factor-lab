# 第 3 课：单因子检验（IC 与分层）

## Rank IC

对每个月 \(t\)：

\[
\mathrm{IC}_t = \mathrm{corr}\big(\mathrm{rank}(f_{i,t}),\,\mathrm{rank}(r_{i,t\to t+1})\big)
\]

- **Mean IC**：平均预测力（A 股单因子常见量级约 0.02–0.08）  
- **ICIR = mean / std**：稳定性；比单纯 mean 更重要  
- **t 统计量**：粗略看是否显著异于 0  

代码：`src/quantlab/research/ic.py`

## 分层收益

按因子值分 5 组，看 Q5–Q1 是否稳定为正（方向对齐后）。  
若出现“两头高、中间低”的 U 型，往往说明非线性或缺失风险暴露。

代码：`src/quantlab/research/layers.py`

## 常见误读

1. 只看累计净值、不看换手与成本  
2. 全样本调参后再全样本汇报（过拟合）  
3. 把合成数据的漂亮结果当成真实市场结论 —— **Phase 1 用于学流程，Phase 2 换真数据**

## 练习

对 `ep` 与 `turnover_20` 分别解释：若 IC 为负，是因子坏了，还是**方向**设反了？  
（提示：看 `FactorSpec.direction`。）
