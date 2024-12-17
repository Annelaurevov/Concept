# Concept - Inspire Your Artistry

**Author**: Annelaure van Overbeeke

Concept is a web application designed to inspire creativity by allowing users to explore, save, and share artistic ideas. This includes daily challenges, a gallery of user submissions, and organizational tools for creative projects.

---

<h2 align="center">Table of Contents</h2>

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [API Usage](#api-usage)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Acknowledgments](#acknowledgments)

---

<h2>Introduction</h2>

Concept is a web application designed to foster creativity and inspiration. Whether you're a professional artist, a hobbyist, or just looking for some creative fun, Concept offers tools to save and share your ideas while connecting with a community of like-minded individuals.

**Key Features:**
- Save and organize ideas like photos, recipes, and artworks.
- Participate in a daily "Doodle of the Day" challenge.
- Explore and interact with a gallery of community submissions.
- Use the public API to integrate Concept data into your own projects.

---

<h2 align="center">Features</h2>

### **1. Creative Organization**
- Store and organize inspirations such as images, recipes, and artworks.
- Create collections or mood boards for your creative projects.

### **2. Daily Doodle Challenge**
- Generate a random scribble each day to inspire your artwork.
- Draw over the scribble, submit your creation, and gain likes.
- Compete on daily leaderboards to showcase your creativity.

### **3. Community Interaction**
- Browse and like submissions from other users.
- Gain inspiration from the shared gallery.

### **4. Public API**
- Access data from Concept using the public API.
- Retrieve information about submissions, likes, and users to create your own integrations.

---

<h2 align="center">Installation</h2>

### Prerequisites
- Python 3.10+
- PostgreSQL

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/concept.git
   cd concept
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file with the following:**
   ```env
   DATABASE_URL=postgresql://<user>:<password>@localhost/<database>
   SECRET_KEY=your-secret-key
   ```

4. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

5. **Start the application:**
   ```bash
   flask run
   ```

6. **Access the application:** Open your browser and go to `http://127.0.0.1:5000`.

---

<h2 align="center">API Usage</h2>

### API Endpoints
- **`GET /api/doodles`**: Retrieve all doodles.
- **`GET /api/doodles/filter?date=YYYY-MM-DD`**: Get doodles for a specific date.

### Example Request
```bash
curl http://127.0.0.1:5000/api/doodles/filter?date=2024-12-17
```

---

<h2 align="center">Screenshots</h2>

### **Homepage**
![Homepage](static/screenshots/homepage.png)

### **Doodle Challenge**
![Doodle Challenge](static/screenshots/doodle.png)

---

<h2 align="center">Project Structure</h2>

- **`app.py`**: Core application logic.
- **`models.py`**: Database models for users, doodles, and saved items.
- **`scribble.py`**: Logic for generating the daily doodles.
- **`static/`**: Static assets like CSS, images, and JavaScript files.
- **`templates/`**: HTML templates for rendering the UI.

---

<h2 align="center">Acknowledgments</h2>

This project was created with inspiration from tools like Google Doodle and community-driven platforms. Special thanks to the following resources and individuals for their guidance and support:

- **Brian Yu and David Malan**: Materials from Harvard's CSCI S-33a course, published under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported license.
- **David Malan**: CS164 course materials from Harvard, published under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported license.
- **Open-source contributors**: For their amazing tools and libraries that made this project possible.

---

Concept is a project fueled by passion for creativity and collaboration. Share your art, explore new ideas, and inspire others!

