# Concept - Inspire Your Artistry

**Auteur**: Annelaure van Overbeeke

Concept website is een platform ontworpen voor artiesten en creatieve geesten om inspiratie te vinden, kunstwerken te delen, en creatieve skills te verbeteren. Van het opslaan van foto's, kunstwerken en recepten tot het spelen van een dagelijkse creatieve uitdaging genaamd "Doodle" – Concept is dé plek om creativiteit te laten bloeien.

---

## **Over het project**

Creatify biedt een inspiratieplek waar gebruikers hun ideeën kunnen bewaren en uitbreiden. Het platform bestaat uit verschillende functies:

- **Opslaan van Inspiratie**: Upload en bewaar foto's, kunstwerken, en recepten op één plek.
- **Doodle Spel**: Een dagelijkse uitdaging waar een willekeurige kras je uitdaagt om een unieke tekening te maken. 
- **Ranking & Likes**: Bekijk populaire doodles per dag, like jouw favorieten, en verbeter je score in de ranglijst.
- **Openbare API**: Ontwikkelaars kunnen toegang krijgen tot ingezonden doodles via een API.

Creatify combineert community, creativiteit, en technologie in één platform.

---

## **Features**

### **Opslag voor inspiratie**
Bewaar en organiseer afbeeldingen, recepten, en kunstwerken. Perfect om een moodboard te maken of ideeën voor je volgende project vast te leggen.

### **Doodle Spel**
Laat je creativiteit de vrije loop met het dagelijkse Doodle-spel:
1. Elke dag wordt een willekeurige kras (scribble) gegenereerd.
2. Maak een tekening gebaseerd op de kras.
3. Upload je kunstwerk en deel het met de community.
4. Verzamel likes en kom in de dagelijkse ranglijst!

### **Community Features**
- Bekijk en like kunstwerken van andere gebruikers.
- Doe inspiratie op door rond te kijken in de openbare galerie.

### **Openbare API**
Creatify biedt een API waarmee externe ontwikkelaars toegang krijgen tot doodles, inclusief informatie over likes en uploaddata. Ideaal voor integratie in andere creatieve applicaties.

---

## **Installatie**

### **Benodigdheden**
1. **Python 3.10+**
2. Virtuele omgeving: `venv`
3. PostgresSQL database

### **Stappen**
1. Clone de repository:
   ```bash
   git clone https://github.com/jouw-repo-url
   cd jouw-repo
   ```

2. Installeer vereisten:
   ```bash
   pip install -r requirements.txt
   ```

3. Maak een `.env` bestand en voeg de vereiste configuraties toe:
   ```
   DATABASE_URL=postgresql://<gebruikersnaam>:<wachtwoord>@localhost/<database>
   SECRET_KEY=mijn-geheime-sleutel
   ```

4. Initializeer de database:
   ```bash
   flask db upgrade
   python create.py
   ```

5. Start de server:
   ```bash
   flask run
   ```

6. Ga naar [http://localhost:5000](http://localhost:5000) om Creatify te gebruiken!

---

## **API-Gebruik**

De Creatify API biedt toegang tot de ingezonden doodles:

### **Endpoints**
- **`GET /api/doodles`**: Haal alle doodles op.
- **`GET /api/doodles/filter?date=YYYY-MM-DD`**: Haal doodles op een specifieke datum op.
- **`POST /api/doodles`**: Voeg een nieuwe doodle toe (vereist authenticatie).

### **Voorbeeld Curl-aanroep**
```bash
curl -H "x-api-key: mijn-doodles" http://localhost:5000/api/doodles/filter?date=2024-12-16
```

---

## **Screenshots**

### **Hoofdpagina**
Inspiratie overzicht en toegang tot opgeslagen ideeën.

![Hoofdpagina](data/images/homepage.png)

### **Doodle-spel**
Kijk hoe een simpele kras verandert in een kunstwerk.

![Doodle Spel](data/images/doodle-game.png)

---

## **Projectstructuur**

- **`/app.py`**: Beheert de routes en functionaliteit van de applicatie.
- **`/models.py`**: Database-modellen voor gebruikers, doodles, en andere tabellen.
- **`/scribble.py`**: Logica voor het genereren van dagelijkse doodles.
- **`/static/` en `/templates/`**: Bevat statische bestanden en HTML-templates.
- **`/requirements.txt`**: Lijst van benodigde Python-packages.

---

## **Referenties**

1. [Flask Documentation](https://flask.palletsprojects.com/)
2. [PostgreSQL Documentation](https://www.postgresql.org/docs/)
3. [Jinja2 Templating](https://jinja.palletsprojects.com/)

---

Creatify is een project gemaakt met passie voor creativiteit en community. Gebruik het, deel je kunst, en laat je inspireren!
