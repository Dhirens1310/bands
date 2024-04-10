from osgeo import gdal
import numpy as np
import cv2
from google.colab.patches import cv2_imshow

# Define input and output paths
input_image = "/content/drive/MyDrive/osimlipal_1.tif"
output_image_crop = "/content/drive/MyDrive/trying/tif1.tif"
output_image_vegetation = "/content/drive/MyDrive/trying/vegetation.tif"

# Open the input image
input_ds = gdal.Open(input_image)

# Get the number of bands in the input image
num_bands = input_ds.RasterCount

# Specify which bands to keep (assuming first three bands represent Red, Green, and Blue)
bands_to_keep = [1, 2, 3]

# Read and stack the selected bands
band_data = []
for band_num in bands_to_keep:
    band = input_ds.GetRasterBand(band_num)
    band_data.append(band.ReadAsArray())

# Stack bands together
rgb_image = np.stack(band_data, axis=-1)

# Compute percentiles for each band
lower_percentile = 0.5
upper_percentile = 99.5
percentiles = np.percentile(rgb_image, (lower_percentile, upper_percentile), axis=(0, 1))

# Calculate clip values
clip_min = percentiles[0]
clip_max = percentiles[1]

# Clip values to min and max
image = np.clip(rgb_image, clip_min, clip_max)

# Scale values to 0-255
image = ((image - clip_min) / (clip_max - clip_min)) * 255
image = image.astype(np.uint8)

# Replace No Data values (assumed to be represented by 0) with a specific integer value
no_data_value = 255  # Choose any integer value that doesn't represent valid data
image[image == 0] = no_data_value

# Write the output image
driver = gdal.GetDriverByName('GTiff')
output_ds = driver.Create(output_image_crop, image.shape[1], image.shape[0], 3, gdal.GDT_Byte)
for i in range(3):
    output_ds.GetRasterBand(i + 1).WriteArray(image[:, :, i])

# Copy the georeferencing information
output_ds.SetProjection(input_ds.GetProjection())
output_ds.SetGeoTransform(input_ds.GetGeoTransform())

# Close the datasets
input_ds = None
output_ds = None

print("Image conversion completed successfully.")


