import os
from PIL import Image, ImageDraw
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math


def create_outline(input_image_path, output_image_path):
    try:
        # Importing Modules
        plt.style.use('ggplot')

        # Loading Original Image
        img = cv2.imread(input_image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Create a 1x1 grid of subplots (just for simplicity)
        fig, axs = plt.subplots(1, 1, figsize=(16, 12))

        # Hide axes
        axs.axis('off')

        # Now update the canvas with the final sketch
        # Converting Image to GrayScale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Inverting the Image
        img_invert = cv2.bitwise_not(img_gray)

        # Smoothing the Image
        img_smoothing = cv2.GaussianBlur(img_invert, (21, 21), sigmaX=0, sigmaY=0)

        # Converting to Pencil Sketch
        final = cv2.divide(img_gray, 255 - img_smoothing, scale=255)

        # Update the canvas with the final sketch
        axs.imshow(final, cmap="gray")

        # Save the final sketch image directly without displaying
        plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close(fig)  # Close the figure to avoid displaying it

    except Exception as e:
        print(f"Error in create_outline: {e}")


def add_grid2(image, output_image_path):
    # Get image dimensions
    image_width, image_height = image.size

    # Define the minimum and maximum number of rows and columns
    min_rows, min_columns = 5, 5
    # Adjust the max_rows and max_columns to 7
    max_rows, max_columns = 7, 7

    # Calculate the optimal number of rows and columns based on the image dimensions
    num_rows = max(min_rows, min(math.ceil(math.sqrt(image_height)), max_rows))
    num_columns = max(min_columns, min(math.ceil(math.sqrt(image_width)), max_columns)) 

    # Calculate the spacing between rows and columns
    row_spacing = image_height // num_rows
    column_spacing = image_width // num_columns

    # Create a new image with an alpha channel
    grid_image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grid_image)

    # Draw horizontal grid lines
    for i in range(1, num_rows):
        y = i * row_spacing
        draw.line([(0, y), (image_width, y)], fill=(255, 0, 0, 255), width=5)

    # Draw vertical grid lines
    for i in range(1, num_columns):
        x = i * column_spacing
        draw.line([(x, 0), (x, image_height)], fill=(255, 0, 0, 255), width=5)

    # Convert the grid image to a numpy array
    grid_array = np.array(grid_image)

    # Convert the original image to a numpy array
    image_array = np.array(image.convert("RGBA"))

    # Blend the two images
    blended_array = (grid_array * (grid_array[:, :, 3] / 255.0)[:, :, None] +
                     image_array * (1.0 - grid_array[:, :, 3] / 255.0)[:, :, None]).astype(np.uint8)

    # Create a new image from the blended array
    blended_image = Image.fromarray(blended_array, 'RGBA')

    # Save the resulting image
    blended_image.save(output_image_path, format="PNG")



def create_grid(input_image_path, output_image_path):
    # Load the input image (contour image from the "Drawing" stage)
    contour_image = Image.open(input_image_path)

    # Now, add the grid to the contoured image
    add_grid2(contour_image, output_image_path)



def add_grid(image, grid_size):
    # Get image dimensions
    image_width, image_height = image.size

    # Calculate the spacing between rows and columns
    row_spacing = image_height // grid_size
    column_spacing = image_width // grid_size

    # Draw horizontal grid lines
    for i in range(1, grid_size):
        y = i * row_spacing
        ImageDraw.Draw(image).line([(0, y), (image_width, y)], fill=(255, 0, 0), width=5)

    # Draw vertical grid lines
    for i in range(1, grid_size):
        x = i * column_spacing
        ImageDraw.Draw(image).line([(x, 0), (x, image_height)], fill=(255, 0, 0), width=5)

