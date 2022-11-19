import pyvista as pyv


COLORS = {  'edges' : '#f7f7f7', 'faces' : '#f4a582',
            'primal birth' : '#1a9641', 'primal death' : '#ca0020',
            'dual birth' : '#0571b0', 'dual death' : '#e66101'}

KWARGS = {'edges' : {'color' : COLORS['edges'], 'opacity' : 0.2},
            'faces' : {'color' : COLORS['faces'], 'opacity' : 0.03}}


def plot_complex(vfig, K, B=set(), **kwargs):
    kwargs = {**KWARGS, **kwargs}
    meshes = {'faces' : pyv.PolyData(K.P, faces=[l for s in K(2) for l in [len(s)] + list(s) if not s in B]),
                'edges' : pyv.PolyData(K.P, lines=[l for s in K(1) for l in [len(s)] + list(s) if not s in B])}
    return meshes, {k : vfig.add_mesh(v, **kwargs[k]) for k,v in meshes.items()}

def plot_cells(vfig, K, cells, dim, **kwargs):
    mesh = (pyv.PolyData(K.P, lines=[l for s in cells for l in [len(s)] + list(s)]) if dim == 1
        else pyv.PolyData(K.P, faces=[l for s in cells for l in [len(s)] + list(s)]) if dim == 2
        else pyv.PolyData(K.P[cells]))
    return mesh, vfig.add_mesh(mesh, **kwargs)
