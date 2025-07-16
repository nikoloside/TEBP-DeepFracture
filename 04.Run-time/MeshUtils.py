import numpy as np
import trimesh

def sort_impulse(e):
    return e[9]

def load_mesh(filepath):
    mesh = trimesh.load(filepath, process=False)
    return mesh.vertices, mesh.faces

class Quaternion:
    def __init__(self, q, is_xyzw_order=True):
        """
        Initialize a quaternion
        Args:
            q: quaternion values
            is_xyzw_order: if True, input is in [x,y,z,w] order; if False, input is in [w,x,y,z] order
        """
        if is_xyzw_order:
            x, y, z, w = q
            self.q = np.array([w, x, y, z])  # internally always store as [w,x,y,z]
        else:
            self.q = np.array(q)  # already in [w,x,y,z] order

    @staticmethod
    def from_xyzw(q):
        """Create quaternion from [x,y,z,w] order"""
        return Quaternion(q, is_xyzw_order=True)

    @staticmethod
    def from_wxyz(q):
        """Create quaternion from [w,x,y,z] order"""
        return Quaternion(q, is_xyzw_order=False)

    def to_xyzw(self):
        """Convert to [x,y,z,w] order"""
        return [self.q[1], self.q[2], self.q[3], self.q[0]]

    def to_wxyz(self):
        """Get quaternion in [w,x,y,z] order"""
        return self.q.tolist()

    def rotate(self, v):
        """Rotate vector v (3D) by quaternion"""
        w, x, y, z = self.q
        t = 2 * np.cross([x, y, z], v)
        return v + w * t + np.cross([x, y, z], t)

    def conjugate(self):
        """Return the conjugate of the quaternion [w,x,y,z] -> [w,-x,-y,-z]"""
        w, x, y, z = self.q
        return Quaternion([w, -x, -y, -z], is_xyzw_order=False)

def form_mesh(vertices, faces):
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def merge_meshes(mesh_list):
    # Merge a list of trimesh.Mesh objects
    return trimesh.util.concatenate(mesh_list)

def save_mesh(filepath, mesh):
    mesh.export(filepath) 
