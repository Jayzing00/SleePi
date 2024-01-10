# Was ist SleePi?

SleePi ist ein innovatives IoT-Projekt, das darauf abzielt, die Schlafumgebung aktiv zu überwachen und Feedback darüber zu geben, wie die aktuelle Umgebung beschaffen ist. Durch die Erfassung verschiedener Umweltparameter hilft SleePi dabei, ein besseres Verständnis und eine Kontrolle über die Faktoren zu gewinnen, die den Schlaf beeinflussen.

# Wie haben wir SleePi erstellt?

Für die Entwicklung von SleePi haben wir uns für die Verwendung des Grove-Systems entschieden. Wir nutzten spezifische Sensoren, um relevante Daten über die Schlafumgebung zu sammeln. Diese Sensoren umfassen:

- Loudness Sensor: Zur Erfassung von Geräuschpegeln.
- Light Sensor: Zur Messung der Lichtverhältnisse.
- Humidity & Temperature Sensor: Für die Überwachung von Luftfeuchtigkeit und Temperatur.

Links zu den Sensoren:

- [Temperatur & Humidity sensor](https://wiki.seeedstudio.com/Grove-TempAndHumi_Sensor-SHT31/)
- [Loudness sensor](https://wiki.seeedstudio.com/Grove-Loudness_Sensor/)
- [Light sensor](https://wiki.seeedstudio.com/Grove-Light_Sensor/)

---

# Setup

Um SleePi einzurichten, folgen Sie diesen Schritten:

1. **Grove.py herunterladen**: Zuerst müssen Sie das Grove.py-Repository von GitHub herunterladen. Verwenden Sie dazu den Befehl:

   ```
   git clone https://github.com/Seeed-Studio/grove.py
   ```

2. **Virtuelles Environment erstellen**: Innerhalb des heruntergeladenen Verzeichnisses erstellen Sie ein virtuelles Environment mit:

   ```
   python -m venv venv
   ```

3. **IoT-Ordner erstellen**: Erstellen Sie im "grove"-Verzeichnis einen Ordner mit dem Namen "IoT". Dieser Ordner wird den gesamten Code beinhalten, der auf dem GitHub-Repository zu finden ist.

   ```
   mkdir IoT
   ```

   Kopieren Sie dann den gesamten Projektcode in diesen "IoT"-Ordner.

4. **Abhängigkeiten installieren**: Aktivieren Sie das virtuelle Environment und installieren Sie die erforderlichen Abhängigkeiten über die `requirements.txt`:

   ```
   source venv/bin/activate
   pip install -r requirements.txt
   ```

# Bedienung

Nachdem das Setup abgeschlossen ist, können Sie SleePi über das Dashboard steuern. Führen Sie dazu einfach den folgenden Befehl aus:

```
python dashboard.py
```

Vergewissern Sie sich, dass Sie sich im richtigen Verzeichnis befinden und das virtuelle Environment aktiviert ist. Mit diesem Befehl starten Sie das Dashboard, über das Sie die erfassten Daten einsehen und verwalten können.

---
