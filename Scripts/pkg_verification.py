"""
Confirms that every required package for the BRICK project imports correctly.
Run this after setting up your virtual environment and installing requirements.txt.
"""

import importlib

packages = [
    "torch",
    "nilearn",
    "nibabel",
    "scipy",
    "sklearn",   # scikit-learn's import name
    "matplotlib",
    "seaborn",
    "pandas",
    "pytest",
    "h5py",
    "tqdm",
]

print(f"{'Package':<15}{'Status':<10}{'Version'}")
print("-" * 40)

failures = []
for pkg in packages:
    try:
        module = importlib.import_module(pkg)
        version = getattr(module, "__version__", "unknown")
        print(f"{pkg:<15}{'OK':<10}{version}")
    except ImportError as e:
        print(f"{pkg:<15}{'FAILED':<10}{e}")
        failures.append(pkg)

print("-" * 40)
if failures:
    print(f"FAILED imports: {failures}")
else:
    print("All imports succeeded.")