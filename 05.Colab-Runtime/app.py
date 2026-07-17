"""DeepFracture Runtime — game-style interactive brittle-fracture demo.

Click the target in the scene to shoot a projectile at it. The impact is
detected by PyBullet, encoded as the paper's 7-D collision embedding, the
per-shape VQ-VAE (hf.co/nikoloside/deepfracture) predicts the fracture, a
pure-Python watershed segments it into fragments, and the fragments fall
back into the simulation.
"""

import queue
import threading

import gradio as gr

from runtime.pipeline import run_demo
from runtime.predictor import SHAPES, download_asset, load_models
from runtime.scene import click_to_shot, render_preview

HEADER = """
# 💥 DeepFracture Runtime — shooting gallery

**👆 Click anywhere on the object to shoot it.** A projectile flies at the
point you click; the impact becomes a 7-D collision embedding, the VQ-VAE
([weights](https://huggingface.co/nikoloside/deepfracture)) predicts the
fracture pattern, watershed segmentation extracts the fragments, and they
tumble back into the rigid-body simulation.

[DeepFracture (CGF 2025)](https://nikoloside.graphics/deepfracture/) ·
[Far-From-Boundary Fields (SMI 2026)](https://nikoloside.graphics/far-from-boundary-fields/) ·
[Code](https://github.com/nikoloside/TEBP-DeepFracture)
"""

_preview_cache = {}


def scene_image(shape):
    if shape not in _preview_cache:
        _preview_cache[shape] = render_preview(download_asset(f"objs/{shape}.obj"))
    return _preview_cache[shape]


def warmup():
    try:
        load_models("squirrel")
        scene_image("squirrel")
    except Exception as e:  # noqa: BLE001 — warmup is best-effort
        print("warmup failed:", e)


threading.Thread(target=warmup, daemon=True).start()


def load_scene(shape):
    yield gr.update(), f"⏳ Loading **{shape}** scene…"
    yield scene_image(shape), f"🎯 Ready — click the **{shape}** to shoot!"


def shoot(shape, speed, seed, gravity, evt: gr.SelectData):
    px, py = evt.index
    target_obj = download_asset(f"objs/{shape}.obj")

    shot = click_to_shot(target_obj, px, py, speed)
    if shot is None:
        yield (gr.update(), "❌ Missed — click **on** the object itself.",
               gr.update(), gr.update(), gr.update())
        return

    aimed = render_preview(target_obj, aim_world=shot["hit_pos"],
                           sphere_pos=shot["sphere_pos"])
    yield (aimed,
           f"🎯 Locked on `{[round(v, 2) for v in shot['hit_pos']]}` — firing at speed {speed:.0f}…",
           None, None, None)

    events = queue.Queue()
    box = {}

    def worker():
        try:
            box["out"] = run_demo(shape, shot["sphere_pos"], shot["sphere_vel"],
                                  seed=int(seed), gravity=-5.0 if gravity else 0.0,
                                  status_cb=events.put)
        except Exception as e:  # noqa: BLE001 — surfaced to the UI below
            box["out"] = {"error": f"runtime crashed: {e}"}
        finally:
            events.put(None)

    threading.Thread(target=worker, daemon=True).start()

    log = []
    while True:
        msg = events.get()
        if msg is None:
            break
        log.append(msg)
        yield (gr.update(), "\n\n".join(log), gr.update(), gr.update(), gr.update())

    out = box.get("out", {"error": "no result"})
    if "error" in out:
        yield (gr.update(), "\n\n".join(log + [f"❌ {out['error']}"]),
               gr.update(), gr.update(), gr.update())
        return

    info = out["info"]
    log.append(f"✅ **{info['n_fragments']} fragments** · impulse {info['impulse_raw']:.0f} "
               f"(norm {info['impulse_norm']:+.2f}) · codebook #{info['codebook_index']}")
    yield (gr.update(), "\n\n".join(log), out["video"], out["glb"], info)


with gr.Blocks(title="DeepFracture Runtime") as demo:
    gr.Markdown(HEADER)

    with gr.Row():
        with gr.Column(scale=3):
            scene = gr.Image(label="🎯 Click the target to shoot", interactive=False)
            status = gr.Markdown("⏳ Loading scene… (first launch downloads the "
                                 "model weights, ~190 MB — give it a minute)")
            with gr.Row():
                shape = gr.Dropdown(SHAPES, value="squirrel", label="Target shape")
                speed = gr.Slider(20, 120, 65, step=1, label="Projectile speed")
            with gr.Row():
                seed = gr.Number(42, label="Latent seed (change it for a different break)",
                                 precision=0)
                gravity = gr.Checkbox(True, label="Gravity after fracture")

        with gr.Column(scale=2):
            video = gr.Video(label="Runtime replay", autoplay=True, loop=True)
            model3d = gr.Model3D(label="Fragments (drag to inspect)",
                                 clear_color=[0.95, 0.95, 0.95, 1.0])
            with gr.Accordion("Collision embedding (network input)", open=False):
                info_json = gr.JSON()

    demo.load(load_scene, inputs=shape, outputs=[scene, status])
    shape.change(load_scene, inputs=shape, outputs=[scene, status])
    scene.select(shoot, inputs=[shape, speed, seed, gravity],
                 outputs=[scene, status, video, model3d, info_json])


if __name__ == "__main__":
    demo.launch()
