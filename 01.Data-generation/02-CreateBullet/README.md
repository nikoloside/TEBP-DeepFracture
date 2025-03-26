# Create Bullet Simulation Scene Instructions

## Steps to Prepare and Create Bullet Simulation

1. **Ensure All OBJ Files are Manifold and Normalize**
   - Before starting the simulation, it is crucial to verify that all OBJ files are manifold and normalize them to fit within a bounding box of [-1, 1]^3. 
   - You can achieve this by running the `manifold_normalize_objs.py` script, which will check for non-manifold edges and vertices, and normalize the objects accordingly.

   To run the script, use the following command:
   ```bash
   python manifold_normalize_objs.py
   ```

3. **Create Bullet Simulation**
   - You have two options to create the bullet simulation:

   **Option 1: Using C++ with Bullet Library** [WIP]
   - If you prefer to use C++, you can create a C++ program that utilizes the Bullet Physics library to set up the simulation. Ensure you have the Bullet library installed and linked correctly in your project.

   **Option 2: Using Maya Plugin**
   - Alternatively, you can use a Maya plugin to manually create the bullet simulation. This method allows for more visual control and adjustments before running the simulation.

   Make sure to follow the respective documentation for the Bullet library or the Maya plugin for detailed instructions on setting up the simulation.
