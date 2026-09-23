"""
Square steel block embedded in a rubber sheet, pulled upward.

Plane-stress linear elasticity solved with bilinear (Q4) finite elements:
    -div(sigma(u)) = rho * g        in Omega        (body force = weight)
    sigma * n      = sigma_0 * e_y  on the top edge (pulled up)
    u_y = 0                         on the bottom edge (rests on a table)

The material coefficients jump by 5 orders of magnitude across the rubber/steel
interface -> no classical solution; the weak form in H^1 is what FEM solves.
Produces figures/steel_in_rubber.png: labelled schematic + computed stress field.
"""
import os
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch

# ----------------------------------------------------------------------------- setup
W, H = 1.0, 1.4            # rubber sheet size [m]
a = 0.3                    # steel square side [m]
x0, x1 = 0.35, 0.65        # steel x-extent
y0, y1 = 0.55, 0.85        # steel y-extent
nx, ny = int(os.environ.get('NX', 80)), int(os.environ.get('NY', 112))  # steel edges must fall on mesh lines
sigma0 = 0.1e6             # applied traction on top edge [Pa]  (0.1 MPa)
g = 9.81

# material: rubber / steel  (E [Pa], nu, rho [kg/m^3])
mat = {
    "rubber": dict(E=2.0e6,   nu=0.49, rho=1100.0),
    "steel":  dict(E=200.0e9, nu=0.30, rho=7850.0),
}

def D_plane_stress(E, nu):
    return E / (1 - nu**2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])

# ----------------------------------------------------------------------------- mesh
xs = np.linspace(0, W, nx + 1)
ys = np.linspace(0, H, ny + 1)
X, Y = np.meshgrid(xs, ys)                        # (ny+1, nx+1)
nodes = np.column_stack([X.ravel(), Y.ravel()])    # node id = j*(nx+1) + i
nn = len(nodes)

def nid(i, j):
    return j * (nx + 1) + i

elems = np.array([[nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1)]
                  for j in range(ny) for i in range(nx)])
cent = nodes[elems].mean(axis=1)
is_steel = (cent[:, 0] > x0) & (cent[:, 0] < x1) & (cent[:, 1] > y0) & (cent[:, 1] < y1)

# ----------------------------------------------------------------------------- Q4 element
gp = np.array([-1, 1]) / np.sqrt(3)
def shape_grad(xi, eta):
    dN = 0.25 * np.array([[-(1 - eta), -(1 - xi)],
                          [ (1 - eta), -(1 + xi)],
                          [ (1 + eta),  (1 + xi)],
                          [-(1 + eta),  (1 - xi)]])
    return dN                                       # dN/dxi, dN/deta  (4x2)

def element_matrices(xy, D, rho):
    """stiffness (8x8) and body-force vector (8,) for gravity -rho*g*e_y"""
    K = np.zeros((8, 8)); f = np.zeros(8)
    for xi in gp:
        for eta in gp:
            dN = shape_grad(xi, eta)
            J = dN.T @ xy                           # 2x2
            detJ = np.linalg.det(J)
            dNdx = dN @ np.linalg.inv(J)            # 4x2
            B = np.zeros((3, 8))
            B[0, 0::2] = dNdx[:, 0]
            B[1, 1::2] = dNdx[:, 1]
            B[2, 0::2] = dNdx[:, 1]
            B[2, 1::2] = dNdx[:, 0]
            K += B.T @ D @ B * detJ
            N = 0.25 * np.array([(1 - xi) * (1 - eta), (1 + xi) * (1 - eta),
                                 (1 + xi) * (1 + eta), (1 - xi) * (1 + eta)])
            f[1::2] += -rho * g * N * detJ
    return K, f

# ----------------------------------------------------------------------------- assemble
rows, cols, vals = [], [], []
F = np.zeros(2 * nn)
Dr, Ds = D_plane_stress(**{k: mat["rubber"][k] for k in ("E", "nu")}), \
         D_plane_stress(**{k: mat["steel"][k] for k in ("E", "nu")})
