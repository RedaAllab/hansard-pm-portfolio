# Fonts

Static weight instances used by `hansard_pm_portfolio.style` (STYLE_DUEL.md §4). Each is SIL Open Font License 1.1 (see the accompanying `OFL-*.txt`), free to bundle and redistribute.

| File | Family (as matplotlib sees it) | Source |
|---|---|---|
| `Lora-Bold.ttf` | `Lora`, weight 700 | [google/fonts, ofl/lora](https://github.com/google/fonts/tree/main/ofl/lora) — variable font, instanced at `wght=700` |
| `Inter-SemiBold.ttf` | `Inter SemiBold`, weight 600 | [google/fonts, ofl/inter](https://github.com/google/fonts/tree/main/ofl/inter) — variable font, instanced at `wght=600` |
| `Inter-Regular.ttf` | `Inter`, weight 400 | same, instanced at `wght=400` |
| `IBMPlexMono-Medium.ttf` | `IBM Plex Mono Medium` | [google/fonts, ofl/ibmplexmono](https://github.com/google/fonts/tree/main/ofl/ibmplexmono) — distributed natively as a static file, no instancing needed |

## Why static instances, not the variable fonts directly

Matplotlib does not reliably resolve a specific weight out of a variable font. Lora and Inter ship from Google Fonts as single variable files spanning their whole weight range; the two static instances used here were generated once with:

```bash
python3 -m fontTools.varLib.instancer Lora-Variable.ttf wght=700 -o Lora-Bold.ttf --update-name-table
python3 -m fontTools.varLib.instancer Inter-Variable.ttf wght=600 -o Inter-SemiBold.ttf --update-name-table
python3 -m fontTools.varLib.instancer Inter-Variable.ttf wght=400 -o Inter-Regular.ttf --update-name-table
```

`--update-name-table` alone was not enough: the instanced files still carried the original variable font's typographic-family name records (name IDs 16/17), which matplotlib's font resolver prefers over the updated legacy family name (ID 1) — so `Inter-SemiBold.ttf` and `Inter-Regular.ttf` both resolved to the single family `"Inter"`, indistinguishable. Name IDs 16, 17, 21, and 22 were stripped from the two Inter instances (and would need the same treatment for any future re-instancing) so each file resolves a unique family name. See `ARCHITECTURE.md` §8.
