# NARUTO Mythos TCG tokens: Power, Chakra, Edge

Original ninja-themed designs for casual play. These are not official artwork or logos.

| File | What | Colours (AMS) | ≈ PLA / time* |
|---|---|---|---|
| `power_tokens.3mf` | 24 × "+1" (Ø20) + 6 × "+5" (Ø24) | red base · **white** numbers | 25 g / ~45 min |
| `chakra_tokens.3mf` | 24 × chakra swirl (Ø22) + 6 × "5" (Ø26) | black base · **yellow** design | 30 g / ~50 min |
| `edge_tokens.3mf` | 2 × shuriken "EDGE" (46 mm) | yellow base · **black** design | 4 g / ~10 min |

\*Plus about 5–10 min and 1–3 g for colour changes. The colour is only in the top 3 layers (0.6 mm),
so each plate swaps colour just a few times.

Rules check ([rulebook](https://irp.cdn-website.com/99e556bf/files/uploaded/Naruto-Mythos-TCG-Rulebook-EN.pdf)):
each Power token is +1 Power on a character, Chakra is spent to pay costs, and the Edge token
breaks ties and decides who goes first. The "+5" and "5" tokens are just shortcuts for big
turns. Tournament rules need Chakra to be easy to tell apart, and these are a different size,
colour and shape from the other tokens.

## Bambu Studio
1. Drag in the file. It's **one object with two parts**: "… base" and "… design". If it asks
   to load as a single object with multiple parts, click **Yes**.
2. In the object list (left), expand the object, click the **design** part, and set its filament
   to the right AMS slot (white for power, yellow for chakra, black for edge). Set the base part
   to its colour (red / black / yellow).
3. Process: **0.20mm Standard** (the text needs the finer layers). Walls 2, infill 15%,
   **supports off**, plate **Textured PEI**.
4. Leave **Prime tower ON** (default for multi-colour); it keeps the colours clean.
   **Flushing volumes** can be lowered to 0.7× when going dark → light.
5. Slice. Every token should show two colours only on the top face.

Regenerate or change counts: edit `COUNTS` in `generate.py`, then `python3 models/naruto_tokens/generate.py`.
