import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

# ==============================================================================
# OPTICAL & SCENE SPECIFICATIONS (200 mm)
# ==============================================================================
SENSOR_WIDTH_MM = 36.0
SENSOR_HEIGHT_MM = 23.98
RES_X_PX = 8192
RES_Y_PX = 5456
FOCAL_LENGTH_MM = 200.0
DISTANCE_M = 1000.0

TARGET_SIZE_M = 0.10  # 10 cm x 10 cm LED panel
PIXEL_PITCH_M = (SENSOR_WIDTH_MM / RES_X_PX) / 1000.0  # ≈ 4.3945e-6 m

# Full Ground Coverage: FOV (Field of View)
ground_w_m = (SENSOR_WIDTH_MM * DISTANCE_M) / FOCAL_LENGTH_MM  # 180.00 m
ground_h_m = (SENSOR_HEIGHT_MM * DISTANCE_M) / FOCAL_LENGTH_MM  # 119.90 m
ground_area_sqm = ground_w_m * ground_h_m  # 21,582.00 m²

# GSD (Ground Sample Distance)
gsd_m = (PIXEL_PITCH_M * DISTANCE_M) / (FOCAL_LENGTH_MM / 1000.0)
px_per_module = TARGET_SIZE_M / gsd_m

# 8 panel slots (4 ON, 4 OFF) = 0.80 m long target
LED_STATES = [1, 0, 1, 0, 1, 0, 1, 0]
CONTRASTS = [1.00, 0.75, 0.50]


# ==============================================================================
# SENSOR SIMULATION ENGINE: ROI (Region of Interest)
# ==============================================================================
def simulate_sensor(contrast, oversample=15):
  total_target_px = len(LED_STATES) * px_per_module
  margin_px = 6.0
  roi_w = int(np.ceil(total_target_px + 2 * margin_px))
  roi_h = int(np.ceil(px_per_module + 2 * margin_px))

  # Target flux levels based on Michelson contrast
  i_on = 0.5 + 0.5 * contrast
  i_off = 0.5 - 0.5 * contrast

  grid_w = roi_w * oversample
  grid_h = roi_h * oversample
  scene = np.full((grid_h, grid_w), i_off, dtype=np.float64)

  y0 = int(round(margin_px * oversample))
  mod_sub = int(round(px_per_module * oversample))

  for idx, state in enumerate(LED_STATES):
    if state == 1:
      x0 = int(round((margin_px + idx * px_per_module) * oversample))
      scene[y0 : y0 + mod_sub, x0 : x0 + mod_sub] = i_on

  # Blur approximation via PSF (Point Spread Function)
  blurred = gaussian_filter(scene, sigma=0.85 * oversample)

  # Integrate into physical sensor photodiodes
  sensor = blurred.reshape(roi_h, oversample, roi_w, oversample).mean(
      axis=(1, 3)
  )

  np.random.seed(42)
  sensor += np.random.normal(0, 0.015, sensor.shape)
  return np.clip(sensor, 0, 1), roi_w, roi_h


# Compute physical ground footprint of the zoomed-in ROI window
_, sample_w_px, sample_h_px = simulate_sensor(1.0)
roi_ground_w_m = sample_w_px * gsd_m
roi_ground_h_m = sample_h_px * gsd_m

# ==============================================================================
# VISUALIZATION
# ==============================================================================
fig, axes = plt.subplots(
    nrows=4,
    ncols=2,
    figsize=(16, 18),
    gridspec_kw={"width_ratios": [3, 2], "height_ratios": [1, 1, 1, 1.25]},
)
plt.subplots_adjust(hspace=0.45, wspace=0.25, top=0.92, bottom=0.05)

# Concise title with small specifications subtitle
fig.suptitle(
    "200mm lens resolution and contrast",
    fontsize=16,
    fontweight="bold",
    y=0.97,
)
fig.text(
    0.5,
    0.945,
    f"1,000 m Distance | Ground Coverage: {ground_w_m:.2f} m × {ground_h_m:.2f} m ({ground_area_sqm:,.2f} m²) | "
    f"GSD: {gsd_m * 100:.2f} cm/px | 10 cm Module = {px_per_module:.2f} px",
    ha="center",
    fontsize=9.5,
    color="#444444",
)

colors = ["crimson", "darkorange", "goldenrod"]

