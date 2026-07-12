# 实施路线图

> 从当前状态到三极全闭合的路径。优先级按依赖关系排列。

## 当前状态总览

```
✅ 已完成:
  层4 (Agda): Bézout crt-merge (0 postulate), CRT crtTheorem
  层3 (C++):  GF(3) 八层 L0→L8, LCM 桥
  层2 (Python): Christoffel 训练, 纳音相变, 384K 步极限环
  层1 (LLVM):  VAVX3 指令集, ternary-core
  编译器:     canonicalEqName 修复

🟡 部分完成:
  层4: T⁶ 晶格定义, A₄ 群, Orbit-Stabilizer 方向映射
  层2: 陈数守卫, 时间晶体验证

🔴 开放:
  层4: GF(3²), φ-respects (已确定为 GF2 残骸→移除), orbitIso
  层2: 幻方正交形式化
  全栈: CRT O(1) 查表
```

## 阶段 1: 形式化层闭合

| # | 任务 | 难度 | 状态 |
|---|---|---|---|
| 1a | `isSetT6Lattice` 去 postulate | 低 | 待执行 |
| 1b | 移除 φ (GF2 残骸), 移除 φ-respects | 低 | 设计决策已确认 |
| 1c | T6.agda 编译修复 (lUnit 导出问题) | 低 | bug |
| 1d | `orbitIso` sec'/ret' 填充 | 高 | 开放问题 |

## 阶段 2: GF(3²) 形式化

| # | 任务 | 难度 |
|---|---|---|
| 2a | 定义 GF9 = GF3[x]/(x²+x+1) | 中 |
| 2b | 定义 Frobenius 自同构 x↦x³ | 低 |
| 2c | 证明 ω↦ω² 是伽罗瓦共轭 | 中 |
| 2d | 在 A4Group 中连接 C3 表示与 GF(3²) | 高 |

## 阶段 3: 幻方正交形式化

| # | 任务 | 难度 |
|---|---|---|
| 3a | 定义 MagicSquare4x4 类型 (行列权重守恒) | 中 |
| 3b | 实现 CRT 谱截断引理 (±2√10→±16) | 高 |
| 3c | 实现正交判据替换引理 (gcd→拓扑内积) | 高 |

## 阶段 4: 全栈闭合

| # | 任务 | 难度 |
|---|---|---|
| 4a | `crtIso` 去 postulate | 高 |
| 4b | CRT O(1) 查表在编译器内核中实现 | 高 |
| 4c | 384K+ 步持续训练 (全 LCM 环闭合验证) | 中 |
| 4d | scholar-loop 跨尺度定理形式化提交 | 高 |

## 当前推荐行动

**立即执行**: 阶段 1a (`isSetT6Lattice`) — 最低风险，独立可证。
**接下来**: 阶段 1b (移除 φ) — 设计决策已确认，纯删除+编译修复。
**中期目标**: 阶段 2 (GF(3²)) — 整个理论链中唯一完全缺失的代码层。

---

## Agda 三条开放问题

| # | 问题 | 难度 | 状态 |
|---|---|---|---|
| 1 | CRT HDU 嵌入 — tau_hdu thunk 触发递归崩溃 | ⭐⭐⭐ | Unify.hs 上下文隔离 |
| 2 | 索引族 transp 子句完全正确性 (#3733) | ⭐⭐⭐⭐⭐ | "non-trivial research" |
| 3 | leftInv raiseS — 类型级 vs 项级 S 提升不一致 | ⭐⭐ | 待分析 |

---

*最后更新: 2026-07-11*
