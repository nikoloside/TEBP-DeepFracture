"""DeepFracture Runtime — interactive brittle-fracture demo.

Rigid-body collision (PyBullet) -> collision embedding -> VQ-VAE generator
(weights from hf.co/nikoloside/deepfracture) -> watershed segmentation ->
fragment meshes -> back into the rigid-body simulation.
"""

import gradio as gr

from runtime.pipeline import PRESETS, parse_csv_preset, run_demo
from runtime.predictor import SHAPES, download_asset

DESCRIPTION = """
# 💥 DeepFracture Runtime

Neural brittle-fracture prediction inside a rigid-body runtime, end to end:
a projectile hits the target (**PyBullet** collision detection), the impact is
encoded as a 7-D collision embedding *(position, direction, impulse)*, the
per-shape **VQ-VAE generator** ([weights on the Hub](https://huggingface.co/nikoloside/deepfracture))
predicts a geometrically-segmented SDF, a pure-Python **watershed / flooding
segmentation** turns it into fragment meshes — and the fragments drop back
into the simulation.

Papers: [DeepFracture (CGF 2025)](https://nikoloside.graphics/deepfracture/) ·
[Far-From-Boundary Fields (SMI 2026)](https://nikoloside.graphics/far-from-boundary-fields/) ·
Code: [TEBP-DeepFracture](https://github.com/nikoloside/TEBP-DeepFracture) ·
[far-from-boundary-fields](https://github.com/nikoloside/far-from-boundary-fields)
"""

DEFAULT_POS = [0.103, 0.822, 2.883]
DEFAULT_VEL = [-2.34, -18.71, -65.61]


def apply_preset(name):
    if name not in PRESETS:
        return [gr.update()] * 7
    shape, csv = PRESETS[name]
    pos, vel = parse_csv_preset(download_asset(csv))
    return [shape] + [round(v, 3) for v in pos] + [round(v, 3) for v in vel]


def fracture(shape, px, py, pz, vx, vy, vz, seed, gravity,
             progress=gr.Progress()):
    progress(0.05, desc="Loading model & simulating collision…")
    out = run_demo(shape, [px, py, pz], [vx, vy, vz], seed=int(seed),
                   gravity=-5.0 if gravity else 0.0)
    if "error" in out:
        raise gr.Error(out["error"])
    info = out["info"]
    summary = (
        f"Impact at step {info['impact_step']} · "
        f"impulse {info['impulse_raw']:.0f} (norm {info['impulse_norm']:+.2f}) · "
        f"codebook #{info['codebook_index']} · "
        f"{info['n_fragments']} fragments"
    )
    return out["video"], out["glb"], summary, info


with gr.Blocks(title="DeepFracture Runtime") as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        with gr.Column(scale=1):
            preset = gr.Dropdown(list(PRESETS.keys()), value="squirrel-260",
                                 label="Collision preset (from the paper's runtime CSVs)")
            shape = gr.Dropdown(SHAPES, value="squirrel", label="Target shape")
            with gr.Group():
                gr.Markdown("**Projectile start position**")
                with gr.Row():
                    px = gr.Slider(-3, 3, DEFAULT_POS[0], step=0.01, label="x")
                    py = gr.Slider(-3, 3, DEFAULT_POS[1], step=0.01, label="y")
                    pz = gr.Slider(-3, 3, DEFAULT_POS[2], step=0.01, label="z")
                gr.Markdown("**Projectile velocity**")
                with gr.Row():
                    vx = gr.Slider(-120, 120, DEFAULT_VEL[0], step=0.5, label="vx")
                    vy = gr.Slider(-120, 120, DEFAULT_VEL[1], step=0.5, label="vy")
                    vz = gr.Slider(-120, 120, DEFAULT_VEL[2], step=0.5, label="vz")
            with gr.Row():
                seed = gr.Number(42, label="Latent seed", precision=0)
                gravity = gr.Checkbox(True, label="Gravity after fracture")
            run_btn = gr.Button("💥 Fracture!", variant="primary")

        with gr.Column(scale=2):
            video = gr.Video(label="Runtime simulation", autoplay=True)
            model3d = gr.Model3D(label="Predicted fragments (drag to inspect)",
                                 clear_color=[0.95, 0.95, 0.95, 1.0])
            summary = gr.Textbox(label="Result", interactive=False)
            with gr.Accordion("Collision embedding (network input)", open=False):
                info_json = gr.JSON()

    preset.change(apply_preset, inputs=preset,
                  outputs=[shape, px, py, pz, vx, vy, vz])
    run_btn.click(fracture,
                  inputs=[shape, px, py, pz, vx, vy, vz, seed, gravity],
                  outputs=[video, model3d, summary, info_json])


if __name__ == "__main__":
    demo.launch()
