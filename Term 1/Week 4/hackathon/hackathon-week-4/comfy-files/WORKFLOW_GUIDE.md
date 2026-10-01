# Workflow Guide

This folder contains the ComfyUI workflows that generate every frame of the film. Each shot has its own workflow file that runs from text prompt to finished 720p clip without any external images. This guide explains what the workflows do technically and how to run them.

## Files

| File | Purpose |
|---|---|
| `shot_01_reef_opening.json` … `shot_08_end_hope.json` | Final workflows, one per shot. Each produces the keyframe and the finished clip. |
| `00_keyframe_preview.json` | Renders 4 keyframe candidates (variants A–D) for every shot, without video. Used to choose the keyframes. |
| `previews_single/preview_XX_….json` | The same preview, but for a single shot. |
| `Shot_List_Prompts.pdf` | Shot list with keyframes and all prompts. |

All workflow files are in ComfyUI **API format**. Load them by dragging the file into the ComfyUI window (or Workflow → Open).

## Required models

| File | Folder | Used for |
|---|---|---|
| `DreamShaperXL_Lightning.safetensors` | `models/checkpoints` | Keyframes (SDXL, Lightning variant) |
| `ltx-video-2b-v0.9.5.safetensors` | `models/checkpoints` | Image-to-video |
| `t5xxl_fp8_e4m3fn.safetensors` | `models/text_encoders` | Text encoder for the video prompts |
| `RealESRGAN_x4plus_anime_6B.pth` | `models/upscale_models` | Upscaling to 720p |

All nodes used are ComfyUI core nodes; no custom nodes are needed.

## How a shot workflow works

Every shot workflow has the same three-part structure.

### 1. Keyframe (SDXL)

- `CheckpointLoaderSimple` loads DreamShaper XL Lightning.
- `CLIPTextEncode` encodes the positive prompt and the negative prompt.
- `EmptyLatentImage` (1024×576) → `KSampler` → `VAEDecode` produces the still image.
- `SaveImage` writes it to `output/keyframes/`.

Sampler settings: 6 steps, cfg 2.5, sampler `dpmpp_sde`, scheduler `karras`, denoise 1.0, fixed seed. These are the recommended settings for a Lightning model (few steps, low cfg).

Every keyframe prompt is built from the same parts: a fixed style block, the words "underwater scene", then the scene description. Shots with a pufferfish also use one fixed character description. This keeps the drawing style and the character consistent across shots, so only the content changes.

Shots 5, 6 and 7 add extra stages to the keyframe (see "Multi-stage keyframes" below).

### 2. Motion (LTX-Video, image-to-video)

- `CheckpointLoaderSimple` loads LTX-Video 2B (model and VAE).
- `CLIPLoader` (type `ltxv`) loads the T5 text encoder; `CLIPTextEncode` encodes the motion prompt and the video negative prompt.
- `LTXVImgToVideo` takes the keyframe as the first frame and creates the video latent (512×288, 73 or 97 frames).
- `LTXVConditioning` sets the frame rate (24 fps).
- `LTXVScheduler` (30 steps, max_shift 2.05, base_shift 0.95, stretch on, terminal 0.1) creates the noise schedule.
- `CFGGuider` (cfg 3.0), `KSamplerSelect` (euler) and `RandomNoise` (fixed seed) feed `SamplerCustomAdvanced`.
- `VAEDecode` turns the result into frames.

Every motion prompt ends with the same style sentence ("Flat 2D cartoon animation with thick black outlines and solid colors") so the video keeps the cartoon look.

### 3. 720p output

- `UpscaleModelLoader` + `ImageUpscaleWithModel` enlarge every frame 4× with RealESRGAN (anime model, suited to flat cartoon images).
- `ImageScale` (Lanczos) resizes to exactly 1280×720.
- `CreateVideo` (24 fps) + `SaveVideo` (mp4, H.264) write the clip to `output/shots/`.

The video model runs at a low resolution because the workflows were built for a 4 GB GPU (RTX 2050). The upscaler brings the result to 720p inside ComfyUI.

## Multi-stage keyframes (shots 5, 6, 7)

Some scenes could not be generated in one text-to-image pass: when a fish and trash were combined in one prompt, the model merged them (fish drawn inside bottles, trash turned into fish). These shots therefore build the keyframe in several stages, all inside the same workflow.

