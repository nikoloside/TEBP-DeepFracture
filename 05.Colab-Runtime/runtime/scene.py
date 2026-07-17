"""Scene preview + click-to-shoot ray casting for the game-style demo."""

import numpy as np

from .collision import SPHERE_RADIUS

WIDTH, HEIGHT = 640, 480
YAW, PITCH, DISTANCE = 50.0, -25.0, 3.2
FOV = 45.0
SPAWN_DISTANCE = 2.6   # distance from the aim point back toward the camera


def _matrices(p, width=WIDTH, height=HEIGHT):
    view = p.computeViewMatrixFromYawPitchRoll(
        cameraTargetPosition=[0, 0, 0], distance=DISTANCE,
        yaw=YAW, pitch=PITCH, roll=0, upAxisIndex=1)
    proj = p.computeProjectionMatrixFOV(fov=FOV, aspect=width / height,
                                        nearVal=0.05, farVal=20)
    return view, proj


def camera_ray(p, px, py, width=WIDTH, height=HEIGHT):
    """Ray (origin, direction) in world space through pixel (px, py)."""
    view, _ = _matrices(p, width, height)
    V = np.array(view).reshape(4, 4).T          # row-major world->cam
    R = V[:3, :3]
    eye = -R.T @ V[:3, 3]

    x_ndc = 2.0 * px / width - 1.0
    y_ndc = 1.0 - 2.0 * py / height
    tan_half = np.tan(np.radians(FOV) / 2.0)
    cam_dir = np.array([x_ndc * tan_half * (width / height),
                        y_ndc * tan_half,
                        -1.0])
    world_dir = R.T @ cam_dir
    world_dir /= np.linalg.norm(world_dir)
    return eye, world_dir


def render_preview(target_obj, aim_world=None, sphere_pos=None,
                   width=WIDTH, height=HEIGHT):
    """Render the scene: target at origin, optional aim marker / sphere."""
    import pybullet as p

    cid = p.connect(p.DIRECT)
    try:
        vis_t = p.createVisualShape(p.GEOM_MESH, fileName=target_obj,
                                    rgbaColor=[0.35, 0.75, 0.35, 1],
                                    physicsClientId=cid)
        p.createMultiBody(baseMass=0, baseVisualShapeIndex=vis_t,
                          basePosition=[0, 0, 0], physicsClientId=cid)
        if aim_world is not None:
            vis_m = p.createVisualShape(p.GEOM_SPHERE, radius=0.05,
                                        rgbaColor=[1, 0.85, 0.1, 1],
                                        physicsClientId=cid)
            p.createMultiBody(baseMass=0, baseVisualShapeIndex=vis_m,
                              basePosition=list(aim_world), physicsClientId=cid)
        if sphere_pos is not None:
            vis_s = p.createVisualShape(p.GEOM_SPHERE, radius=SPHERE_RADIUS,
                                        rgbaColor=[0.85, 0.2, 0.2, 1],
                                        physicsClientId=cid)
            p.createMultiBody(baseMass=0, baseVisualShapeIndex=vis_s,
                              basePosition=list(sphere_pos), physicsClientId=cid)

        view, proj = _matrices(p, width, height)
        _, _, rgb, _, _ = p.getCameraImage(width, height, view, proj,
                                           renderer=p.ER_TINY_RENDERER,
                                           physicsClientId=cid)
        frame = np.reshape(np.asarray(rgb, dtype=np.uint8),
                           (height, width, 4))[:, :, :3]
        return frame
    finally:
        p.disconnect(cid)


def click_to_shot(target_obj, px, py, speed, width=WIDTH, height=HEIGHT):
    """Map an image click to a projectile (position, velocity, hit point).

    Returns None if the click ray misses the target mesh.
    """
    import pybullet as p

    cid = p.connect(p.DIRECT)
    try:
        col_t = p.createCollisionShape(p.GEOM_MESH, fileName=target_obj,
                                       physicsClientId=cid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=col_t,
                          basePosition=[0, 0, 0], physicsClientId=cid)
        eye, ray = camera_ray(p, px, py, width, height)
        hits = p.rayTest(list(eye), list(eye + ray * 20.0), physicsClientId=cid)
        if not hits or hits[0][0] < 0:
            return None
        hit_pos = np.array(hits[0][3])
        spawn = hit_pos - ray * SPAWN_DISTANCE
        vel = ray * float(speed)
        return {"sphere_pos": spawn.tolist(),
                "sphere_vel": vel.tolist(),
                "hit_pos": hit_pos.tolist()}
    finally:
        p.disconnect(cid)
