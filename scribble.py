import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Configureer Matplotlib om geen GUI te gebruiken
import matplotlib
matplotlib.use('Agg')

def generate_random_scribble():
    """
    Genereer een willekeurige scribble als (x, y) punten.
    """
    x = np.cumsum(np.random.uniform(-1.5, 1.5, 15))
    y = np.cumsum(np.random.uniform(-1.5, 1.5, 15))
    x = np.append(x, x[0])
    y = np.append(y, y[0])
    return x, y

def plot_scribble(x, y, output_path):
    """
    Plot een scribble en sla deze op als een afbeelding.
    """
    plt.figure(figsize=(6, 6))
    plt.plot(x, y, color='black', linewidth=2)
    plt.axis('equal')
    plt.axis('off')
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

def generate_daily_scribble(output_dir="static/doodles"):
    """
    Genereer een scribble voor vandaag en sla deze op.
    Return de bestandsnaam van de gegenereerde doodle.
    """
    today = datetime.now().date()
    filename = f"doodle_{today}.png"
    output_path = os.path.join(output_dir, filename)

    # Controleer of het bestand al bestaat
    if not os.path.exists(output_path):
        os.makedirs(output_dir, exist_ok=True)
        x, y = generate_random_scribble()
        plot_scribble(x, y, output_path)

    return filename
