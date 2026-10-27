# %%
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

'''
This program is meant to illustrate the pixel size required vs camera resolution. 
The parameters are a 1km distance, using a 135mm lens, as well as each LED being required to fill 3 pixels of the camera.
The lens to camera combination could be better optomized, but keeping focal length constant is necessary for the equation.
'''

#hard coded camera specs of the DJI Inspire 3
SENSOR_WIDTH_MM = 36.0  # 35mm Full-Frame width
SENSOR_HEIGHT_MM = 23.98  # 35mm Full-Frame height (8K 3:2 aspect ratio)
FOCAL_LENGTH_MM = 135.0  # Fixed lens focal length
DISTANCE_M = 1000.0  # Fixed distance to target (1 km)
K_SAMPLES = 3.0  # Camera sensor pixels per LED pixel module

# Your camera benchmark
CAMERA_RES_X = 8192
CAMERA_RES_Y = 5456
CAMERA_MP = 44.7

# ==============================================================================
# CLOSED-FORM DERIVATIONS (for D = 1000 m, f = 135 mm, W = 36 mm, k = 3 px)
# ==============================================================================
# Optical projection: s_cm = (k * D * W_sensor) / (f * N_x * 10) = 80,000 / N_x
# Since MP = N_x * N_y / 1e6 and N_y = N_x * (23.98 / 36.0):
#   N_x = sqrt(MP * 1e6 * (36.0 / 23.98))
#   s_cm = 65.29 / sqrt(MP)
#   MP   = 4263.11 / (s_cm ^ 2)


def pixel_size_from_mp(mp):
  """Computes min LED pixel size (cm) for a given camera resolution in MP."""
  return 65.2925 / np.sqrt(mp)


def mp_from_pixel_size(s_cm):
  """Computes required camera resolution (MP) for a given LED pixel size in cm."""
  return 4263.11 / (s_cm**2)


# ==============================================================================
# DUAL-PERSPECTIVE PLOTTING (High-Detail View)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(
    f"LED Pixel Size vs. Camera Resolution at D = {int(DISTANCE_M)} m (f ="
    f" {int(FOCAL_LENGTH_MM)} mm Lens, k = {K_SAMPLES:.0f} px)",
    fontsize=13,
    fontweight="bold",
)

# ------------------------------------------------------------------------------
# PANEL 1: LED Pixel Size (cm) vs. Camera Resolution (MP)
# ------------------------------------------------------------------------------
mp_range = np.linspace(10, 100, 500)
pixel_sizes = pixel_size_from_mp(mp_range)

ax1.plot(
    mp_range,
    pixel_sizes,
    color="navy",
    linewidth=2.2,
    label="Min LED Pixel Size Curve",
)

# Reference cameras
ref_cameras = [
    (12.0, "12 MP (A7S III)"),
    (24.0, "24 MP (Standard FF)"),
    (44.7, "44.7 MP (DJI Inspire 3)"),
    (61.0, "61 MP (A7R V)"),
    (100.0, "100 MP (Medium Format)"),
]

for mp, label in ref_cameras:
  s_val = pixel_size_from_mp(mp)
  color = "darkred" if mp == CAMERA_MP else "darkslategrey"
  ax1.scatter([mp], [s_val], color=color, s=40, zorder=5)
  ax1.annotate(
      f"{label}\n{s_val:.1f} cm",
      (mp, s_val),
      textcoords="offset points",
      xytext=(0, 12 if mp != CAMERA_MP else -28),
      ha="center",
      fontsize=8,
      fontweight="bold" if mp == CAMERA_MP else "normal",
  )

# Target benchmark lines
ax1.axhline(
    10.0,
    color="crimson",
    linestyle="--",
    linewidth=1.2,
    alpha=0.85,
    label="10 cm Target",
)
ax1.axhline(
    15.0,
    color="orange",
    linestyle="--",
    linewidth=1.2,
    alpha=0.85,
    label="15 cm Max Cap",
)

ax1.set_xlim(10, 100)
ax1.set_ylim(0, 25)
ax1.set_xlabel("Camera Resolution (Megapixels)", fontsize=11)
ax1.set_ylabel("Minimum LED Pixel Size (cm)", fontsize=11)
ax1.set_title(
    "How Big the LED Pixel Must Be\nfor a Given Camera Sensor", fontsize=11
)

ax1.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax1.xaxis.set_minor_locator(ticker.MultipleLocator(2))
ax1.yaxis.set_major_locator(ticker.MultipleLocator(2.5))
ax1.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax1.grid(which="major", linestyle="-", linewidth=0.7, alpha=0.7)
ax1.grid(which="minor", linestyle=":", linewidth=0.4, alpha=0.4)
ax1.legend(loc="upper right", framealpha=0.9)

# ------------------------------------------------------------------------------
# PANEL 2: Required Camera Resolution (MP) vs. LED Pixel Size (cm)
# ------------------------------------------------------------------------------
s_range = np.linspace(5.5, 20.0, 500)
mp_needed = mp_from_pixel_size(s_range)

ax2.plot(
    s_range,
    mp_needed,
    color="forestgreen",
    linewidth=2.2,
    label="Required Camera Resolution",
)

# Reference pixel sizes
ref_pixels = [(10.0, 42.63), (15.0, 18.95)]
for s_cm, req_mp in ref_pixels:
  ax2.scatter([s_cm], [req_mp], color="crimson", s=45, zorder=5)
  ax2.annotate(
      f"{s_cm:.0f} cm Pixel\n{req_mp:.1f} MP",
      (s_cm, req_mp),
      textcoords="offset points",
      xytext=(20, 10),
      ha="left",
      fontsize=8.5,
      fontweight="bold",
  )

# Your camera reference line
ax2.axhline(
    CAMERA_MP,
    color="darkred",
    linestyle="--",
    linewidth=1.2,
    alpha=0.85,
    label=f"DJI Inspire 3 ({CAMERA_MP} MP)",
)

ax2.set_xlim(5.5, 20.0)
ax2.set_ylim(0, 120)
ax2.set_xlabel("LED Pixel Size (cm)", fontsize=11)
ax2.set_ylabel("Required Camera Resolution (Megapixels)", fontsize=11)
ax2.set_title(
    "Camera Resolution Needed\nfor a Given Physical Pixel Size", fontsize=11
)

ax2.xaxis.set_major_locator(ticker.MultipleLocator(2.0))
ax2.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax2.yaxis.set_major_locator(ticker.MultipleLocator(20.0))
ax2.yaxis.set_minor_locator(ticker.MultipleLocator(5.0))
ax2.grid(which="major", linestyle="-", linewidth=0.7, alpha=0.7)
ax2.grid(which="minor", linestyle=":", linewidth=0.4, alpha=0.4)
ax2.legend(loc="upper right", framealpha=0.9)

plt.tight_layout()

# Save plot to current working directory
output_filename = "pixel_size_vs_resolution_1000m.png"
plt.savefig(output_filename, dpi=300)
print(f"Plot saved successfully as '{output_filename}'.")

plt.show()
