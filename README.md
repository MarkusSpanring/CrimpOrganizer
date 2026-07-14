# CrimpOrganizer — Benutzerhandbuch & Installation (README)

Willkommen beim **CrimpOrganizer**! Dieses Programm hilft Ihnen dabei, Ihre Crimpwerkzeuge (Zangen), Crimpkontakte und Kabelquerschnitte übersichtlich zu verwalten sowie professionelle Prüfberichte und Arbeitsanweisungen im PDF-Format auszudrucken.

---

## 1. Voraussetzungen & Installation (Für Einsteiger)

Da es sich um eine Web-Anwendung handelt, benötigen Sie keine komplizierte Installation. Folgen Sie einfach diesen Schritten:

### Schritt A: Git & Python installieren
Das Programm benötigt **Git** (zum Herunterladen des Codes) und **Python** (zum Ausführen des Programms):
1. **Python**: Laden Sie die aktuelle Version für Ihr Betriebssystem von [python.org](https://www.python.org/downloads/) herunter. *Wichtig bei Windows*: Setzen Sie bei der Installation den Haken bei **"Add Python to PATH"**.
2. **Git**: Laden Sie Git von [git-scm.com](https://git-scm.com/downloads) herunter und installieren Sie es.

### Schritt B: Code herunterladen & Ordner öffnen
1. Öffnen Sie die Eingabeaufforderung (Windows: `Win`-Taste -> `cmd` eingeben -> `Enter`) oder das Terminal (macOS/Linux).
2. Laden Sie das Programm über Git herunter, indem Sie Folgendes eingeben:
   ```bash
   git clone https://github.com/IhrBenutzername/CrimpOrganizer.git
   ```
3. Wechseln Sie in den heruntergeladenen Ordner:
   ```bash
   cd CrimpOrganizer
   ```

### Schritt C: Abhängigkeiten installieren & Starten
Geben Sie den folgenden Befehl im Terminal ein, um das Programm zu starten:

```bash
# Wenn Sie das moderne 'uv' Tool verwenden:
uv run python app.py

# Oder mit Standard-Python:
python app.py
```

Das Programm installiert beim ersten Start alle benötigten Pakete (wie Flask und ReportLab) automatisch.

### Schritt D: Im Webbrowser öffnen
Sobald das Programm gestartet ist, sehen Sie eine Meldung wie:
` * Running on http://127.0.0.1:5000`

1. Öffnen Sie Ihren bevorzugten Internet-Browser (z.B. Google Chrome, Firefox oder Microsoft Edge).
2. Geben Sie oben in der Adresszeile **`http://localhost:5000`** ein und drücken Sie `Enter`.
3. Sie sehen nun die Benutzeroberfläche des CrimpOrganizers!

---

## 2. Anleitung zur Benutzung

Die Anwendung ist in drei Hauptbereiche unterteilt:

### 1. Zangen-Verwaltung (Linke Spalte)
Hier verwalten Sie Ihre Crimpzangen:
* **Neue Zange hinzufügen**: Klicken Sie oben auf das grüne Plus-Symbol (`+`).
* **Zange bearbeiten**: Klicken Sie auf das blaue Stift-Symbol (`✏️`) neben der jeweiligen Zange.
  * Hier können Sie den **Hersteller**, die **Serie** und die **Artikelnummer** ändern.
  * **Einsätze (Slots)**: Geben Sie z.B. einen AWG-Wert und Querschnitt ein und klicken Sie auf **Hinzufügen**. Einträge können über das kleine `×` direkt gelöscht werden.
  * **Zangen-IDs**: Fügen Sie die spezifische Identifikationsnummer (z.B. Z-003) Ihrer Zange hinzu.
  * Der **Speichern**-Button wird erst aktiv, wenn Sie tatsächlich Werte im Dialog geändert haben.

### 2. Kontakt-Verwaltung (Rechte Spalte)
Hier verwalten Sie Ihre Crimpkontakte und weisen ihnen passende Zangen zu:
* **Neuer Kontakt**: Klicken Sie oben rechts auf das Plus-Symbol (`+`).
* **Kontakt bearbeiten**: Klicken Sie auf das blaue Stift-Symbol (`✏️`) neben dem jeweiligen Kontakt.
  * Geben Sie die **Artikelnummer (Referenz)**, **Serie**, **Hersteller** und den **Crimp-Typ** (offen/geschlossen) ein.
  * **Crimpzange & Slot zuweisen**:
    1. Wählen Sie den gewünschten **Querschnitt**, die **Crimpzange** und den **Slot** (Einsatz) aus den Dropdowns aus.
    2. Tragen Sie die geforderte Zugkraft (**Soll-Wert (N)**) ein.
    3. Sobald alle 4 Zuweisungs-Felder ausgefüllt sind, leuchtet der **Hinzufügen**-Button blau auf. Klicken Sie darauf, um die Zuweisung in die Tabelle einzutragen.
    4. Klicken Sie am Ende des Dialogs auf **Speichern**.

### 3. Zangen-Filter (Die "Hinzufügen"-Funktion)
Wenn Sie eine Zange in der linken Liste durch Anklicken auswählen:
* Die Kontaktliste filtert sich automatisch und zeigt nur noch Kontakte an, die mit dieser Zange kompatibel sind.
* Die Tabelle blendet eine neue Spalte **Querschnitt** ein. Hier sehen Sie einen Button (z.B. `+ 0.50 mm² hinzufügen`).
* Klicken Sie auf diesen Button, um den Kontakt mit dem entsprechenden Querschnitt direkt in die aktuelle Crimp-Auftragsliste zu übernehmen.

### 4. Auftragsliste (Unten) & PDF-Druck
Im unteren Bereich wird Ihr aktueller Crimp-Auftrag zusammengestellt:
* Sie sehen alle hinzugefügten Kontakte, Querschnitte, die zugewiesene Zange, den Slot und die Soll-Zugkraft.
* Über das rote Mülleimer-Symbol können Sie Einträge entfernen.
* Klicken Sie rechts unten auf **Drucken (PDF)**.
* Ein Dialog öffnet sich, in dem Sie **Bestellnummer**, **Auftragsnummer** und **Prüfprotokollnummer** eingeben können.
* Klicken Sie auf **Drucken**, um ein professionelles PDF-Dokument mit allen Arbeitsanweisungen und Tabellen für den Zugtest zu erstellen und abzuspeichern.
* Über **Auftrag leeren** können Sie die Liste für den nächsten Auftrag zurücksetzen.

### 5. Auto-Update (Anwendung aktualisieren)
Wenn eine neue Version des Programms im Git-Repository vorliegt:
* Klicken Sie in der linken Menüleiste ganz unten auf **Update** (🔄).
* Bestätigen Sie die Abfrage. Das Programm lädt den neuesten Code herunter, startet sich selbstständig neu und lädt die Webseite nach wenigen Sekunden automatisch neu.

---

## 3. Einstellungen (Soll-Zugkräfte konfigurieren)
Klicken Sie oben rechts auf das Zahnrad-Symbol (`⚙️`), um die Standard-Zugkräfte für verschiedene Querschnitte festzulegen:
* Fügen Sie neue Querschnitte hinzu und tragen Sie die Soll-Zugkräfte (in Newton, N) für offene und geschlossene Hülsen ein.
* Diese Werte werden beim Zuweisen von Zangen im Kontakt-Editor automatisch als Standard vorgeschlagen.
