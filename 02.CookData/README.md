# Cook Data Process Steps

The 01.Data-generation step involves downloading the necessary OBJ files for processing and simulation processing.

### 2. Transform OBJ Files to GS-SDF
Once the OBJ files are obtained, they will be transformed into GS-SDF (Pure SDF with internal UDF segments). This transformation is crucial for preparing the data for further training process.

### 3. Generate CSV Files for Impact Collision Information
We will create CSV files that contain impact collision information. These CSV files will then be transformed into vector data, which will include both the CSV and additional info files.


### 4. Combine Vector CSV Files and GS-SDF
The final step involves combining the vector CSV files with the GS-SDF files to create a comprehensive dataset. The data import will include files from the following directories:
- info/*.txt
- impact/*.txt
- gssdf/*.nii
- ffbdf/*.nii

> python create_input_output.py

By following these steps, we ensure that the Cook Data component is well-prepared for training and analysis.

## FFBF mode (related paper)

The `ffbdf/*.nii` outputs above are the **Far-From-Boundary Field (FFBDF)** encoding of
the fractured solids. This is the data-cooking side of our SMI 2026 paper
**"Far-From-Boundary Fields for Learning Segmented Implicit Solids"** (Huang & Kanai).
The encoding is produced by `encode_obj_to_nii()` in
[`create_input_output.py`](create_input_output.py) — use this FFBF (FFBDF) mode for that
paper. The fractured solids themselves come from the simulation in
[`../01.Data-generation`](../01.Data-generation).

- Paper code: https://github.com/nikoloside/far-from-boundary-fields


