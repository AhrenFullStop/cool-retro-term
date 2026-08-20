# Council member portraits

Prompt set for the 5 council members × 3 thinking states = **15 portraits**.

| File | Contents |
|---|---|
| `prompts.json` | The manifest. 15 fully-assembled prompts plus the components they were built from. |
| `generate.py` | Renders the manifest to PNGs. Stdlib only, bring your own API key. |
| `png/` | Output directory (gitignored — regenerate rather than commit). |

## Rendering

```sh
export OPENAI_API_KEY=sk-...
./generate.py --provider openai
```

or

```sh
export GEMINI_API_KEY=...
./generate.py --provider gemini
```

Existing files are skipped, so a failed run is safe to re-run — it picks up where it
stopped. Iterate on one character with `--only cto`, or one image with
`--only cto-thinking`, and add `--force` to overwrite. `--dry-run` prints the exact
prompts without calling anything.

Model ids move fast. If your account exposes a different one, pass `--model`.

## How a prompt is assembled

Each of the 15 prompts is `shared_style_prefix` + `character` + `identity_anchor` +
the state description. The manifest keeps all four separately, so a change to the
shared style is one edit rather than fifteen.

The **identity anchor** is the piece that does not appear in the original brief. Image
models will happily give you three different men across a character's three states —
same description, different face. Each anchor restates the invariants (same face, same
hair, same garment, same accent hex) so the three states read as one person. If faces
still drift, the next lever is generating the `idle` state first and passing it back as
a reference image on the other two.

## States

`idle` → `thinking` → `done`, for each of:

| Member | Accent | Hex |
|---|---|---|
| Ideas Man | violet | `#6B5F9E` |
| Product Guy | rose | `#B98D93` |
| Pragmatist | steel blue | `#4A79B8` |
| Ponytail | azure | `#4A9AD8` |
| CTO | indigo | `#22357F` |

## Provenance

Every entry carries a `source` field. Thirteen are `user-supplied` — the brief's wording,
edited only for punctuation and to append the accent-colour instruction.

Two are `authored`, because the source brief was truncated:

- **`cto-thinking`** — the brief cut off at *"Deep contemplation — eyes closed or looking
  downward, processing s…"*. Completed in the established voice.
- **`cto-done`** — absent from the brief entirely. Written from scratch to close the
  arc the other four characters follow (idle → effort → resolution).

Both are the ones to review first.
