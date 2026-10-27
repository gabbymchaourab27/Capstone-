import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

'''
This code is meant to solve for the focal length required to view a pixel of nxn dimesions
 at some distance. The ideal benchmark I set was for the distance to be 1km with the pixel being a 10cm X 10cm led panel.
This program is meant to find the minumum detectability given that the led grid must occupy at least 3 camera pixels to be detected.
'''

#Camera specifications for the DJI Inspire 3
SENSOR_WIDTH_MM = 36.0  # 35mm Full-Frame width (8K 3:2 mode)
SENSOR_HEIGHT_MM = 23.98  # 35mm Full-Frame height (8K 3:2 mode)
RES_X_PX = 8192  # Max photo horizontal resolution
RES_Y_PX = 5456  # Max photo vertical resolution
EFFECTIVE_MP = 44.7  # Megapixels

# Calculated sensor pixel pitch (μm)
PIXEL_PITCH_UM = (SENSOR_WIDTH_MM / RES_X_PX) * 1000.0  # ≈ 4.395 μm

# Sampling criteria: sensor pixels needed per LED module for reliable decoding
K_SAMPLES = 3.0

# Lens focal lengths to simulate (mm)
FOCAL_LENGTHS_MM = [35, 50, 85, 135, 200, 400]
MAX_DISTANCE_M = 1000.0


# ==============================================================================
# CORE EQUATION
# ==============================================================================
def calc_required_led_pixel_size(distance_m, focal_length_mm, k=K_SAMPLES):
  """Computes required physical LED pixel width (in meters) to span

  k camera sensor pixels at a given distance.
  """
  return (k * distance_m * (SENSOR_WIDTH_MM / 1000.0)) / (
      (focal_length_mm / 1000.0) * RES_X_PX
  )


# ==============================================================================
# VISUALIZATION (TUNED Y-AXIS SCALE)
# ==============================================================================
distances = np.linspace(5, MAX_DISTANCE_M, 1000)

fig, ax = plt.subplots(figsize=(11, 6.5))

for f in FOCAL_LENGTHS_MM:
  pixel_sizes_cm = calc_required_led_pixel_size(distances, f, K_SAMPLES) * 100.0
  ax.plot(distances, pixel_sizes_cm, label=f"{f} mm lens", linewidth=2)

# Reference benchmarks
ax.axhline(
    10.0,
    color="crimson",
    linestyle="--",
    linewidth=1.8,
    label="10 cm Target Pixel Benchmark",
)
ax.axvline(1000.0, color="gray", linestyle=":", alpha=0.7)

# --- Enhanced Y-Axis Detail ---
# Capping at 40 cm focuses on the relevant region (0 to 30 cm) around the 10 cm target
ax.set_ylim(0, 40)
ax.set_xlim(0, MAX_DISTANCE_M)

# Explicit tick spacing for precise reading:
# Major ticks every 5 cm, minor ticks every 1 cm
ax.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))
ax.xaxis.set_major_locator(ticker.MultipleLocator(100.0))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(20.0))

# Dual grid (major and subtle minor) for high-precision inspection
ax.grid(which="major", linestyle="-", linewidth=0.75, alpha=0.7)
ax.grid(which="minor", linestyle=":", linewidth=0.5, alpha=0.4)

ax.set_title(
    f"Required LED Pixel Size vs. Distance (High-Detail View)\n"
    f"Sensor: 36 × 23.98 mm | {RES_X_PX} × {RES_Y_PX} ({EFFECTIVE_MP} MP) |"
    f" Sampling: {K_SAMPLES:.0f} px/module",
    fontsize=12,
    fontweight="bold",
)
ax.set_xlabel("Distance to Camera (m)", fontsize=11)
ax.set_ylabel("Minimum Required LED Pixel Size (cm)", fontsize=11)

ax.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.show()
