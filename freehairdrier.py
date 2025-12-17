import random
import tkinter as tk
from tkinter import ttk, messagebox

OFFSET = 3  # 规则中的常数 +3

def parse_code(code: str):
    """把输入解析成6位数字串，返回digits列表；不合法则抛ValueError"""
    code = code.strip()
    if len(code) != 6 or not code.isdigit():
        raise ValueError("请输入恰好 6 位数字（允许前导 0）。")
    return [int(ch) for ch in code]

def expected_d4(digits, offset=OFFSET):
    """根据 d1 d2 d3 d5 d6 计算应有的 d4"""
    d1, d2, d3, d4, d5, d6 = digits
    s = d1 + d2 + d3 + d5 + d6 + offset
    return s % 10

def is_valid(code: str, offset=OFFSET):
    """检验是否符合 d4 ≡ d1+d2+d3+d5+d6+offset (mod 10)"""
    digits = parse_code(code)
    exp = expected_d4(digits, offset)
    ok = (digits[3] == exp)
    return ok, exp, digits

def add1_mod10(x: int):
    """+1(mod10)，9->0，不进位"""
    return (x + 1) % 10

def transform_add1_d4_d6(code: str):
    """对第4位和第6位各+1(mod10)"""
    digits = parse_code(code)
    digits[3] = add1_mod10(digits[3])  # d4
    digits[5] = add1_mod10(digits[5])  # d6
    return "".join(map(str, digits))

