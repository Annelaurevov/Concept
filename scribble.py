import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Configure Matplotlib to use a non-GUI backend
import matplotlib
matplotlib.use('Agg')


def generate_random_scribble():
    """
    Generate a random scribble as (x, y) points.

    Returns:
        tuple: Two arrays (x, y) representing the coordinates of the scribble.
    """
    # Generate random cumulative changes for x and y to create a scribble
    x = np.cumsum(np.random.uniform(-1.5, 1.5, 15))
    y = np.cumsum(np.random.uniform(-1.5, 1.5, 15))

    # Close the scribble by appending the starting point to the end
    x = np.append(x, x[0])
    y = np.append(y, y[0])
    return x, y


def plot_scribble(x, y, output_path):
    """
    Plot a scribble and save it as an image.

    Args:
        x (array): Array of x-coordinates of the scribble.
        y (array): Array of y-coordinates of the scribble.
        output_path (str): Path to save the generated image.
    """
    # Create a square figure
    plt.figure(figsize=(6, 6))
    # Plot the scribble with black lines
    plt.plot(x, y, color='black', linewidth=2)
    # Ensure the plot axes are equal and remove axis lines
    plt.axis('equal')
    plt.axis('off')
    # Save the plot to the specified output path
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    # Close the plot to free up resources
    plt.close()


def generate_daily_scribble(output_dir="static/doodles"):
    """
    Generate a scribble for the current day and save it.

    Args:
        output_dir (str): Directory to save the generated scribble image.

    Returns:
        str: Filename of the generated scribble image.
    """
    # Get today's date and create a unique filename for the scribble
    today = datetime.now().date()
    filename = f"doodle_{today}.png"
    output_path = os.path.join(output_dir, filename)

    # Check if the file already exists
    if not os.path.exists(output_path):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        # Generate random scribble data
        x, y = generate_random_scribble()
        # Plot and save the scribble to the output path
        plot_scribble(x, y, output_path)

    # Return the filename of the generated scribble
    return filename
