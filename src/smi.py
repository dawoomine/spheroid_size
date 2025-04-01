import os
import cv2
import pandas as pd
from datetime import datetime

from statistics import mean, stdev


class SMI:
    def __init__(self, scalebar_diameter: int, ratio: float, output_dirname: str):
        if scalebar_diameter < 1:
            raise ValueError("Set the scalebar diameter.")

        self.scalebar_diameter = scalebar_diameter
        self.ratio = ratio
        self.output_dirname = output_dirname

        self.num_of_contours = 0
        self.num_of_ellipses = 0
        self.diameter_average = 0
        self.diameter_standard_deviation = 0
        self.result_image = None
        self.result_data = None

    def measure(self, image_path: str):
        if not image_path:
            raise ValueError("Select the image file.")

        if not os.path.exists(image_path):
            raise ValueError(f"Image file {image_path} does not exist.")

            # Get the current date and time for unique filenames
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Load the image in grayscale
        org_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if org_image is None:
            raise RuntimeError("Error loading image")

        # Apply a GaussianBlur to reduce noise and improve shape detection
        blurred_image = cv2.GaussianBlur(org_image, (9, 9), 2)
        self.save_image(blurred_image, current_time, "blurred_"+os.path.basename(image_path))

        # Threshold the image to create a binary image
        _, binary_image = cv2.threshold(blurred_image, 100, 255, cv2.THRESH_BINARY)

        # Find contours in the binary image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Convert the image to color to draw the detected shapes
        result_image = cv2.cvtColor(org_image, cv2.COLOR_GRAY2BGR)

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
            _pixels = axis * self.ratio
            _size = (_pixels / diameter) * self.scalebar_diameter
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
            scaled_axes = (axes[0] * self.ratio, axes[1] * self.ratio)  # Scale the axes by 5%
            cv2.ellipse(result_image, (center, scaled_axes, angle), (0, 255, 0), 1)
            cv2.circle(result_image, (int(center[0]), int(center[1])), 1, (0, 255, 255), 2)  # Draw center

            # Annotate the ellipse number and diameter on the image
            text = f"{ellipse_number}: {pixels:.2f}"
            position = (int(center[0] + axes[0] / 2 + 5), int(center[1]) + 5)
            cv2.putText(result_image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            ellipse_number += 1

        # Save the annotated image
        output_image = self.save_image(result_image, current_time, os.path.basename(image_path))

        diameter_average = mean(diameters)
        diameter_stdev = stdev(diameters)

        results.insert(0, ["scale bar", feret_pixels, feret_size])
        results.insert(0, ["standard deviation", "", diameter_stdev])
        results.insert(0, ["average", "", diameter_average])

        output_excel = self.save_excel(results, current_time, os.path.basename(image_path))

        self.num_of_contours = len(contours) - 1
        self.num_of_ellipses = len(ellipses)
        self.diameter_average = diameter_average
        self.diameter_standard_deviation = diameter_stdev
        self.result_image = output_image
        self.result_data = output_excel

    def save_image(self, image, current_time, image_name):
        saved_path = os.path.join(self.output_dirname, f"{current_time}_{image_name}_annotated_image_.png")
        cv2.imwrite(saved_path, image)
        return saved_path

    def save_excel(self, results, current_time, image_name):
        excel_path = os.path.join(self.output_dirname, f"{current_time}_{image_name}_ellipse_diameters.xlsx")
        df = pd.DataFrame(results, columns=["Ellipse Number", "Diameter (pixels)", "Diameter (μm)"])
        df.to_excel(excel_path, index=False)
        return excel_path

