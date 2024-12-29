import os
from statistics import variance

import cv2
import numpy as np
import pandas as pd
from datetime import datetime

from statistics import mean, stdev


def measure_ellipse_short_axis(image_path: str, output_directory: str, scalebar_diameter: int, ratio: float):
    # Get the current date and time for unique filenames
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error loading image")
        return

    # Apply a GaussianBlur to reduce noise and improve shape detection
    blurred_image = cv2.GaussianBlur(image, (9, 9), 2)

    # Threshold the image to create a binary image
    _, binary_image = cv2.threshold(blurred_image, 100, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Convert the image to color to draw the detected shapes
    image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Prepare to store ellipse data
    ellipses = []

    # Iterate through each contour
    for contour in contours:
        # Fit an ellipse to the contour if it has enough points
        if len(contour) >= 5:
            ellipse = cv2.fitEllipse(contour)
            (center, axes, angle) = ellipse

            # axes[0] is the short axis and axes[1] is the long axis
            short_axis = min(axes)
            long_axis = max(axes)

            # Check if the short and long axes do not differ by more than 1.5-fold
            if 10 <= short_axis <= 60 and long_axis / short_axis <= 1.5:
                ellipses.append((center, axes, angle, short_axis))

    # Sort the ellipses by the x-coordinate of their centers (left to right)
    ellipses.sort(key=lambda e: e[0][0])
    (center, axes, angle, short_axis) = ellipses[0]
    ellipses = ellipses[1:]

    # Prepare to store results and number the ellipses
    results = []
    ellipse_number = 1

    def calculate(axis, diameter):
        _pixels = axis * ratio
        _size = (_pixels / diameter) * scalebar_diameter
        return _pixels, _size

    first_diameter = short_axis if ellipses else 1  # Use 1 to avoid division by zero

    # Get the diameter of the first ellipse for normalization
    feret_pixels, feret_size = calculate(short_axis, first_diameter)

    diameters = []

    # Iterate through sorted ellipses
    for ellipse in ellipses:
        (center, axes, angle, short_axis) = ellipse
        # Calculate the normalized diameter
        pixels, size = calculate(short_axis, first_diameter)

        # Store the result in the list
        results.append([ellipse_number, pixels, size])
        diameters.append(size)

        # Draw the ellipse slightly larger to appear outside the original boundary
        scaled_axes = (axes[0] * ratio, axes[1] * ratio)  # Scale the axes by 5%
        cv2.ellipse(image_color, (center, scaled_axes, angle), (0, 255, 0), 1)
        cv2.circle(image_color, (int(center[0]), int(center[1])), 1, (0, 255, 255), 2)  # Draw center

        # Annotate the ellipse number and diameter on the image
        text = f"{ellipse_number}: {pixels:.2f}"
        position = (int(center[0] + axes[0] / 2 + 5), int(center[1]) + 5)
        cv2.putText(image_color, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        ellipse_number += 1

    # Generate full paths for the output files
    output_image = os.path.join(output_directory, f"{current_time}_annotated_image_.png")
    output_excel = os.path.join(output_directory, f"{current_time}_ellipse_diameters.xlsx")

    # Save the annotated image
    cv2.imwrite(output_image, image_color)

    diameter_average = mean(diameters)
    diameter_stdev = stdev(diameters)

    results.insert(0, ["scale bar", feret_pixels, feret_size])
    results.insert(0, ["standard deviation", "", diameter_stdev])
    results.insert(0, ["average", "", diameter_average])

    # Save the results to an Excel file
    df = pd.DataFrame(results, columns=["Ellipse Number", "Diameter (pixels)", "Diameter (μm)"])
    df.to_excel(output_excel, index=False)

    return {
        'contours': len(contours)-1,
        'ellipses': len(ellipses),
        'average': diameter_average,
        'standard deviation': diameter_stdev,
        'input image': image_path,
        'output image': output_image,
        'result': output_excel
    }

# Provide the path to your image and output file paths
#image_path = "C:\\Users\\seong\\Dropbox\\Spheroid Size\\Data\\spheroid_sample.png"
#output_directory = "C:\\Users\\seong\\Dropbox\\Spheroid Size\\Data"

#measure_ellipse_short_axis(image_path, output_directory)
