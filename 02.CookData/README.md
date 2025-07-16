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


