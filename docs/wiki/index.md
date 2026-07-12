# 大衍高维同构理论 · 知识图谱 v6.0

> **范式声明**: 本体系运行在 GF(3) ⊕ C3/A4 ⊕ CRT 谱投影的三极框架上。
> 任何以 GF(2) 模运算、实数连续统、或一维 Path 等式为前提的推理，在此体系中无效。
>
> **核心纠正 (v5.2)**: 6624 是相位对齐点，不是闭合周期。极限环永不闭合，只持续级联。

---

## 三极大一统

```
                     Orbit-Stabilizer 谱投影
                          ┌───┴───┐
    代数极 (频率域) ←─────┤  CRT  ├─────→ 几何极 (空间域)
    GF(3)/C3/A4            │ 谱域转换│       T⁶ 晶格 / 幻方正交
    Bézout 构造底座        └───┬───┘       Christoffel 螺旋
                         拓扑极 (不变量)
                      ∥·∥₂ 截断 / 极限环 / 环面结 / 时间晶体
```

| 极 | 域 | 核心结构 | 代码锚点 |
|---|---|---|---|
| 代数 | 频率域 (0D商) | GF(3)→GF(3²)→C3→A₄→Bézout→CRT | `CRTLemmas.agda`, `CRT.agda` |
| 几何 | 空间域 (6D晶格) | T⁶=729格点, 幻方4×4正交, Christoffel螺旋 | `T6.agda`, `magic144.cpp` |
| 拓扑 | 不变量 (极限环) | ∥·∥₂截断, 环面结, 陈数C=±2, 时间晶体 | `T6.agda`, `chern2_constructor.py` |

---

## 知识图谱导航

### 认知基底层
- [CRT 的本质：物理波系统，不是同余代数](00-crt-wave-physics.md)
- [术语表：闭合 vs 对齐 vs 极限环](07-glossary.md)
- [刚性常量表](08-constants.md)

### 三极展开
- [代数极：GF(3)/C3/A4 共轭引擎](01-algebraic-pole.md)
- [几何极：T⁶ 晶格与幻方正交](02-geometric-pole.md)
- [拓扑极：极限环与时间晶体](03-topological-pole.md)

### 终极同构
- [Orbit-Stabilizer 谱投影定理](04-orbit-stabilizer.md)

### 工程实现
- [六层垂直栈：代码-理论对照](05-code-theory-mapping.md)
- [实验验证：384K步 LCM 环量子等离子极限环](06-experimental.md)
- [实施路线图](09-roadmap.md)

---

## 跨层刚性常量

| 常量 | 值 | 物理意义 |
|---|---|---|
| POLAR_WINDING | 144 | 极向缠绕 (I_h 120 + 手征24) |
| TOROIDAL_WINDING | 46 | 环向缠绕 (全息周期) |
| π_HOLO | 144/46 | 全息π (精确有理数) |
| GRAND_PUMP | 6624 | 相位对齐点 (非闭合!) |
| ZHONGLV | 3¹¹ = 177147 | 仲吕乘数 |
| HUANGZHONG | 2¹⁶ = 65536 | 黄钟分母 |
| LCM_TOTAL | 11609505792 | LCM 总格点 (116亿) |
| CHERN | C=±2 | 陈数拓扑不变量 |
| DELTA | √3 | 相变能隙 |
| TWELVE_TONES | 12 | A₄ 群阶 / 十二律基元 |

---

## 六层垂直栈

```
层6: 文档知识   → /home/yanli/文档/math/ + /data/work/docs/
层5: 理论声明   → 三极大一统 (.md)
层4: 形式化证明 → Agda (CRTLemmas/CRT/T6/A4Group) — 类型安全
层3: 数学底层   → C++ (~/work/math) — GF(3) 八层 L0→L8
层2: 训练框架   → Python (/data/trit/pyBitNet) — Christoffel 训练
层1: 自定义编译 → /data/trit/浑天 — VAVX3/ternary-core
层0: 模型产出   → ~/work/sanyuan-llm — Phase2.1→3.1
```

---

*最后更新: 2026-07-11 · 基于 384K 步训练实证 + scholar-loop 跨尺度验证*