for e, conn in enumerate(elems):
    D, rho = (Ds, mat["steel"]["rho"]) if is_steel[e] else (Dr, mat["rubber"]["rho"])
    Ke, fe = element_matrices(nodes[conn], D, rho)
    dofs = np.column_stack([2 * conn, 2 * conn + 1]).ravel()
    rows.append(np.repeat(dofs, 8)); cols.append(np.tile(dofs, 8)); vals.append(Ke.ravel())
    F[dofs] += fe
K = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                  shape=(2 * nn, 2 * nn))

# top-edge traction sigma0 upward -> consistent nodal loads (uniform, trapezoid rule)
top = [nid(i, ny) for i in range(nx + 1)]
dx = W / nx
F[2 * np.array(top) + 1] += sigma0 * dx
F[2 * top[0] + 1] -= sigma0 * dx / 2; F[2 * top[-1] + 1] -= sigma0 * dx / 2

# Dirichlet: bottom edge u_y = 0, bottom-centre node u_x = 0 (roller support)
bottom = [nid(i, 0) for i in range(nx + 1)]
fixed = [2 * n + 1 for n in bottom] + [2 * nid(nx // 2, 0)]
free = np.setdiff1d(np.arange(2 * nn), fixed)
u = np.zeros(2 * nn)
u[free] = spla.spsolve(K[free][:, free].tocsc(), F[free])
U = u.reshape(-1, 2)

# ----------------------------------------------------------------------------- stresses (element centroid)
stress = np.zeros((len(elems), 3))
for e, conn in enumerate(elems):
    D = Ds if is_steel[e] else Dr
    dN = shape_grad(0.0, 0.0)
    J = dN.T @ nodes[conn]; dNdx = dN @ np.linalg.inv(J)
    B = np.zeros((3, 8))
    B[0, 0::2] = dNdx[:, 0]; B[1, 1::2] = dNdx[:, 1]
    B[2, 0::2] = dNdx[:, 1]; B[2, 1::2] = dNdx[:, 0]
    stress[e] = D @ B @ U[conn].ravel()
sxx, syy, txy = stress.T
svm = np.sqrt(sxx**2 - sxx * syy + syy**2 + 3 * txy**2)

# tractions on the four faces of the steel square (elements in the rubber, one layer out)
def face_mean(mask, comp):
    return comp[mask].mean() / sigma0
dy = H / ny
above = (~is_steel) & (cent[:, 1] > y1) & (cent[:, 1] < y1 + dy) & (cent[:, 0] > x0) & (cent[:, 0] < x1)
below = (~is_steel) & (cent[:, 1] < y0) & (cent[:, 1] > y0 - dy) & (cent[:, 0] > x0) & (cent[:, 0] < x1)
left  = (~is_steel) & (cent[:, 0] < x0) & (cent[:, 0] > x0 - dx) & (cent[:, 1] > y0) & (cent[:, 1] < y1)
right = (~is_steel) & (cent[:, 0] > x1) & (cent[:, 0] < x1 + dx) & (cent[:, 1] > y0) & (cent[:, 1] < y1)
faces = dict(
    top=dict(normal=face_mean(above, syy), shear=np.abs(txy[above]).mean() / sigma0),
    bottom=dict(normal=face_mean(below, syy), shear=np.abs(txy[below]).mean() / sigma0),
    left=dict(normal=face_mean(left, sxx), shear=np.abs(txy[left]).mean() / sigma0),
    right=dict(normal=face_mean(right, sxx), shear=np.abs(txy[right]).mean() / sigma0),
)
corner_r = max(svm[(~is_steel) & (np.abs(cent[:, 0] - x0) < dx) & (np.abs(cent[:, 1] - y1) < dy)]) / sigma0
inside_steel = svm[is_steel].mean() / sigma0
far_field = svm[(~is_steel) & (cent[:, 1] > 1.25)].mean() / sigma0
strain_rubber = (U[top, 1].mean()) / H
weight_steel = mat["steel"]["rho"] * g * a * a
print(f"rubber elongation : {100*strain_rubber:.1f} %   steel strain ~ {sigma0/mat['steel']['E']:.1e}")
print(f"far-field |σ|/σ0  : {far_field:.2f}")
print(f"mean |σ| in steel : {inside_steel:.2f} σ0")
print(f"corner peak       : {corner_r:.1f} σ0 (mesh-dependent, grows with refinement)")
for k, v in faces.items():
    print(f"  {k:6s} face  normal {v['normal']:+.2f} σ0   |shear| {v['shear']:.2f} σ0")
print(f"steel weight / applied force = {weight_steel/(sigma0*W):.3f}")

# ----------------------------------------------------------------------------- figure
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
C_RUBBER, C_STEEL, C_FORCE, C_GRAV = "#b9ead6", "#c9c9c4", "#eb6834", "#4a3aa7"
blue_ramp = LinearSegmentedColormap.from_list(
    "seq-blue", ["#f4f8fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])

fig, (axL, axR) = plt.subplots(1, 2, figsize=(14, 7.6), gridspec_kw=dict(width_ratios=[1.05, 1]))
fig.patch.set_facecolor("#fcfcfb")

# ---- left: schematic ---------------------------------------------------------
ax = axL
ax.set_facecolor("#fcfcfb")
ax.add_patch(Rectangle((0, 0), W, H, fc=C_RUBBER, ec=INK2, lw=1.2))
ax.add_patch(Rectangle((x0, y0), a, a, fc=C_STEEL, ec=INK, lw=1.6))

# pulling force on top edge
for xx in np.linspace(0.08, 0.92, 8):
    ax.add_patch(FancyArrowPatch((xx, H + 0.02), (xx, H + 0.16), arrowstyle="-|>",
                                 mutation_scale=14, color=C_FORCE, lw=1.8))
ax.text(W / 2, H + 0.20, r"pulled up: traction $\sigma_0 = 0.1$ MPa", ha="center", va="bottom",
        color=INK, fontsize=10.5)
# support at bottom
for xx in np.linspace(0.06, 0.94, 12):
    ax.add_patch(Polygon([[xx - 0.02, -0.06], [xx + 0.02, -0.06], [xx, 0]], fc=INK2, ec="none"))
ax.text(W / 2, -0.09, "rests on a table  ($u_y = 0$)", ha="center", va="top", color=INK2, fontsize=9.5)

# gravity
ax.add_patch(FancyArrowPatch((0.09, 1.30), (0.09, 1.12), arrowstyle="-|>", mutation_scale=12,
                             color=C_GRAV, lw=1.6))
ax.text(0.12, 1.21, r"$g$  (body force $\rho g$)", color=C_GRAV, fontsize=9.5, va="center")

# material labels
ax.text(0.05, 0.10, "RUBBER  (matrix)\n" r"$\rho \approx 1100$ kg/m$^3$" "\n" r"$E \approx 2$ MPa,  $\nu \approx 0.49$"
        f"\nstretches ≈ {100*strain_rubber:.0f} %", fontsize=9.5, color=INK, va="bottom",
        bbox=dict(boxstyle="round,pad=0.35", fc="#fcfcfb", ec=INK2, lw=0.8))
ax.text(x0 + a / 2, y0 + a / 2, "STEEL\n" r"$\rho \approx 7850$ kg/m$^3$" "\n" r"$E \approx 200$ GPa" "\n"
        r"$\nu \approx 0.3$" "\n(≈ rigid)", fontsize=8, color=INK, ha="center", va="center",
        linespacing=1.25)

# face tractions (arrows drawn on the rubber side, pointing the way the rubber pulls the steel)
def face_arrow(p, q, color=C_FORCE):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, color=color, lw=1.5))
for xx in np.linspace(x0 + 0.04, x1 - 0.04, 5):
    face_arrow((xx, y1 + 0.005), (xx, y1 + 0.08))          # rubber above pulls top face up
    face_arrow((xx, y0 - 0.005), (xx, y0 - 0.08))          # rubber below pulls bottom face down
for yy in np.linspace(y0 + 0.06, y1 - 0.06, 3):
    face_arrow((x0 - 0.05, yy), (x0 - 0.005, yy))          # sides: rubber's Poisson contraction squeezes the steel
    face_arrow((x1 + 0.05, yy), (x1 + 0.005, yy))
# shear on the sides: rubber slides up relative to the rigid steel
for yy, dyy in [(y1 - 0.03, 0.05), (y0 + 0.03, -0.05)]:
    for xx in (x0 - 0.035, x1 + 0.035):
        face_arrow((xx, yy), (xx, yy + dyy), color=INK2)

ft = faces
ax.text(x1 + 0.09, y1 + 0.04, f"top face\n$\\sigma_n \\approx {ft['top']['normal']:+.1f}\\,\\sigma_0$ (tension)",
        fontsize=9, color=INK, va="center")
ax.text(x1 + 0.09, y0 - 0.04, f"bottom face\n$\\sigma_n \\approx {ft['bottom']['normal']:+.1f}\\,\\sigma_0$ (tension)",
        fontsize=9, color=INK, va="center")
ax.text(x0 - 0.10, y0 + a / 2, f"side faces\nshear $|\\tau| \\approx {ft['left']['shear']:.2f}\\,\\sigma_0$\n"
        f"$\\sigma_n \\approx {ft['left']['normal']:+.2f}\\,\\sigma_0$\n(slight squeeze)",
        fontsize=9, color=INK, va="center", ha="right", linespacing=1.3)
# corners
for (cx, cy) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
    ax.plot(cx, cy, marker="*", ms=10, color=C_FORCE, mec=INK, mew=0.6, zorder=5)
ax.annotate(r"corners: $\sigma \sim r^{\lambda-1}\to\infty$" "\n(interface-corner singularity)",
            xy=(x1, y1), xytext=(0.62, 1.08), fontsize=9.5, color=INK,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.16, H + 0.32)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Set-up and stress on each part of the steel square", fontsize=12, color=INK, loc="left")

# ---- right: computed field -----------------------------------------------------
ax = axR
ax.set_facecolor("#fcfcfb")
scale = 2.0                                        # deformation exaggeration
Xd = (nodes[:, 0] + scale * U[:, 0]).reshape(ny + 1, nx + 1)
Yd = (nodes[:, 1] + scale * U[:, 1]).reshape(ny + 1, nx + 1)
field = (svm / sigma0).reshape(ny, nx)
vmax = 2.0
pc = ax.pcolormesh(Xd, Yd, field, cmap=blue_ramp, vmin=0, vmax=vmax, shading="flat",
                   edgecolors="none", rasterized=True)
# steel outline (deformed)
ii0, ii1 = int(round(x0 / dx)), int(round(x1 / dx)); jj0, jj1 = int(round(y0 / dy)), int(round(y1 / dy))
px = np.concatenate([Xd[jj0, ii0:ii1 + 1], Xd[jj0:jj1 + 1, ii1], Xd[jj1, ii1:ii0 - 1:-1], Xd[jj1:jj0 - 1:-1, ii0]])
py = np.concatenate([Yd[jj0, ii0:ii1 + 1], Yd[jj0:jj1 + 1, ii1], Yd[jj1, ii1:ii0 - 1:-1], Yd[jj1:jj0 - 1:-1, ii0]])
ax.plot(px, py, color=INK, lw=1.4)
# undeformed outline for reference
ax.add_patch(Rectangle((0, 0), W, H, fill=False, ec=MUTED, lw=0.9, ls="--"))
cb = fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.03)
cb.set_label(r"$|\sigma|_{vM}\,/\,\sigma_0$   (clipped at 2)", color=INK2)
cb.ax.tick_params(colors=INK2)
ax.text(0.5, H + 0.17, f"far field ≈ {far_field:.1f} σ₀   ·   inside steel ≈ {inside_steel:.1f} σ₀   ·   "
        f"corner cell ≈ {corner_r:.0f} σ₀", ha="center", va="bottom", fontsize=9.5, color=INK2)
ax.set_xlim(-0.08, 1.14); ax.set_ylim(-0.05, H + 0.30)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"Computed stress field  (plane-stress FEM, {nx}×{ny} Q4, deformation ×{scale:.0f})",
             fontsize=12, color=INK, loc="left")

fig.text(0.01, 0.01,
         "Coefficients jump 10⁵× across the interface → no C² (strong) solution; the weak form in H¹ is what "
         "the FEM solves. Stress concentrates at the four interface corners (like a re-entrant corner) and "
         "refining the mesh makes the peak grow without bound.", fontsize=9, color=INK2, ha="left", va="bottom",
         wrap=True)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("figures/steel_in_rubber.png", dpi=170, facecolor=fig.get_facecolor())
print("saved figures/steel_in_rubber.png")
