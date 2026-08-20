# Council member portraits

Prompt set for the 5 council members × 3 thinking states = **15 portraits**.

| File | Contents |
|---|---|
| `prompts.json` | The manifest. 15 fully-assembled prompts plus the components they were built from. |
| `generate.py` | Renders the manifest to PNGs. Stdlib only, bring your own API key. |
| `png/` | Output directory (gitignored — regenerate rather than commit). |

## Rendering

Requires `OPENAI_API_KEY` in the environment. The command:

```sh
cd assets/council-portraits
./generate.py --provider openai --quality low
```

That writes 15 PNGs to `png/`. Existing files are skipped, so an interrupted run is
safe to re-run — it picks up where it stopped.

`--quality` is `low` | `medium` | `high` and is the main cost lever; omit it to take
the API default. Low is cheapest and good for checking composition and character
consistency; re-render the keepers at `--quality high --force` once the set looks right,
since this style leans hard on facial detail.

Other flags: `--only cto` (one member) or `--only cto-thinking` (one image), `--force`
to overwrite, `--dry-run` to print prompts without calling anything.

Gemini works too, via `GEMINI_API_KEY` and `--provider gemini`. Model ids move fast —
pass `--model` if your account exposes a different one.

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