**Masked inpainting** is used in all three: the base image is encoded back into a latent (`VAEEncode`), a mask is built from `SolidMask` and `MaskComposite` nodes, and `SetLatentNoiseMask` tells the second `KSampler` to repaint only the masked area. Everything outside the mask stays unchanged.

### Shot 5 – inpaint into another shot's keyframe
1. Regenerates the shot 4 keyframe (same prompt and seed as shot 4).
2. Repaints a box in the centre (408×344 px at x=304, y=112, edges softened with `FeatherMask`) with the pufferfish. Seed 1207, denoise 0.9.

Result: the trash around the fish is pixel-identical to shot 4. The prompt of step 2 still contains the wording of an earlier "tangled" shot; it was kept unchanged because changing it would change the chosen image.

### Shot 6 – repaint selected regions
1. Generates the base image (fish and reef). Seed 1306.
2. Repaints two regions with the fishing net: the top band (1024×128 px) and the left strip (264×576 px). Seed 1106, denoise 1.0.

The video pass of this shot renders at 896×512 instead of 512×288, so the thin net lines are not lost in the video model's compression. Additional video negatives prevent the net from disappearing.

### Shot 7 – keep the subject, repaint the surroundings
1. Generates the base image. Seed 1208.
2. Inverted mask: the fish in the centre (304×288 px at x=360, y=136) is **kept**, everything else is repainted as a polluted seabed. The mask edge is softened with `MaskToImage` → `ImageBlur` (radius 24) → `ImageToMask`. This stage uses extra negatives (sky, land, coral, bright colours) and cfg 3.5 so the new environment replaces the original reef. Seed 1208, denoise 0.9.
3. A light pass over the whole image (`VAEEncode` → `KSampler`, denoise 0.3, seed 1215) blends the seam around the fish.

The video uses a static camera and extra negatives (colour change, scene change, camera movement) so the model does not invent new surroundings.

## Shot settings

| # | File | Keyframe | Keyframe seed(s) | Video size | Frames | Video seed |
|---|---|---|---|---|---|---|
| 1 | `shot_01_reef_opening.json` | text-to-image | 1201 | 512×288 | 73 (3.0 s) | 1201 |
| 2 | `shot_02_kids_playing.json` | text-to-image | 1302 | 512×288 | 73 (3.0 s) | 1302 |
| 3 | `shot_03_parents_smile.json` | text-to-image | 1103 | 512×288 | 73 (3.0 s) | 1103 |
| 4 | `shot_04_trash_arrives.json` | text-to-image | 1105 | 512×288 | 73 (3.0 s) | 1105 |
| 5 | `shot_05_horrified.json` | shot 4 + inpaint | 1105 → 1207 | 512×288 | 97 (4.0 s) | 1207 |
| 6 | `shot_06_fishing_net.json` | base + inpaint | 1306 → 1106 | 896×512 | 73 (3.0 s) | 1106 |
| 7 | `shot_07_last_child.json` | base + inverted inpaint + blend | 1208 → 1208 → 1215 | 512×288 | 97 (4.0 s) | 1208 |
| 8 | `shot_08_end_hope.json` | text-to-image | 1209 | 512×288 | 73 (3.0 s) | 1209 |

Total: 632 frames = 26.3 s at 24 fps. All outputs are 1280×720.

## How the keyframes were chosen (variants)

`00_keyframe_preview.json` and the files in `previews_single/` render four candidates per shot, called variants A–D. For text-to-image shots, the variants use the shot's base seed plus 0, 100, 200 or 300. For the inpainting shots, the variants also differ in denoise strength. The chosen variant per shot is used in the final shot files:

1C, 2D, 3B, 4B, 5C, 6B, 7C, 8C

## Regenerating the film

1. Install the four models listed above.
2. Load `shot_01_reef_opening.json` and press Run; repeat for shots 2–8. ComfyUI queues the runs, so all eight can be started at once.
3. Clips are saved to `output/shots/`, keyframes to `output/keyframes/`.
4. The eight clips are joined in order with hard cuts (1280×720, 24 fps); no frames are changed.

To change a shot, open its workflow and edit the prompt in the `CLIPTextEncode` node, the seed in the `KSampler` / `RandomNoise` node, or the length in the `LTXVImgToVideo` node, then run it again.

**Note on reproducibility:** fixed seeds make every run repeatable on the same setup. On a different GPU, driver or ComfyUI version, results can differ slightly. The clips in the film were rendered on Windows with an NVIDIA RTX 2050 (4 GB).
