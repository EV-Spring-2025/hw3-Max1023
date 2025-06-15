# EV HW3: PhysGaussian
## Setup
To set up the virtual environment and install the required packages, use the following commands:
```bash
conda create --name ev_hw3 python=3.11
conda activate ev_hw3
pip install -r requirements.txt
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
git clone --recurse-submodules https://github.com/XPandora/PhysGaussian
cd PhysGaussian
pip install -e gaussian-splatting/submodules/diff-gaussian-rasterization/
pip install -e gaussian-splatting/submodules/simple-knn/
cd ../
```
## Preparation
Download ficus_whitebg-trained.zip in [Gaussian Splatting models](https://drive.google.com/drive/folders/1EMUOJbyJ2QdeUz8GpPrLEyN4LBvCO3Nx) for our experiment.
To simulate a reconstructed 3D Gaussian Splatting scene, run the following command:
```bash
cd PhysGaussian
python gs_simulation.py --model_path ./ficus_whitebg-trained --output_path ../output --config ./config/ficus_config.json --render_img --compile_video
cd ../
```
Change the parameters in ./config/ficus_config.json to see different outputs.
Check output videos in the output file.

## Evaluate PSNR value
To see psnr of output videos with different parameters, run the commanownload the datad:
```bash
python calculate_psnr.py "path/to/baseline.mp4" "path/to/altered.mp4"
```

## Ablation study
**Baseline:**  
n_grid = 100 / substep = 1e-4 / grid_v_damping_scale = 0.9999 / softening = 0.1

|                       | n_grid = 1 | substep_dt = 1e-5 | grid_v_damping_scale = 1.9999 | grid_v_damping_scale = 0.0009 | Softening = 10 |
|-----------------------|------------|-------------------|-------------------------------|-------------------------------|----------------|
| **Jelly psnr**        | 24.72      | 21.20             | 22.35                         | 21.97                         | 24.72          |
| Compared to baseline  |            |                   |                               |                               |                |
| **Snow psnr**         | 42.66      | 16.29             | Warp CUDA error 700 if set    | 16.25                         | 42.29          |
| Compared to baseline  |            |                   | scale > 1                     |                               |                |

## Interpreting the Parameter Tests

**n_grid (Grid Resolution)**

    Jelly (Continuum Elasticity): Jelly is simulated as a continuous, deformable object. Its elastic forces (what makes it jiggle and hold its shape) depend on calculating the spatial deformation within the material. This calculation is done on the grid.

        With a high-resolution grid (n_grid=100), you can accurately capture how different parts of the jelly stretch and shear.
        With a tiny grid (n_grid=1), you lose all of this spatial information. The simulation can no longer compute internal stress and strain properly. The jelly block might behave more like a single rigid object or lose its characteristic "jiggle," causing a major deviation from the baseline, hence the low PSNR.

    Snow (Granular Material): Snow is often simulated as a granular material using models like the Drucker-Prager model. While it has some cohesion, its motion is governed by the collective behavior of many small particles.

        In many scenarios (like a simple pile settling or a slow avalanche), the large-scale motion doesn't depend heavily on fine-grained internal stress calculations. The primary motion is advecting (moving) the particles.
        As a result, even a very coarse grid might be sufficient to handle the bulk interactions and gravity, leading to a final result that looks very similar to the high-resolution simulation.

**substep_dt (Time Step)**

    Change: Decreasing the time step from 1e-4 to 1e-5.
    Result: A significant drop in PSNR for both Jelly (21.20) and especially for Snow (16.29).
    Interpretation: A smaller time step causes the simulation to diverge from the baseline's path. While in many physics simulations smaller time steps lead to more accuracy, here it results in a different outcome. This shows that the system's behavior is sensitive to the dt value.

**grid_v_damping_scale (Velocity Damping)**

This parameter controls how much the velocity of the material is reduced at each step. A value of 1 means no damping, while a value close to 0 means high damping.

    Change 1: Setting damping to 1.9999 (i.e., amplifying velocity).
        Result: Caused a "Warp CUDA error 700" for the Snow material and lowered the PSNR for Jelly (22.35).
        Interpretation: A damping value greater than 1 is physically unrealistic, as it adds energy to the system. This leads to numerical instability and simulation crashes (the CUDA error), which is a common outcome for "exploding" simulations.

    Change 2: Setting damping to 0.0009 (very high damping).
        Result: A massive drop in PSNR for both materials (Jelly: 21.97, Snow: 16.25).
        Interpretation: High damping removes most of the motion from the material, making it behave very differently from the minimally damped baseline. This expectedly results in a low PSNR.

**Softening**

    Change: Increasing the softening parameter from 0.1 to 10.
    Result: Very little change in PSNR for either material (Jelly: 24.72, Snow: 42.29).
    Interpretation: Similar to grid resolution, the softening parameter appears to have a minimal impact on the final visual output in this specific test case. The materials' behavior is robust to this change.

**Key Takeaways**

    Stability is Crucial: Unphysical parameters, like a damping scale greater than 1, will break the simulation.
    Not All Parameters Are Equal: The simulation's visual outcome was highly sensitive to changes in substep_dt and grid_v_damping_scale but was largely unaffected by n_grid and softening.
    Materials Behave Differently: The "Snow" material was more sensitive to parameter changes than "Jelly," crashing when damping was increased and showing a larger PSNR drop with changes in substep_dt. This highlights that different materials require different parameter tuning for stable and desirable results.

## Results
All outputs showed in the former ablation study can be find in ./output