def create_animation_frames(countoured_image_path, grid_size, output_path):
    # Load the countoured image
    countoured_image = Image.open(countoured_image_path)

    # Create a blank white face
    blank_face = Image.new("RGB", countoured_image.size, (255, 255, 255))

    # Add the grid to the blank face
    add_grid(blank_face, grid_size)

    # Save the first frame
    frames = [blank_face]

    # Loop through each grid section and add frames with contours
    for row_index in range(grid_size):
        for col_index in range(grid_size):
            # Calculate the x and y range for the current grid section
            x_range = col_index * (countoured_image.width // grid_size), (col_index + 1) * (countoured_image.width // grid_size)
            y_range = row_index * (countoured_image.height // grid_size), (row_index + 1) * (countoured_image.height // grid_size)

            # Crop the countoured image to the current grid section
            cropped_image = countoured_image.crop((x_range[0], y_range[0], x_range[1], y_range[1]))

            # Create a copy of the blank face to draw contours on
            animated_frame = blank_face.copy()

            # Draw contours on the frame
            animated_frame.paste(cropped_image, (x_range[0], y_range[0]))

            # Draw grid on the frame
            add_grid(animated_frame, grid_size)

            # Add the frame to the animation
            frames.append(animated_frame)

    # Save the frames
    frames[1].save(output_path, save_all=True, append_images=frames[2:], duration=2000, loop=0)


# Example usage
#create_animation_frames("/Users/jha/Desktop/sinnovationproject/outline_stage1.jpg", 7, "/Users/jha/Desktop/innovationproject/output_animation.gif")



# Uncomment the following function if you want to include the shading stage
'''
def create_shading(input_image_path, output_image_path):
    try:
        image = cv2.imread(input_image_path)
        if image is None:
            raise FileNotFoundError(f"Error loading input image: {input_image_path}")

        # Convert the image to grayscale
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to focus on dark areas
        _, thresholded = cv2.threshold(grayscale, 50, 255, cv2.THRESH_BINARY)

        # Convert the thresholded image back to a 3-channel image
        thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)

        # Blend the thresholded image with the original image to create shading with soft edges
        alpha = 0.3  # You can adjust the alpha value to control the shading intensity
        shaded_image = cv2.addWeighted(image, alpha, thresholded, 1 - alpha, 0)

        # Save and display the shaded image
        cv2.imwrite(output_image_path, shaded_image)
    except Exception as e:
        print(f"Error in create_shading: {e}")
'''

def create_and_display_stage(stage_name, input_image_path, output_image_path=None):
    if stage_name == "Drawing":
        create_outline(input_image_path, output_image_path)
    elif stage_name == "Blocking in":
        # Uncomment the following line if you want to include shading
        # create_shading(input_image_path, output_image_path)
        pass
    elif stage_name == "Grid":
        create_grid(input_image_path, output_image_path)
    elif stage_name == "Animation":
        create_animation_frames(input_image_path, 7, output_image_path)

def main():
    print("Art Project Assistant")
    print("Let's create images for each stage of the painting!")

    input_image_path = input("Please provide the input image path: ")

    # Verify that the input image file exists
    if not os.path.isfile(input_image_path):
        print(f"Error: Input image file not found: {input_image_path}")
        return

    # Get the directory of the input image
    input_image_directory = os.path.dirname(input_image_path)

    # Define output image paths for each stage in the same directory as the input
    stages = [
        ("Drawing", input_image_path, os.path.join(input_image_directory, "outline_stage1.jpg")),
        ("Blocking in", input_image_path, os.path.join(input_image_directory, "shading_stage.jpg")),
        ("Grid", os.path.join(input_image_directory, "outline_stage1.jpg"), os.path.join(input_image_directory, "grid_stage.png")),
        ("Animation", os.path.join(input_image_directory, "outline_stage1.jpg"), os.path.join(input_image_directory, "animation.gif")),
    ]

    for stage_name, input_path, output_path in stages:
        create_and_display_stage(stage_name, input_path, output_path)

if __name__ == "__main__":
    main()
