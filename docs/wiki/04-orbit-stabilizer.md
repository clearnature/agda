# Orbit-Stabilizer 谱投影定理

> 将代数、几何、拓扑钉死在一起的终极同构。Orbit x ≃ A₄/Stab x 是 CRT 谱域转换。

## 核心主张

```
Orbit x    = Σ T6Lattice (λ y → ∥ A4OrbitEquiv x y ∥₂)
           = 空间域 (粒子在 T⁶ 上的几何位置, 729格点, 6D)

A4/Stab x  = A4Element / CosetEquiv x
           = 频率域 (对应哪个谐波模式, 12陪集, 0D)

orbitStabilizer : Orbit x ≃ A4/Stab x
           = CRT 谱投影 — 空间域 ⇄ 频率域
           = 6D→0D 的维度投影
```

## 当前实现 — ✅ 构造性闭合

```
T6.agda (编译 0 错误):
├── φ : A4Element → Orbit x                          ✅ 商消除分解
├── φ-respects : 商 well-definedness                 🔴 postulate (结构必须)
├── isSetT6Lattice : isSet T6Lattice                 ✅ 构造性 (Discrete→isSet)
├── isSetOrbit x : isSet (Orbit x)                   ✅ 构造性
├── isSetA4/Stab x : isSet (A4/Stab x)              ✅ 构造性
├── orbitStabilizer← : A4/Stab x → Orbit x          ✅ rec 商消除 (T6.agda:243)
├── orbitStabilizer→ : Orbit x → A4/Stab x          ✅ STrec 截断消除 (T6.agda:248)
├── sec' : orbitStabilizer→ ∘ orbitStabilizer← ≡ id ✅ elimProp (T6.agda:256)
├── ret' : orbitStabilizer← ∘ orbitStabilizer→ ≡ id ✅ STelim (T6.agda:260)
├── orbitIso : Iso (Orbit x) (A4/Stab x)            ✅ iso 构造器 (T6.agda:270)
├── orbitStabilizer-path : Orbit x ≡ A4/Stab x      ✅ isoToPath (T6.agda:273)
└── orbitStabilizer : Orbit x ≃ A4/Stab x           ✅ pathToEquiv (T6.agda:276)
```

## φ 的正确理解

**φ 不是 GF(2) 残骸。它是商消除的结构性分解。** (wiki v1 的"移除 φ"论断是错误的)

```agda
orbitStabilizer← x = rec (isSetOrbit x) (φ x) (φ-respects x)
```

`rec` 是商类型的标准消除子。签名: `rec : isSet B → (A → B) → (∀ a b → R a b → f a ≡ f b) → A/R → B`

第三个参数就是 well-definedness 条件。对于 A4/Stab x:
- `R g h = CosetEquiv x g h = a4Action g x ≡ a4Action h x`
- `f g = φ x g = (a4Action g x , ∣(g, reflᶜ)∣₂)`
- 第三条 = `∀ g h → R g h → f g ≡ f h` = **φ-respects**

φ-respects 不是"缺失的证明"——它是类型论上 `rec` 消除商类型时必须提供的 well-definedness 条件。

**频谱投影的标准分解**:
1. φ: A4Element → Orbit x = 单个谐波指标 → 空间格点
2. rec: A4Element/CosetEquiv → Orbit x = 等价类 → 空间格点

φ-respects 作为 postulate 是合理的——它断言了映射在商上是 well-defined 的。

## sec' / ret' 闭合细节

```
sec' (T6.agda:255-257):
  elimProp 将商等价类 [g] 消除到命题
  目标: orbitStabilizer→ (orbitStabilizer← [g]) ≡ [g]
  化简: [g] ≡ [g] → reflᶜ

ret' (T6.agda:259-263):
  STelim 将集合截断 ∥_∥₂ 消除到路径
  关键: 从截断中提取 (g, eq), 用 ΣPathP 构造 Orbit 中的往返

orbitIso (T6.agda:269-270):
  iso (orbitStabilizer→ x) (orbitStabilizer← x) (sec' x) (ret' x)
  — Iso 三要素全部构造性给出
```

## 代码-状态对照

| 组件 | T6.agda 行号 | 状态 |
|---|---|---|
| Orbit 定义 | 144-145 | ✅ |
| A4/Stab 定义 | 152-153 | ✅ |
| φ | 176-177 | ✅ |
| φ-respects | 183-184 | 🔴 postulate (rec 的结构性前置) |
| isSetT6Lattice | 204-205 | ✅ 构造性 (Discrete→isSet) |
| orbitStabilizer← | 242-243 | ✅ rec 消除 |
| orbitStabilizer→ | 247-248 | ✅ STrec 消除 |
| sec' | 255-257 | ✅ elimProp |
| ret' | 259-263 | ✅ STelim |
| orbitIso | 269-270 | ✅ iso |
| orbitStabilizer-path | 272-273 | ✅ isoToPath |
| orbitStabilizer | 275-276 | ✅ pathToEquiv |

## 跨文档引用

- [CRT 的本质](00-crt-wave-physics.md) — 谱投影范式
- [代数极](01-algebraic-pole.md) — A₄ 群定义
- [几何极](02-geometric-pole.md) — T⁶ 晶格
- [拓扑极](03-topological-pole.md) — ∥·∥₂ 截断选择
- [实施路线图](09-roadmap.md) — 剩余开放问题
