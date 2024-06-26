# Inhaltsverzeichnis
- [0. Applikation ausführen](#0---applikation-ausführen)
- [1. Datenmodell](#1---datenmodell)
- [2. Fahrplan und Testfälle](#2---fahrplan-und-testfälle)
  - [Testdaten](#testdaten)
  - [Testszenarien](#testszenarien)
- [3. Verwendete APIs](#3---verwendete-apis)
- [4. Problemstellungen/Lösungen](#4---problemstellungensungen)
  - [Aktionen](#aktionen)
  - [Verbindungssuche](#verbindungssuche)
  - [Ticketkauf + Sitzplatzreservierung](#ticketkauf)

# 0.   Applikation ausführen

Repository klonen und folgende Befehle in der Shell ausführen:
```
cd Ticket
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# 1.   Datenmodell

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/615956f4-92b3-472b-a8f3-30383d2a9ed3">


# 2.   Fahrplan und Testfälle

## Testdaten

<img width="463" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/0e8402ed-a06b-4c5e-973d-9317b2a1d372">
<img width="431" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/96b341e1-fae9-4f0e-984e-eafe2a58b921">

## Testszenarien:

1.     Ohne Umstieg

Steyr Bahnhof -- St. Valentin Bahnhof 

01.01.2024

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/50b4b42c-c113-4aec-b425-77109501903e">


2.     Mit Umstieg

Steyr Bahnhof -- Wien

01.01.2024

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/cba56974-38fb-417b-8741-943c0b445240">


3.     Mit 50% Rabatt Aktion

Linz HBF -- Graz HBF

01.01.2024

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/4003ff22-b1db-4eb1-95f0-786ab9c9a74f">


4.     Ohne Warnungen

WienHBF -- Salzburg HBF

01.06.2026

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/704478aa-cdca-4682-975a-4d2a114cc71e">


5.     Mit Warnungen

WienHBF -- Salzburg HBF

01.06.2024

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/00d7edec-c3b5-486f-adcd-d26540c9c662">


6.     Sitzplatzbuchung (Testszenario: Züge haben 2 Sitzplätze)

Steyr Bahnhof -- Wien

01.01.2024

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/3d41cfad-5d1a-4e14-8e57-adfc3265711b">


Weitere Sitzplatzbuchung:

Steyr Bahnhof -- Ramingdorf

01.01.2024

08:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/8b8480dc-e988-4ce2-9098-874235ebea3b">


Weitere Sitzplatzbuchung:

Steyr Bahnhof -- Ramingdorf

01.01.2024

08:00

**Fehler: Keine verfügbaren Sitzplätze für die Strecke**

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/8e6d189d-5e78-41f3-8b40-e102414ab0a4">
<img width="342" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/1b6bdc8b-6a26-42e5-aaee-75b08c7d20c6">


Weitere Sitzplatzbuchung zu anderer Uhrzeit:

Steyr Bahnhof -- Ramingdorf

01.01.2024

09:00

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/25f2bb31-a847-4842-9411-3893f8267cc1">
<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/3cfa0d6f-d452-4cc1-a3af-96ae43e31d9d">


7.     Ticket stornieren

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/6b2142e7-d0c3-4bfc-9073-5ef98dc601df">


Klick auf Stornieren:

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/573667b7-4087-427c-967b-1b9a8750bf49">


8.     Ticket in der Vergangenheit

Wird beim Aufruf der Ticketpage berechnet.

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/dda32708-11c2-42b2-8bdb-e895ebc61e1c">


9.     Globale Aktion anlegen

Login als Admin User, oder direkt über Link: <https://tickets.max-oberaigner.eu/admin>

Klick auf „neue Aktion"

-      Validierung auf Startdatum vor Enddatum

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/5020ba34-537d-49af-b78d-20805581ee7f">
<img width="421" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/c4e1f7b9-42b8-4dfd-9725-3a9c25f72ddd">


-      Validierung Datum muss heute oder in der Zukunft liegen

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/dfb4b98e-70de-4419-833a-de00d3c52f1f">

<img width="420" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/cd2fa2e2-4d11-446b-b6fa-36e1af59e472">


-      Gültige Aktion anlegen

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/1022d028-916a-4722-bcea-b52804136768">

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/23ffe224-a6e1-46ee-8954-565679f2c0bf">

10.  Globale Aktion bearbeiten

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/8979e966-fb16-4ba5-923d-4a1c61be732b">


Änderung Rabatt auf 30%

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/89977daa-9296-457f-819c-66c3eba202b6">


11.  Globale Aktion löschen

-      Tickets wurden bereits gekauft

Klick auf Löschen:
<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/b8561904-7e29-4eaa-92df-2b854f433ed3">


-      Tickets wurden noch nicht gekauft

Klick auf Löschen:

<img width="249" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/7ae42936-0bd5-49fe-a7d5-1dad7533b09b">

12.  Profil bearbeiten

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/5c042170-1926-4491-99ac-9477762168f8">


13.  Registrierung

<img width="334" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/8d087f35-4d05-48bc-947b-6f73ee454420">
<img width="357" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/dfb9a09d-93fa-44b4-89e3-768267d77a3f">



Datenbank:

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/85f0c651-9a7d-44be-901c-336628862a35">


Login:

<img width="454" alt="image" src="https://github.com/lnoemeyer/PRDKE/assets/32127275/7a2e537e-704e-4b62-91ed-5802ffeea50d">


# 3.   Verwendete APIs

-      Fahrplan

o   Die folgende API liefert alle Fahrplane retour

@app.route('/api/railwayschedules', methods=['GET']) # selbst erstellte Test-API, da Teamkollege ausgefallen ist

def api_railwayschedules():

    data = [

        {

            "date": "01.01.2024",

            "time": "08:00",

            "priceadjust_percent": 10,

            "railwayscheduleid": 1,

            "routeid": 6,

            "startstation": "Steyr Bahnhof",

            "endstation": "St.Valentin Bahnhof",

            "stationplan": [

                {

                    "start": "Steyr Bahnhof",

                    "end": "Steyr Munichholz Bahnhof",

                    "nutzungsentgeld": 5,

                    "duration": 15

                },

                {

                    "start": "Steyr Munichholz Bahnhof",

                    "end": "Ramingdorf",

                    "nutzungsentgeld": 18,

                    "duration": 10

                },

                {

                    "start": "Ramingdorf",

                    "end": "Enns",

                    "nutzungsentgeld": 2,

                    "duration": 20

                },

                {

                    "start": "Enns",

                    "end": "St.Valentin Bahnhof",

                    "nutzungsentgeld": 1.75,

                    "duration": 15

                }

            ],

            "crew": [

                {

                    "personalid": 1,

                    "name": "Tom Baum"

                },

                {

                    "personalid": 2,

                    "name": "Andrea Baum"

                }

            ],

            "train": {

                "trainid": 1,

                "train_name": "WB100"

            }

        },

        {

            "date": "01.01.2024",

            "time": "09:00",

            "priceadjust_percent": 10,

            "railwayscheduleid": 1,

            "routeid": 6,

            "startstation": "Steyr Bahnhof",

            "endstation": "St.Valentin Bahnhof",

            "stationplan": [

                {

                    "start": "Steyr Bahnhof",

                    "end": "Steyr Munichholz Bahnhof",

                    "nutzungsentgeld": 5,

                    "duration": 15

                },

                {

                    "start": "Steyr Munichholz Bahnhof",

                    "end": "Ramingdorf",

                    "nutzungsentgeld": 18,

                    "duration": 10

                },

                {

                    "start": "Ramingdorf",

                    "end": "Enns",

                    "nutzungsentgeld": 2,

                    "duration": 20

                },

                {

                    "start": "Enns",

                    "end": "St.Valentin Bahnhof",

                    "nutzungsentgeld": 1.75,

                    "duration": 15

                }

            ],

            "crew": [

                {

                    "personalid": 1,

                    "name": "Tom Baum"

                },

                {

                    "personalid": 2,

                    "name": "Andrea Baum"

                }

            ],

            "train": {

                "trainid": 1,

                "train_name": "WB100"

            }

        },

        {

            "date": "01.01.2024",

            "time": "10:00",

            "priceadjust_percent": 10,

            "railwayscheduleid": 1,

            "routeid": 6,

            "startstation": "Steyr Bahnhof",

            "endstation": "St.Valentin Bahnhof",

            "stationplan": [

                {

                    "start": "Steyr Bahnhof",

                    "end": "Steyr Munichholz Bahnhof",

                    "nutzungsentgeld": 5,

                    "duration": 15

                },

                {

                    "start": "Steyr Munichholz Bahnhof",

                    "end": "Ramingdorf",

                    "nutzungsentgeld": 18,

                    "duration": 10

                },

                {

                    "start": "Ramingdorf",

                    "end": "Enns",

                    "nutzungsentgeld": 2,

                    "duration": 20

                },

                {

                    "start": "Enns",

                    "end": "St.Valentin Bahnhof",

                    "nutzungsentgeld": 1.75,

                    "duration": 15

                }

            ],

            "crew": [

                {

                    "personalid": 1,

                    "name": "Tom Baum"

                },

                {

                    "personalid": 2,

                    "name": "Andrea Baum"

                }

            ],

            "train": {

                "trainid": 1,

                "train_name": "WB100"

            }

        },

        {

            "date": "01.06.2024",

            "time": "17:00",

            "priceadjust_percent": 10,

            "railwayscheduleid": 1,

            "routeid": 6,

            "startstation": "Steyr Bahnhof",

            "endstation": "St.Valentin Bahnhof",

            "stationplan": [

                {

                    "start": "Steyr Bahnhof",

                    "end": "Steyr Munichholz Bahnhof",

                    "nutzungsentgeld": 5,

                    "duration": 15

                },

                {

                    "start": "Steyr Munichholz Bahnhof",

                    "end": "Ramingdorf",

                    "nutzungsentgeld": 18,

                    "duration": 10

                },

                {

                    "start": "Ramingdorf",

                    "end": "Enns",

                    "nutzungsentgeld": 2,

                    "duration": 20

                },

                {

                    "start": "Enns",

                    "end": "St.Valentin Bahnhof",

                    "nutzungsentgeld": 1.75,

                    "duration": 15

                }

            ],

            "crew": [

                {

                    "personalid": 1,

                    "name": "Tom Baum"

                },

                {

                    "personalid": 2,

                    "name": "Andrea Baum"

                }

            ],

            "train": {

                "trainid": 1,

                "train_name": "WB100"

            }

        },

        {

            "date": "01.01.2024",

            "time": "11:00",

            "priceadjust_percent": 10,

            "railwayscheduleid": 1,

            "routeid": 9,

            "startstation": "Salzburg",

            "endstation": "Wien",

            "stationplan": [

                {

                    "start": "Salzburg",

                    "end": "Wels",

                    "nutzungsentgeld": 24,

                    "duration": 55

                },

                {

                    "start": "Wels",

                    "end": "Enns",

                    "nutzungsentgeld": 10,

                    "duration": 25

                },

                {

                    "start": "Enns",

                    "end": "Amstetten",

                    "nutzungsentgeld": 4,

                    "duration": 15

                },

                {

                    "start": "Amstetten",

                    "end": "Wien",

                    "nutzungsentgeld": 15,

                    "duration": 45

                }

            ],

            "crew": [

                {

                    "personalid": 1,

                    "name": "Tom Baum"

                },

                {

                    "personalid": 2,

                    "name": "Andrea Baum"

                }

            ],

            "train": {

                "trainid": 1,

                "train_name": "WB100"

            }

        },

        {

            "date": "01.01.2024",

            "time": "12:00",

            "priceadjust_percent": 15,

            "railwayscheduleid": 2,

            "routeid": 2,

            "startstation": "Linz HBF",

            "endstation": "Graz HBF",

            "stationplan": [

                {

                    "start": "Linz HBF",

                    "end": "Steyr Bahnhof",

                    "nutzungsentgeld": 8,

                    "duration": 40

                },

                {

                    "start": "Steyr Bahnhof",

                    "end": "Kapfenberg",

                    "nutzungsentgeld": 12,

                    "duration": 60

                },

                {

                    "start": "Kapfenberg",

                    "end": "Graz HBF",

                    "nutzungsentgeld": 10,

                    "duration": 50

                }

            ],

            "crew": [

                {

                    "personalid": 3,

                    "name": "Michaela Klein"

                },

                {

                    "personalid": 4,

                    "name": "Stephan Groß"

                }

            ],

            "train": {

                "trainid": 2,

                "train_name": "RB202"

            }

        },

        {

            "date": "01.01.2024",

            "time": "13:30",

            "priceadjust_percent": 10,

            "railwayscheduleid": 3,

            "routeid": 3,

            "startstation": "St.Valentin Bahnhof",

            "endstation": "Linz",

            "stationplan": [

                {

                    "start": "St.Valentin Bahnhof",

                    "end": "Enns",

                    "nutzungsentgeld": 2.5,

                    "duration": 15

                },

                {

                    "start": "Enns",

                    "end": "Linz",

                    "nutzungsentgeld": 5,

                    "duration": 25

                }

            ],

            "crew": [

                {

                    "personalid": 5,

                    "name": "Lara Müller"

                },

                {

                    "personalid": 6,

                    "name": "Jan Hofer"

                }

            ],

            "train": {

                "trainid": 3,

                "train_name": "IC300"

            }

        },

        {

            "date": "01.06.2024",

            "time": "13:30",

            "priceadjust_percent": 10,

            "railwayscheduleid": 3,

            "routeid": 1,

            "startstation": "WienHBF",

            "endstation": "Salzburg HBF",

            "stationplan": [

                {

                    "start": "WienHBF",

                    "end": "Wels HBF",

                    "nutzungsentgeld": 22.5,

                    "duration": 65

                },

                {

                    "start": "Wels HBF",

                    "end": "Salzburg HBF",

                    "nutzungsentgeld": 19,

                    "duration": 55

                }

            ],

            "crew": [

                {

                    "personalid": 5,

                    "name": "Lara Müller"

                },

                {

                    "personalid": 6,

                    "name": "Jan Hofer"

                }

            ],

            "train": {

                "trainid": 3,

                "train_name": "IC300"

            }

        },

        {

            "date": "01.06.2026",

            "time": "13:30",

            "priceadjust_percent": 10,

            "railwayscheduleid": 3,

            "routeid": 1,

            "startstation": "WienHBF",

            "endstation": "Salzburg HBF",

            "stationplan": [

                {

                    "start": "WienHBF",

                    "end": "Wels HBF",

                    "nutzungsentgeld": 22.5,

                    "duration": 65

                },

                {

                    "start": "Wels HBF",

                    "end": "Salzburg HBF",

                    "nutzungsentgeld": 19,

                    "duration": 55

                }

            ],

            "crew": [

                {

                    "personalid": 5,

                    "name": "Lara Müller"

                },

                {

                    "personalid": 6,

                    "name": "Jan Hofer"

                }

            ],

            "train": {

                "trainid": 3,

                "train_name": "IC300"

            }

        }

    ]

    return jsonify(data)

-      Flotte

o   Es wird hardgecoded angenommen, dass ein Zug 2 Sitzplätze hat - da Teamkollege ausgefallen ist.

-      Strecke

o   <http://localhost:5001/Strecken>

§  Fragt alle Strecken ab, um diese beim Hinzufügen von Aktionen auswählen zu können

      [{"abschnitte":[{"end":"StP\u00f6lten Bahnhof","id":2,"laenge":1243.0,"maxGeschwindigkeit":120,"nutzungsentgeld":15.0,"start":"WienHBF"},{"end":"Linz HBF","id":3,"laenge":1234.0,"maxGeschwindigkeit":453,"nutzungsentgeld":13.0,"start":"StP\u00f6lten Bahnhof"},{"end":"Wels HBF","id":4,"laenge":12.0,"maxGeschwindigkeit":342,"nutzungsentgeld":124.0,"start":"Linz HBF"},{"end":"Salzburg HBF","id":5,"laenge":2134.0,"maxGeschwindigkeit":223,"nutzungsentgeld":123.0,"start":"Wels HBF"}],"endbahnhof":"Salzburg HBF","id":1,"name":"Weststrecke","spurbreite":1435,"startbahnhof":"WienHBF"},{"abschnitte":[{"end":"Liezen HBF","id":6,"laenge":12.0,"maxGeschwindigkeit":120,"nutzungsentgeld":12.0,"start":"Linz HBF"},{"end":"Graz HBF","id":7,"laenge":9450.0,"maxGeschwindigkeit":10,"nutzungsentgeld":14.0,"start":"Liezen HBF"}],"endbahnhof":"Graz HBF","id":2,"name":"S\u00fcdbahnStrecke","spurbreite":1000,"startbahnhof":"Linz HBF"}]

o   [http://localhost:5001/StreckeVonBis/{route_id}/{departure_station}/{arrival_station}/Warnungen](http://localhost:5001/StreckeVonBis/%7broute_id%7d/%7bdeparture_station%7d/%7barrival_station%7d/Warnungen%22)

§  Liefert alle Warnungen zwischen 2 Haltestellen

[{"abschnittId":2,"beschreibung":"Achtung Eisb\u00e4r greift wahllos Z\u00fcge an!","endzeitpunkt":"2025-12-12T00:00:00","id":1,"name":"Eisb\u00e4rangriff","startzeitpunkt":"2020-12-12T00:00:00"},{"abschnittId":4,"beschreibung":"2,5 m Wasser auf den Gleisen bitte nur langsam fahren","endzeitpunkt":"2025-12-12T00:00:00","id":2,"name":"Hochwasser","startzeitpunkt":"2020-12-12T00:00:00"}]

# 4.   Problemstellungen/Lösungen

#### Aktionen

- **Aktionen mit gleichem Namen anlegen**
  - Wird bewusst erlaubt, da der Name kein primary key ist.

- **Aktionen löschen/bearbeiten**
  - Aktionen können nur gelöscht bzw. bearbeitet werden, wenn noch keine Tickets dazu existieren. Dies wird mit einer entsprechenden Methode überprüft und ggf. wird ein Fehler ausgegeben (siehe Testfälle):
    - `ticket_count = db.session.query(Section).filter(Section.promotion_id == promotion_id).count()`

- **Anwendung von Aktionen**
  - Eigene Methode, die die beste Aktion herausfindet:
    - Holt alle zutreffenden Aktionen (Route stimmt überein, oder globale Aktion) aus DB und prüft, ob diese am aktuellen Datum gültig sind.
    - Erste Aktion wird in Variable `best_discount` gespeichert. Geht alle Aktionen durch und prüft, ob diese besser ist als `best_discount` -> sonst wird diese in `best_discount` gespeichert.

#### Verbindungssuche

- **Methode zur Direktverbindungssuche**
  - **Parameter**
    - Schedules: Fahrpläne
    - `form_start_station`: Startbahnhof
    - `form_end_station`: Endbahnhof
    - `start_time`: gewünschte Abfahrtszeit
    - `end_time`: gewünschte späteste Abfahrtszeit (wird vorher berechnet: gewünschte Abfahrtszeit+24h)
  - **Algorithmus**
    - Alle Fahrpläne durchiterieren:
      - Bahnhofliste extrahieren
      - Start- und Endbahnhof liegen auf der Strecke in der richtigen Reihenfolge? -> sonst Sprung zum nächsten Schleifendurchgang
      - Zeit aufsummieren, da je Station nur die Zeit für diese Station gespeichert ist
      - Startbahnhof liegt auf diesem Fahrplan; in gewünschtem Zeitfenster (`start_time`, `end_time`)? -> ja
        - Abfahrtszeit speichern
        - `Boolean processing_route = true`
      - Startbahnhof gefunden? -> ja (`processing_route==true`)
      - Preise aufsummieren, da je Station nur der Preis für diese eine Station gespeichert ist
      - Endbahnhof liegt auf diesem Fahrplan?
        - Ankunftszeit speichern
      - Vorteilhafteste Aktion anwenden -> siehe oben im Dokument Methode bei Lösungsansatz für Aktionen
      - Gefundenes Ergebnis in Liste Speichern
    - Wurde Ergebnis gefunden?
      - Ja -> Return Liste
      - Nein -> Return Error

#### Ticketkauf

- **Ticket wurde bereits gefunden und auf der Detailseite wurde auf kaufen geklickt**
  - **Algorithmus**
    - Ticketdaten aus Zwischenspeicher auslesen
    - Sitzplatzreservierung berücksichtigen (siehe Details beim Punkt „Sitzplatzreservierung“ weiter unten)
    - Ticketobjekt erstellen und in DB speichern
    - Ticket mit Umstieg?
      - Ja
        - Pseudo-Ticket-Daten vor Umstieg aus Zwischenspeicher auslesen und mithilfe der Methode `save_section()` als Entität `Section` persistieren
        - Pseudo-Ticket-Daten nach Umstieg aus Zwischenspeicher auslesen und mithilfe der Methode `save_section()` als Entität `Section` persistieren
      - Nein
        - Pseudo-Ticket-Daten ohne Umstieg aus Zwischenspeicher auslesen und mithilfe der Methode `save_section()` als Entität `Section` persistieren
    - **Sitzplatzreservierung**
      - Methode `get_seat_number()`
        - **Parameter**: Alle „Pseudo-Ticketdaten“ aus Zwischenspeicher
        - **Zweck**: Sucht die nächste freie Sitzplatznummer
        - **Algorithmus**
          - Abfrage der Sitzplatzanzahl von API
          - Alle Sitzplatzreservierungen von diesem Zug und Tag aus Datenbank auslesen
          - Zeitlich überlappende Sitzplatzreservierungen filtern
          - Anzahl bisheriger Reservierungen kleiner als maximale Sitzplatzanzahl des Zugs?
            - Ja -> Rückgabe der höchsten Sitzplatznummer+1
            - Nein -> Rückgabe None
      - Wurde beim Ticketkauf die Sitzplatzreservierung angehakt? -> ja
        - Gesamtpreis um 3€ erhöhen (Annahme: Für Strecken mit Umstiegen verrechnen wir trotzdem nur die 3€)
        - Ticketobjekt erstellen und in DB speichern
        - Ticket mit Umstieg?
          - Ja
            - Abfrage der Sitzplatznummer mit `get_seat_number()` für Fahrt vor Umstieg
            - Abfrage der Sitzplatznummer mit `get_seat_number()` für Fahrt nach Umstieg
            - Sitzplatz für beide Fahrten gefunden?
              - Ja -> Persistierung der Sitzplätze
              - Nein (return None) -> Ausgabe Fehlermeldung
          - Nein
            - Abfrage der Sitzplatznummer mit `get_seat_number()` -> siehe oben
            - Sitzplatz gefunden?
              - Ja -> Persistierung des Sitzplatzes
              - Nein (return None) -> Ausgabe Fehlermeldung