def generate_code(fixed_d2=None, prefer_d3=None, offset=OFFSET):
    """
    生成符合规则的六码：
      - fixed_d2: 若为 0~9，则第二位固定该值；None 表示随机
      - prefer_d3: 若为 0~9，则第三位优先用该值（概率更高）；None 表示纯随机
    """
    d1 = random.randint(0, 9)

    if fixed_d2 is None:
        d2 = random.randint(0, 9)
    else:
        d2 = int(fixed_d2)

    if prefer_d3 is None:
        d3 = random.randint(0, 9)
    else:
        # 让第三位“偏好某个值”（比如 1），80% 概率取偏好值
        d3 = int(prefer_d3) if random.random() < 0.8 else random.randint(0, 9)

    d5 = random.randint(0, 9)
    d6 = random.randint(0, 9)

    # 按规则算 d4
    d4 = (d1 + d2 + d3 + d5 + d6 + offset) % 10
    return f"{d1}{d2}{d3}{d4}{d5}{d6}"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("六斋八层吹风机验证码")
        self.geometry("760x520")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        pad = 10

        frm_top = ttk.Frame(self)
        frm_top.pack(fill="x", padx=pad, pady=pad)

        ttk.Label(frm_top, text="输入六码：").grid(row=0, column=0, sticky="w")
        self.ent_code = ttk.Entry(frm_top, width=20)
        self.ent_code.grid(row=0, column=1, sticky="w", padx=(6, 18))
        self.ent_code.insert(0, "951992")

        ttk.Label(frm_top, text="第二位固定：").grid(row=0, column=2, sticky="w")
        self.var_fixed_d2 = tk.StringVar(value="不固定")
        self.cmb_d2 = ttk.Combobox(
            frm_top,
            textvariable=self.var_fixed_d2,
            values=["不固定"] + [str(i) for i in range(10)],
            width=8,
            state="readonly"
        )
        self.cmb_d2.grid(row=0, column=3, sticky="w", padx=(6, 18))

        ttk.Label(frm_top, text="第三位偏好：").grid(row=0, column=4, sticky="w")
        self.var_pref_d3 = tk.StringVar(value="不偏好")
        self.cmb_d3 = ttk.Combobox(
            frm_top,
            textvariable=self.var_pref_d3,
            values=["不偏好"] + [str(i) for i in range(10)],
            width=8,
            state="readonly"
        )
        self.cmb_d3.grid(row=0, column=5, sticky="w", padx=(6, 0))

        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill="x", padx=pad, pady=(0, pad))

        ttk.Button(frm_btn, text="检验", command=self.on_check).pack(side="left")
        ttk.Button(frm_btn, text="生成", command=self.on_generate).pack(side="left", padx=8)
        ttk.Button(frm_btn, text="等价变换：第4/6位+1", command=self.on_transform).pack(side="left", padx=8)
        ttk.Button(frm_btn, text="清空输出", command=self.on_clear).pack(side="right")

        frm_mid = ttk.Frame(self)
        frm_mid.pack(fill="x", padx=pad, pady=(0, pad))

        ttk.Label(frm_mid, text="批量生成数量：").pack(side="left")
        self.var_n = tk.StringVar(value="10")
        ttk.Entry(frm_mid, textvariable=self.var_n, width=8).pack(side="left", padx=6)
        ttk.Button(frm_mid, text="批量生成", command=self.on_generate_batch).pack(side="left", padx=8)

        frm_out = ttk.Frame(self)
        frm_out.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        ttk.Label(frm_out, text="输出：").pack(anchor="w")
        self.txt = tk.Text(frm_out, height=22, wrap="word")
        self.txt.pack(fill="both", expand=True)

        # 小提示：规则展示
        self._log("规则：d4 ≡ d1+d2+d3+d5+d6+3 (mod 10)")
        self._log("等价变换：第4位和第6位同时 +1(mod10) 仍通过（9→0不进位）")
        self._log("-" * 60)

    def _log(self, s: str):
        self.txt.insert("end", s + "\n")
        self.txt.see("end")

    def _get_fixed_d2(self):
        v = self.var_fixed_d2.get()
        return None if v == "不固定" else int(v)

    def _get_pref_d3(self):
        v = self.var_pref_d3.get()
        return None if v == "不偏好" else int(v)

    def on_check(self):
        code = self.ent_code.get().strip()
        try:
            ok, exp, digits = is_valid(code)
            d1,d2,d3,d4,d5,d6 = digits
            if ok:
                self._log(f"[通过] {code} ✅  计算得到应有 d4={exp}（当前 d4={d4}）")
            else:
                self._log(f"[不通过] {code} ❌  计算得到应有 d4={exp}（当前 d4={d4}）")
                self._log(f"  提示：把第4位改成 {exp} 就会通过（其他位不变）。")
        except Exception as e:
            messagebox.showerror("输入错误", str(e))

    def on_generate(self):
        fixed_d2 = self._get_fixed_d2()
        pref_d3 = self._get_pref_d3()
        code = generate_code(fixed_d2=fixed_d2, prefer_d3=pref_d3)
        self.ent_code.delete(0, "end")
        self.ent_code.insert(0, code)
        self._log(f"[生成] {code}")

    def on_generate_batch(self):
        try:
            n = int(self.var_n.get().strip())
            if n <= 0 or n > 5000:
                raise ValueError
        except:
            messagebox.showerror("数量错误", "请输入 1~5000 的整数。")
            return

        fixed_d2 = self._get_fixed_d2()
        pref_d3 = self._get_pref_d3()

        self._log(f"[批量生成] n={n}，第二位固定={fixed_d2 if fixed_d2 is not None else '不固定'}，第三位偏好={pref_d3 if pref_d3 is not None else '不偏好'}")
        for _ in range(n):
            self._log(generate_code(fixed_d2=fixed_d2, prefer_d3=pref_d3))
        self._log("-" * 60)

    def on_transform(self):
        code = self.ent_code.get().strip()
        try:
            new_code = transform_add1_d4_d6(code)
            self._log(f"[等价变换] {code}  ->  {new_code}")
            # 顺便检验一下新码是否通过
            ok, exp, digits = is_valid(new_code)
            self._log(f"  变换后检验：{'通过 ✅' if ok else '不通过 ❌'}（应有d4={exp}）")
            self.ent_code.delete(0, "end")
            self.ent_code.insert(0, new_code)
        except Exception as e:
            messagebox.showerror("输入错误", str(e))

    def on_clear(self):
        self.txt.delete("1.0", "end")

if __name__ == "__main__":
    random.seed()  # 需要可复现就改成固定数字
    app = App()
    app.mainloop()
