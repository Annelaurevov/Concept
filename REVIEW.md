# REVIEW.md

**Code review uitgevoerd door: [Elisa Dalemans] en [Finn Dokter]**

---

## Inleiding

Dit document beschrijft een uitgebreide code review van met een focus op het verbeteren van leesbaarheid, onderhoudbaarheid, beveiliging en consistentie. Tijdens de review heb ik 10 belangrijke verbeterpunten genoteerd. 

De belangrijkste doelstellingen van deze review zijn:
- **Herbruikbaarheid verbeteren:** Door logica te verplaatsen naar helperfuncties.
- **Beveiliging verhogen:** Door gevoelige gegevens te centraliseren en beter te beveiligen.
- **Leesbaarheid verbeteren:** Door gebruik te maken van flake8.
- **Gebruikerservaring verbeteren:** Door duidelijke foutmeldingen en consistent gedrag in de applicatie.

---

## 1. **Te veel logica in routes**

**Tegengekomen probleem**:  
Routes zoals `/save/<item_type>` maar ook andere routes bevatten validatie, gegevensopslag en gebruikersfeedback in één functie. Dit zorgt voor lange en moeilijk leesbare code.

**Oplossing**:  
Verplaats de logica naar aparte helpers.py, hierdoor wordt de code beter gestructureerd en testbaar.

**Afweging**:  
- *Voordeel*: Betere leesbaarheid en herbruikbaarheid van de code.  
- *Nadeel*: Kost tijd om de helper-functies te implementeren.  

**Voorbeeld**:  
In plaats van met als voorbeeld save van photos:  
```python
@app.route('/save/<item_type>', methods=["POST"])
@login_required
def save_item(item_type):
    user_id = session["user_id"]
    data = request.form

    if item_type == "photo":
        url = request.form.get("image_url")
        description = request.form.get("description", "No description available")
        # Create unique image_id, with a hash
        image_id = hashlib.md5(url.encode()).hexdigest()

        if not url:
            flash("Missing image data.", "error")
            return redirect(request.referrer)

        existing_like = SavedImage.query.filter_by(user_id=user_id, image_id=image_id).first()
        if existing_like:
            flash("You have already liked this image!", "warning")
            return redirect(request.referrer)

        new_like = SavedImage(
            user_id=user_id,
            image_id=image_id,
            url=url,
            description=description
        )

        db.session.add(new_like)
        db.session.commit()

        flash("Image liked successfully!", "success")
```

Gebruik:  
```python
@app.route('/save/<item_type>', methods=["POST"])
@login_required
def save_item(item_type):
    """
    Save an item (photo, art, or recipe) to the user's favorites.
    Determines the item type and processes it accordingly.
    """
    # Retrieve the current user's ID from the session
    user_id = session["user_id"]

    # Retrieve form data from the POST request
    data = request.form

    # Process the item based on its type
    if item_type == "photo":
        process_photo(data, user_id)
```

En voeg de logica toe in een helper-functie:  
```python
def process_photo(data, user_id):
    """
    Process and save a photo item for the user.

    Args:
        data (dict): The form data containing photo information.
        user_id (int): The ID of the user saving the photo.
    """
    image_url = data.get("image_url")
    if not image_url:
        flash("Invalid image URL.", "error")
        return

    # Generate image_id as a unique hash of the image_url
    image_id = md5(image_url.encode()).hexdigest()

    existing_photo = SavedImage.query.filter_by(
        user_id=user_id,
        image_id=image_id
    ).first()

    if existing_photo:
        flash("Photo already saved.", "info")
        return

    new_image = SavedImage(
        user_id=user_id,
        image_id=image_id,
        url=image_url,
        description=data.get("description", "No description available"),
    )

    try:
        db.session.add(new_image)
        db.session.commit()
        flash("Photo saved successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving photo: {e}", "error")
```

---

## 2. **Centraliseer API-configuratie**

**Tegengekomen probleem**:  
API-sleutels en configuraties zoals headers zijn verspreid door de code. Vooral voor UNPLASH die gebruikt wordt in de index en bij photos. 

**Oplossing**:  
Verplaats alle API-configuratie naar een `config.py`. 

**Afweging**:  
- *Voordeel*: Makkelijker onderhoud en betere beveiliging.  
- *Nadeel*: Kleine herstructurering.  

