# Sophie & Aiden's Pokémon channel: video editing

This repo holds our YouTube editing setup. Every video is edited the same way, using the toolkit in `editor/`.
Each video gets its own settings file in `projects/<video>/project.py`. Read this whole file before editing anything.

## Our style (approved Nov 2026, video 1)

**Overall vibe:** sweet, playful and sparkly, with a cute pastel look. The pacing is fast like Leonhart's
(tight jump cuts), but the feel is soft and lofi, never loud or aggressive.

### Must do
- **Pacing:** cut every pause longer than about 0.5 s (`silencedetect -36dB d=0.5`, keep 0.12 s of padding).
  Never cut inside card reveals, the hits lineup or the price check. List those as `protect` windows.
- **Punch-ins:** the shot alternates between normal and a 1.12x zoom every ~3.5 s. Big pulls get a soft
  1.5x zoom with **no shake**.
- **Color:** a gentle warm pastel grade (`eq=saturation=1.1:brightness=0.025:gamma=1.03,colorbalance=rs=0.03:bs=0.04:rm=0.02`).
- **Font:** Fredoka (rounded, soft) everywhere. It's in `editor/fonts/`.
- **Big sticker captions (top):** cream text with thick pastel outlines (pink, lavender, mint or peach), with
  twinkling stars and hearts. They bounce in, float and wobble, then shrink out. Use them only for hype moments
  and pulls (e.g. "IRON TREADS SIR!", "OUR FIRST GOLD CARD!", "THE HITS", "SUBSCRIBE FOR MORE RIPS!").
- **Card pop-ups:** the official card image (from images.pokemontcg.io) springs in on the right with a twist,
  floats, glows, gets a star burst, shows a rarity + number label, and swooshes off. End with a
  quick-fire "THE HITS" montage of the other hits.
- **Sparkle bursts:** stars and hearts across the screen at every scene change and on every big pull.
- **Image pop-ups:** when we say "chat, insert a picture", pop the image in the middle with a soft bounce.
- **Subtitles:** for ALL speech. **Sophie = pink, Aiden = blue**, in Fredoka with a dark plum outline and a
  little pop-in, along the bottom. The speaker is detected from voice pitch (Sophie higher, split at ~140 Hz).
  Clips where only one person talks are listed under `speakers.solo`. Censor swears (`f***`) and bleep them
  in the audio.
- **Sound effects (all soft and cute, synthesized in `editor/sfxlib.py`):** bubble pop on each caption,
  sparkle chime + soft whoosh on cards and scene changes, gentle bass thump on big pulls, ding on gold cards.
- **Music:** **lofi only**, from Mixkit (free for monetized YouTube, no credit needed). Keep it quiet, duck it
  under our voices, and drop it out for ~2 s on each big pull. The track list is in `editor/music.py`.
  **Never Kevin MacLeod.** Chillout tracks under the intro/backstory, lofi hip hop under the rip.
- **Intro structure:** the intro hook, then an "Editor Sophie" backstory cut-in (with a yellow name tag) if
  we filmed one, then back to "let's get to it", then the rip.
- **Shorts (2 per video):** vertical 1080x1920, 25–40 s each, with a pink title bar on top, the same sticker
  captions, card pop-up, sparkles and subtitles.

### Never do
- **No light-background "reaction" caption pills** that comment on what we say (e.g. "DOUBLE GOLD STAR?!",
  "THE QUICK OPEN METHOD", "SUS BOOSTERS"). None at all, in the main video or the Shorts. The toolkit no
  longer has that caption style. Don't add it back.
- No shaky zooms, harsh/meme sound effects or loud music.
- No Kevin MacLeod music, and no music we don't have the rights to.

## How to edit a new video

1. **Network:** the cloud environment must allow `drive.usercontent.google.com` and `drive.google.com`
   (to download from Google Drive), plus `images.pokemontcg.io`, `api.pokemontcg.io` and `assets.mixkit.co`.
2. **Set up the project:** `cp -r projects/_template projects/<yyyy-mm-name>` and put the Drive file ids in `sources`.
3. **Prep:** `python3 editor/prep.py <project>` downloads the clips, transcribes them (whisper medium.en),
   finds pauses and pitch, and makes contact sheets in `work/<project>/analysis/`.
4. **Plan the edit** from the transcripts and contact sheets: the timeline order, protect windows, big pulls,
   card pop-ups (identify each card from the footage, look it up on api.pokemontcg.io, and check the image
   matches), sticker captions, bleeps and Shorts. Check frames with ffmpeg before committing to times.
5. **Check:** `python3 editor/build_main.py <project> --plan`, then `--test 40` and look at frames.
6. **Render:** `python3 editor/build_main.py <project>` gives the master, a 1080p copy under 400 MB (the
   size limit for sending files in the app) and a 720p phone preview. Then run `python3 editor/build_shorts.py <project>`.
7. Send the 720p preview first, then the 1080p and the Shorts. Also hand over `work/<project>/out/subs.srt`
   if they want YouTube closed captions.

## Notes and gotchas
- Footage is iPhone HEVC. Some clips are stored rotated, and ffmpeg auto-rotates them, which is fine.
  Normalize everything to 1920x1080 at 29.97 fps.
- Jump-cut video selects use half-open frame ranges (`HALF` in `common.py`) so audio and picture stay in sync over hundreds of cuts.
- Don't `split` a source that's used twice in the timeline. Each timeline piece opens its own input (it saves memory).
- Graphics are drawn by PIL as transparent qtrle clips and layered with `setpts=PTS+t/TB`, `overlay` and `eof_action=pass`.
- YouTube downloads get blocked by a bot check here, so ask for timestamps or screenshots of reference videos instead.
- A render runs at ~0.35–0.45x real time on 4 cores, so a 12-minute edit takes ~30–40 min.
- `work/` (downloads, renders, cache) is git-ignored and disappears with the cloud session.
