# Concept

## Het Probleem
Veel mensen zoeken naar unieke vintage en tweedehands items, zoals kleding en meubels, maar hebben beperkte toegang tot lokale markten zoals Waterlooplein. Deze markten zijn vaak alleen fysiek toegankelijk, wat het lastig maakt voor zowel kopers als verkopers om buiten hun directe omgeving te komen. Dit project digitaliseert het aanbod van lokale markten, waardoor bezoekers eenvoudig toegang krijgen tot unieke items zonder fysiek aanwezig te hoeven zijn.

## Gebruikers
- **Primair:** Vintage- en tweedehandsliefhebbers die op zoek zijn naar unieke items, maar beperkt zijn in hun fysieke bereik.
- **Secundair:** Lokale marktkramers die hun bereik willen vergroten door hun aanbod online te presenteren.

## Setting
De website is ontworpen om te worden gebruikt op laptops en desktops voor een optimale browse-ervaring, maar is ook toegankelijk op mobiele apparaten voor gebruikers die onderweg zijn.

## Vernieuwende Factor
In tegenstelling tot algemene marktplaatsen zoals Vinted, richt **Concept** zich uitsluitend op lokale markten en hun unieke aanbod. Gebruikers kunnen door vintage items van specifieke markten bladeren en ontdekken wat er te koop is, inclusief historische en culturele context van de markt.

Inspiratie voor het ontwerp:
- [Oblist](https://oblist.com/)
- [Etsy](https://www.etsy.com/)
- [Marktplaats](https://www.marktplaats.nl/)
- [Gohar World](https://gohar.world/)
- [Feisty Feast](https://feistyfeast.com/)

## schets
![Schets van Concept](programmeerproject/search_results.jpeg)

## Features
### Totale Lijst
- **Homepage:** Met een visueel aantrekkelijke lijst van highlights en aanbevolen items.
- **Zoekfunctionaliteit:** Inclusief filters op categorie (bijv. kleding, meubels, accessoires).
- **Categoriepagina's:** Laten de verschillende types items zien met visuals en beschrijvingen.
- **Verkopersprofielen:** Een sectie voor elke marktkramer om hun aanbod en achtergrondinformatie weer te geven.
- **Productpagina:** Gedetailleerde productpagina's met foto’s, beschrijvingen, prijzen en de mogelijkheid om contact op te nemen met de verkoper.
- **Interactiviteit met Kaart:** Gebruikers kunnen zien waar de fysieke locatie van de verkoper is, met een kaart die marktkramen weergeeft.
- **Betaalfunctionaliteiten:** Integratie van Stripe of PayPal voor veilige betalingen.

### Cruciale Lijst
- **Homepage met highlights** en categorieën.
- **Categoriepagina's** met filters voor efficiënt browsen.
- **Productpagina's** met gedetailleerde informatie.
- **Veilig betaalsysteem** voor transacties.

### Niet-Cruciale Lijst
- **Interactie met een kaart** die de fysieke locatie van marktkramen toont.
- **Aanbevelingsfunctie** voor vergelijkbare producten.
- **Verkopersprofielen** met achtergrondinformatie en foto’s van hun kraam.

## Requirements
### API's
1. **Stripe API** of **PayPal API** voor betalingen.
2. **Algolia API** voor geavanceerde zoekfunctionaliteit met filters.
3. **Google Maps API** voor locatie-integratie en kaartweergave.
4. **Cloudinary API** voor het optimaliseren en beheren van productafbeeldingen.
5. **Firebase Authentication** of **Auth0** voor veilige gebruikersauthenticatie.

### Frameworks en Tools
- **Frontend:** Next.js (React Framework) voor een snelle, interactieve gebruikerservaring.
- **Backend:** Node.js of Django voor server-side logica en API endpoints.
- **Database:** MongoDB of PostgreSQL voor gebruikers- en productgegevens.
- **Styling:** Tailwind CSS voor een moderne en minimalistische interface die lijkt op Oblist.

## Uitdagingen en Risico's
1. **UI/UX Complexiteit:**
   - Het creëren van een visueel aantrekkelijk ontwerp zoals Oblist, terwijl het eenvoudig blijft voor alle gebruikers.
   - **Oplossing:** Focus op een clean design en maak gebruik van component libraries zoals Tailwind CSS.
   
2. **Zoekfunctionaliteit en Filteropties:**
   - Het implementeren van een krachtige zoekfunctie om specifieke items te vinden.
   - **Oplossing:** Gebruik Algolia voor geavanceerde zoek- en filtermogelijkheden.

3. **Beveiligde Transacties:**
   - Verkopers en kopers moeten een veilige ervaring hebben bij het uitvoeren van transacties.
   - **Oplossing:** Gebruik bewezen betalingsproviders zoals Stripe en PayPal voor integratie.

## Visuele Opzet
De interface is geïnspireerd door Oblist en richt zich op minimalisme en duidelijkheid:
- **Minimalistisch design:** Een heldere, foto-gebaseerde interface die gebruikers gemakkelijk door het aanbod laat navigeren.
- **Grid lay-out:** Voor categorieën en productoverzicht.
- **Prominente zoekbalk:** Voor het gemakkelijk vinden van specifieke items.
- **Interactieve kaart:** Voor het tonen van fysieke locaties van verkopers.