**Voorbeeld**:  
Huidige situatie:  
```python
headers = {"Authorization": f"Client-ID {Config.UNSPLASH_API_KEY}"}
```

Verbetering met `.env`:  
```python
import os
headers = {"Authorization": f"Client-ID {os.getenv('UNSPLASH_API_KEY')}"}
```
---

## 3. **Beveiligingsproblemen**

**Tegengekomen probleem**:  
Opvolgend porbleem van 2, zorg dat de API-sleutels en URI's veilig in .env staan en haal ze op via config.py

**Oplossing**:  
Plaats alle gevoelige gegevens in een `.env` bestand en laad ze in met `os.getenv()`.

**Afweging**:  
Geen, veel beter zo. 
---

## 4. **Consistent blijven**

**Tegengekomen probleem**:  
Niet alle routes geven feedback bij fouten, zoals `/recipes` wanneer er geen resultaten zijn. Ook is er niet over een method GET/POST toegevoegd.

**Oplossing**:  
Zorg voor `flash()`-meldingen bij succes en fouten.

**Afweging**:  
- *Voordeel*: Betere gebruikerservaring.  
- *Nadeel*: Extra meldingen implementeren kan tijd kosten.  

**Voorbeeld**:  
```python
if not data or not data.get("hits"):
    flash("No recipes found. Please try another query.", "warning")
    return render_template('recipes.html', recipes=[], query=query)
```

---

## 5. **Herhalingen in API-aanroepen**

**Tegengekomen probleem**:  
De logica voor API-aanroepen wordt herhaald voor Unsplash, Rijksmuseum en Edamam.

**Oplossing**:  
Maak een helper-functie `fetch_api_data` om herhaling weg te halen.

**Voorbeeld**:  
```python
def fetch_api_data(api_url, params=None, headers=None):
    """
    Fetch data from an API endpoint using requests.

    Args:
        api_url (str): The API URL.
        params (dict): Query parameters for the API request.
        headers (dict): HTTP headers for the API request.

    Returns:
        dict: The JSON response from the API or None if an error occurs.
    """
    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return None
```

---

## 6. **Lange routes en duplicatie**

**Tegengekomen probleem**:  
Routes zoals `/doodles` bevatten te veel logica voor het ophalen, genereren en weergeven van doodles.

**Oplossing**:  
Splits de verantwoordelijkheden in meerdere functies.

**Voorbeeld**:  
```python
@app.route("/doodles", defaults={"date": None}, methods=["GET", "POST"])
@app.route("/doodles/<date>", methods=["GET", "POST"])
@login_required
def doodles(date):
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for("doodles"))
    else:
        selected_date = datetime.now().date()

    # Fetching data
    todays_doodles = fetch_doodles_by_date(selected_date)
    submissions = fetch_doodle_submissions_and_likes(selected_date)
    total_likes, most_liked_doodles = calculate_doodle_statistics(submissions)
    user_likes = fetch_user_likes(session['user_id'])
    all_dates = fetch_all_doodle_dates()

    # Generate a new doodle for today if it doesn't exist
    if not todays_doodles and selected_date == datetime.now().date():
        filename = generate_daily_scribble()
        new_doodle = Doodle(filename=filename, date=selected_date)
        db.session.add(new_doodle)
        db.session.commit()
        todays_doodles.append(new_doodle)

    return render_template(
        "doodles.html",
        today=selected_date.strftime("%Y-%m-%d"),
        todays_doodles=todays_doodles,
        submissions=submissions,
        total_likes=total_likes,
        most_liked_doodles=most_liked_doodles,
        user_likes={like.doodle_id for like in user_likes},
        all_dates=all_dates
    )

def fetch_doodles_by_date(selected_date):
    """
    Retrieve all doodles for a specific date from the database.

    Args:
        selected_date (date): The date to filter doodles by.

    Returns:
        list: A list of Doodle objects for the selected date.
    """
    return Doodle.query.filter(Doodle.date == selected_date).all()


def get_todays_doodle():
    """
    Retrieve today's Doodle of the Day from the database.

    Returns:
        Doodle: The Doodle object for today's date, or None if not found.
    """
    today = datetime.now().date()
    return Doodle.query.filter(Doodle.date == today).first()

```

