from osgeo import gdal
import numpy as np
import os
from affine import Affine

def crop_image(input_image, output_folder, tile_size=2048):
    # Open the input image
    input_ds = gdal.Open(input_image)

    # Check if the input image was successfully opened
    if input_ds is None:
        print("Error opening input image.")
        return

    # Read the image as an array
    image_array = np.transpose(np.array([input_ds.GetRasterBand(i+1).ReadAsArray() for i in range(input_ds.RasterCount)]), (1, 2, 0))

    # Get image dimensions
    image_height, image_width, _ = image_array.shape

    # Calculate number of tiles in each dimension
    num_tiles_x = (image_width - 1) // tile_size + 1
    num_tiles_y = (image_height - 1) // tile_size + 1

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get geotransform and projection information
    geotransform = input_ds.GetGeoTransform()
    projection = input_ds.GetProjection()

    # Loop through each tile
    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            # Calculate tile coordinates
            x1 = x * tile_size
            y1 = y * tile_size
            x2 = min(x1 + tile_size, image_width)
            y2 = min(y1 + tile_size, image_height)

            # Crop tile
            cropped_image = image_array[y1:y2, x1:x2, :]

            # Write the output tile
            tile_filename = f"{os.path.splitext(os.path.basename(input_image))[0]}_tile_{y}_{x}.tif"
            tile_path = os.path.join(output_folder, tile_filename)

            print("Creating tile:", tile_path)  # Added for debugging

            driver = gdal.GetDriverByName('GTiff')
            tile_ds = driver.Create(tile_path, x2 - x1, y2 - y1, 3, gdal.GDT_Byte)

            print("Tile dataset:", tile_ds)  # Added for debugging

            if tile_ds is None:
                print("Failed to create tile dataset.")
                continue

            for i in range(3):
                tile_ds.GetRasterBand(i + 1).WriteArray(cropped_image[:, :, i])

            # Set georeferencing information
            tile_geotransform = list(geotransform)
            tile_geotransform[0] += x1 * geotransform[1]
            tile_geotransform[3] += y1 * geotransform[5]

            tile_ds.SetGeoTransform(tile_geotransform)
            tile_ds.SetProjection(projection)

            tile_ds = None

    # Close the input dataset
    input_ds = None

    print("Image cropping completed successfully.")

# Input image path
input_image_path = "/content/drive/MyDrive/trying/tif1.tif"

# Output folder path
output_folder_path = "/content/drive/MyDrive/trying/tiles"

# Perform cropping to tiles
crop_image(input_image_path, output_folder_path)
