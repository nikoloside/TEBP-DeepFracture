"""PyBullet collision runtime: detect the impact, then re-simulate fragments.

Ported from TEBP-DeepFracture 04.Run-time (BreakableWorld / DynamicObject),
trimmed to a single breakable target hit by a sphere projectile.
"""

import os
import tempfile

import numpy as np

TIMESTEP = 1.0 / 250.0
IMPULSE_THRESHOLD = 2000.0   # BreakableWorld.threshold
IMPULSE_MAX = 10000.0        # predict-runtime.py impulseMax
SPHERE_RADIUS = 0.18
SPHERE_MASS = 1.0


def _rotate(p, quat, vec):
    mat = np.array(p.getMatrixFromQuaternion(quat)).reshape(3, 3)
    return mat @ np.asarray(vec)


def _camera(p, width=480, height=360, yaw=50.0, pitch=-25.0, distance=3.2):
    view = p.computeViewMatrixFromYawPitchRoll(
        cameraTargetPosition=[0, 0, 0], distance=distance,
        yaw=yaw, pitch=pitch, roll=0, upAxisIndex=1)
    proj = p.computeProjectionMatrixFOV(fov=45, aspect=width / height,
                                        nearVal=0.05, farVal=20)
    return view, proj


def _snapshot(p, width=480, height=360):
    view, proj = _camera(p, width, height)
    _, _, rgb, _, _ = p.getCameraImage(width, height, view, proj,
                                       renderer=p.ER_TINY_RENDERER)
    frame = np.reshape(np.asarray(rgb, dtype=np.uint8), (height, width, 4))[:, :, :3]
    return frame


def run_fracture_sim(target_obj, fragment_builder,
                     sphere_pos, sphere_vel,
                     gravity=-5.0, seconds_after=3.0,
                     frame_stride=10, width=480, height=360,
                     max_impact_steps=2500):
    """Full runtime loop.

    fragment_builder(pos_local, dir_local, imp_norm, imp_raw) is called at
    impact time and must return a list of fragment mesh files (.obj) in the
    target's local frame.

    Returns (frames, info) where frames is a list of HxWx3 uint8 arrays and
    info a dict with the collision embedding; info is None if nothing hit.
    """
    import pybullet as p

    cid = p.connect(p.DIRECT)
    try:
        p.setTimeStep(TIMESTEP, physicsClientId=cid)
        p.setGravity(0, 0, 0, physicsClientId=cid)

        col_t = p.createCollisionShape(p.GEOM_MESH, fileName=target_obj)
        vis_t = p.createVisualShape(p.GEOM_MESH, fileName=target_obj,
                                    rgbaColor=[0.35, 0.75, 0.35, 1])
        body_t = p.createMultiBody(baseMass=1.0,
                                   baseCollisionShapeIndex=col_t,
                                   baseVisualShapeIndex=vis_t,
                                   basePosition=[0, 0, 0])

        col_s = p.createCollisionShape(p.GEOM_SPHERE, radius=SPHERE_RADIUS)
        vis_s = p.createVisualShape(p.GEOM_SPHERE, radius=SPHERE_RADIUS,
                                    rgbaColor=[0.85, 0.2, 0.2, 1])
        body_s = p.createMultiBody(baseMass=SPHERE_MASS,
                                   baseCollisionShapeIndex=col_s,
                                   baseVisualShapeIndex=vis_s,
                                   basePosition=list(sphere_pos))
        p.resetBaseVelocity(body_s, list(sphere_vel), [0, 0, 0])

        frames = [_snapshot(p, width, height)]
        info = None
        last_lvel, last_avel = (0, 0, 0), (0, 0, 0)

        # --- phase A: fly until impact -----------------------------------
        for step in range(max_impact_steps):
            last_lvel, last_avel = p.getBaseVelocity(body_t)
            p.stepSimulation()
            if step % frame_stride == 0:
                frames.append(_snapshot(p, width, height))

            contacts = [c for c in p.getContactPoints()
                        if {c[1], c[2]} == {body_t, body_s}]
            total_impulse = sum(c[9] for c in contacts)
            if total_impulse > IMPULSE_THRESHOLD:
                impact = max(contacts, key=lambda c: c[9])
                tar_pos, tar_orn = p.getBasePositionAndOrientation(body_t)

                # DynamicObject.startFracturing: to target-local frame
                rel = np.asarray(impact[5]) - np.asarray(tar_pos)
                normal = np.asarray(impact[7])
                if impact[2] != body_t:
                    normal = -normal
                _, inv_orn = p.invertTransform([0, 0, 0], tar_orn)
                pos_local = _rotate(p, inv_orn, rel)
                dir_local = _rotate(p, inv_orn, normal)
                imp_raw = impact[9]
                imp_norm = min(imp_raw, IMPULSE_MAX) / IMPULSE_MAX * 2.0 - 1.0

                info = {
                    "impact_step": step,
                    "pos_local": pos_local.tolist(),
                    "dir_local": dir_local.tolist(),
                    "impulse_raw": float(imp_raw),
                    "impulse_total": float(total_impulse),
                    "impulse_norm": float(imp_norm),
                    "target_pos": list(tar_pos),
                    "target_orn": list(tar_orn),
                }
                break
        if info is None:
            return frames, None

        # --- neural fracture prediction ----------------------------------
        fragment_files = fragment_builder(info["pos_local"], info["dir_local"],
                                          info["impulse_norm"], info["impulse_raw"])
        info["n_fragments"] = len(fragment_files)

        # --- phase B: swap target for fragments, keep simulating ---------
        p.removeBody(body_t)
        n = max(len(fragment_files), 1)
        for frag_file in fragment_files:
            col_f = p.createCollisionShape(p.GEOM_MESH, fileName=frag_file)
            vis_f = p.createVisualShape(p.GEOM_MESH, fileName=frag_file)
            body_f = p.createMultiBody(baseMass=1.0 / n,
                                       baseCollisionShapeIndex=col_f,
                                       baseVisualShapeIndex=vis_f,
                                       basePosition=info["target_pos"],
                                       baseOrientation=info["target_orn"])
            p.resetBaseVelocity(body_f, list(last_lvel), [0, 0, 0])

        if gravity:
            p.setGravity(0, gravity, 0)
            plane_col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[8, 0.05, 8])
            p.createMultiBody(baseMass=0, baseCollisionShapeIndex=plane_col,
                              basePosition=[0, -1.15, 0])

        for step in range(int(seconds_after / TIMESTEP)):
            p.stepSimulation()
            if step % frame_stride == 0:
                frames.append(_snapshot(p, width, height))

        return frames, info
    finally:
        p.disconnect(cid)


def export_fragments_for_sim(fragments, out_dir=None):
    """Write fragment meshes as .obj files for PyBullet."""
    out_dir = out_dir or tempfile.mkdtemp(prefix="fragments-")
    os.makedirs(out_dir, exist_ok=True)
    files = []
    for i, mesh in enumerate(fragments):
        path = os.path.join(out_dir, f"frag_{i:03d}.obj")
        mesh.export(path)
        files.append(path)
    return files