---

## 7. **Foutafhandeling verbeteren**

**Tegengekomen probleem**:  
Routes en API-aanroepen hebben geen duidelijke foutmeldingen voor gebruikers.

**Oplossing**:  
Geef gebruikers zinvolle foutmeldingen en log fouten voor debugging.

**Voorbeeld**:  
```python
try:
        # Fetch data from Unsplash API
        data = fetch_api_data(Config.UNSPLASH_RANDOM_URL,
                          params=params, headers=headers)
        # Extract and format image data
        images = [
            {"id": generate_hash(img["urls"]["regular"]),
             "url": img["urls"]["regular"]}
            for img in data if "urls" in img and "regular" in img["urls"]
        ] if data else []
    except Exception as e:
        flash("Error fetching images. Please try again later.", "error")
        print(f"Error fetching images: {e}")
        images = []
```

---

# Verbeterpunten: 8 t/m 10

## 8. **Voeg Flake8 toe voor een nette code**

**Tegengekomen probleem:**  
Niet alle code voldoet aan de standaarden, wat zorgt voor inconsistenties en mogelijke moeilijkheden bij het lezen en onderhouden van de code.

**Oplossing:**  
Gebruik Flake8 om code consistent te maken met de juiste richtlijnen. Voeg Flake8 toe aan de projectvereisten en voer het uit om overtredingen te identificeren.

### Afweging:
- **Voordeel:** Code wordt consistent, beter leesbaar en voldoet aan industriestandaarden.
- **Nadeel:** Kost wat tijd om bestaande fouten op te lossen.

### Uitwerking:  
   Verbeter code die niet aan de richtlijnen voldoet. Zorg bijvoorbeeld voor:
   - Correcte witruimte.
   - Geen lange regels (gebruik max. 79 karakters).
   - Juiste naamgevingsconventies.


---

## 9. **Voeg structuur toe in app.py en helpers.py**

**Tegengekomen probleem:**  
`app.py` en `helpers.py` bevatten veel verschillende functies zonder duidelijke scheiding.

**Oplossing:**  
Introduceer een logisch structuur in de bestanden, bijvoorbeeld door:
1. **Groepering van functies op basis van functionaliteit.**
2. **Toevoegen van sectiecommentaar en docstrings.**

### Afweging:
- **Voordeel:** Verbeterde leesbaarheid en onderhoudbaarheid.
- **Nadeel:** Geen.

### Voorbeeldstructuur:
- **app.py**:
   ```python
   # _________________________________________________________________________#
   #                               HOMEPAGE                                   #
   # _________________________________________________________________________#
   @app.route('/')
   def index():
       ...

   # _________________________________________________________________________#
   #                           SAVE/DELETE ITEMS                              #
   # _________________________________________________________________________#
   @app.route('/save/<item_type>', methods=["POST"])
   @login_required
   def save_item(item_type):
       ...
   ```

- **helpers.py**:
   ```python
   # _________________________________________________________________________#
   #                               RECIPES                                    #
   # _________________________________________________________________________#
   def process_recipe(data, user_id):
       ...

   # _________________________________________________________________________#
   #                               PHOTOS                                     #
   # _________________________________________________________________________#
   def process_photo(data, user_id):
       ...
   ```
---

## 10. **Verwijder ongebruikte imports en afhankelijkheden**

**Tegengekomen probleem:**  
Sommige imports en afhankelijkheden in `requirements.txt` worden niet gebruikt.

**Oplossing:**  
Controleer welke imports en pakketten daadwerkelijk nodig zijn, en verwijder de rest.

### Afweging:
- **Voordeel:** Minder afhankelijkheden betekent snellere installatie en minder kwetsbaarheden.
- **Nadeel:** Vereist een goede controle van de imports en pakketten.
  

## Conclusie  

Deze verbeterpunten maken de begrijpelijkheid, onderhoudbaarheid en beveiliging van de code een stuk beter. Door logica te centraliseren in helpers.py, routes te verkleinen en gevoelige gegevens beter te beveiligen in .env, wordt de code prettiger om mee te werken. Veel aanpassingen waren zeker de moeite waard. Ik heb vooral veel tijd besteed aan alle logica uit app.py te filteren en het in helpers.py met de juiste defenities te implementeren.