# --- Rows 1-3: Zoomed-In Photodiode Models at 100%, 75%, 50% Contrast ---
for row, (contrast, col) in enumerate(zip(CONTRASTS, colors)):
  img, w_px, h_px = simulate_sensor(contrast)

  # Left column: Discretized Sensor Grid
  ax_img = axes[row, 0]
  ax_img.imshow(
      img,
      cmap="inferno",
      origin="lower",
      extent=[0, w_px, 0, h_px],
      vmin=0,
      vmax=1.0,
  )
  ax_img.set_xticks(np.arange(0, w_px + 1, 1))
  ax_img.set_yticks(np.arange(0, h_px + 1, 1))
  ax_img.grid(color="cyan", linestyle="-", linewidth=0.35, alpha=0.35)
  ax_img.tick_params(
      labelbottom=False, labelleft=False, left=False, bottom=False
  )

  ax_img.set_title(
      f"Sensor 2D Array ({contrast * 100:.0f}% Contrast)\n"
      f"ROI (Region of Interest): {roi_ground_w_m:.2f} m × {roi_ground_h_m:.2f} m "
      f"({roi_ground_w_m * 100:.0f} × {roi_ground_h_m * 100:.0f} cm)",
      fontsize=10,
      fontweight="bold",
      pad=8,
  )

  # Right column: 1D Horizontal Intensity Profile
  ax_prof = axes[row, 1]
  center_y = h_px // 2
  profile = img[center_y, :]
  x_coords = np.arange(len(profile)) + 0.5

  ax_prof.step(
      x_coords,
      profile,
      where="mid",
      color=col,
      linewidth=2,
      label=f"{contrast * 100:.0f}% Contrast",
  )
  ax_prof.scatter(x_coords, profile, color="black", s=14, zorder=3)
  ax_prof.set_xlim(0, w_px)
  ax_prof.set_ylim(-0.05, 1.05)
  ax_prof.set_xlabel("Sensor X Coordinate (pixels)", fontsize=9)
  ax_prof.set_ylabel("Normalized Intensity", fontsize=9)
  ax_prof.grid(True, linestyle=":", alpha=0.6)
  ax_prof.legend(loc="upper right", fontsize=8)
  ax_prof.set_title(
      f"1D Cross-Section Intensity Profile ({contrast * 100:.0f}% Contrast)",
      fontsize=10,
      fontweight="bold",
      pad=8,
  )

# --- Row 4: Full Sensor View To Real-Life Scale ---
ax_full = axes[3, 0]
full_frame_bg = np.full((120, 180), 0.05)
ax_full.imshow(
    full_frame_bg,
    cmap="gray",
    origin="lower",
    extent=[0, ground_w_m, 0, ground_h_m],
    vmin=0,
    vmax=1.0,
)

target_x0 = (ground_w_m - (len(LED_STATES) * TARGET_SIZE_M)) / 2.0
target_y0 = (ground_h_m - TARGET_SIZE_M) / 2.0
rect_target = patches.Rectangle(
    (target_x0, target_y0),
    len(LED_STATES) * TARGET_SIZE_M,
    TARGET_SIZE_M,
    edgecolor="crimson",
    facecolor="yellow",
    linewidth=1.5,
    zorder=5,
)
ax_full.add_patch(rect_target)

ax_full.annotate(
    f"0.80 m Target Strip\n(occupies {px_per_module * 8:.1f} of {RES_X_PX} pixels)",
    xy=(target_x0 + 0.4, target_y0 + 0.05),
    xytext=(target_x0 + 25, target_y0 + 25),
    arrowprops=dict(facecolor="red", edgecolor="red", arrowstyle="->", lw=1.5),
    fontsize=9.5,
    fontweight="bold",
    color="white",
    bbox=dict(boxstyle="round,pad=0.4", fc="crimson", alpha=0.9),
)

ax_full.set_xlim(0, ground_w_m)
ax_full.set_ylim(0, ground_h_m)
ax_full.set_xlabel("Ground Width (meters)", fontsize=9.5)
ax_full.set_ylabel("Ground Height (meters)", fontsize=9.5)
ax_full.set_title(
    f"Full Sensor View to Scale: 100% FOV (Field of View)\n"
    f"{ground_w_m:.1f} m × {ground_h_m:.1f} m Total Ground Coverage",
    fontsize=10,
    fontweight="bold",
    pad=8,
)

# Row 4, Right column: Scale Context & Legend summary
ax_info = axes[3, 1]
ax_info.axis("off")
info_text = (
    "SCALE SUMMARY (200 mm Lens at 1,000 m)\n"
    "----------------------------------------------------\n"
    f"• Full Picture Seen by Drone : {ground_w_m:.2f} m × {ground_h_m:.2f} m\n"
    f"• Total Area of Full Photo   : {ground_area_sqm:,.2f} m² (2.16 hectares)\n"
    f"• Total Sensor Resolution    : {RES_X_PX:,} × {RES_Y_PX:,} pixels (44.7 MP)\n\n"
    f"• 8-Light LED Target Strip   : 0.80 m × 0.10 m (80 cm × 10 cm)\n"
    f"• Zoomed Model Window (Rows 1-3) : {roi_ground_w_m:.2f} m × {roi_ground_h_m:.2f} m\n"
    f"  - Zoomed model covers only {sample_w_px} × {sample_h_px} camera pixels\n"
    f"  - Displays {roi_ground_w_m * 100:.0f} cm of ground to show photodiodes."
)
ax_info.text(
    0.05,
    0.5,
    info_text,
    fontsize=9.5,
    family="monospace",
    verticalalignment="center",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#f8f8f8", edgecolor="#cccccc"),
)

plt.show()
