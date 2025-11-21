# `pdfc` – PDF Compressor for the Command Line

sharpen = 0.0 bis unbegrenzt (float)

## Sharpen (`-s`, `-sharpen`) and Contrast (`-c`, `-contrast`)

### Praktische Bereiche

| Wert | Effekt | Verwendung |
|------|--------|------------|
| **0.0** | Komplett unscharf (blur) | Nicht empfohlen |
| **0.5** | Leicht unscharf | Rauschreduzierung |
| **1.0** | Original (keine Änderung) | Baseline |
| **1.2-1.5** | Leichte Schärfung | ✅ Empfohlen für normale Dokumente |
| **1.5-2.0** | Mittlere Schärfung | ✅ Gut für Text |
| **2.0-2.5** | Starke Schärfung | Für sehr unscharfe Scans |
| **2.5-3.0** | Sehr starke Schärfung | ⚠️ Risiko von Artefakten |
| **>3.0** | Extreme Schärfung | ❌ Meist zu viel, Artefakte |

### Visuelle Effekte

sharpen = 0.5:   T e x t   (verschwommen)
sharpen = 1.0:   Text      (original)
sharpen = 1.5:   Text      (klarer, schärfer)
sharpen = 2.0:   Text      (sehr scharf)
sharpen = 3.0:   Text      (zu scharf, Halos/Kanten-Artefakte)

contrast = 0.0 bis unbegrenzt (float)


### Praktische Bereiche

| Wert | Effekt | Verwendung |
|------|--------|------------|
| **0.0** | Komplett grau (kein Kontrast) | Nicht sinnvoll |
| **0.5** | Reduzierter Kontrast | Weichere Bilder |
| **1.0** | Original (keine Änderung) | Baseline |
| **1.2-1.5** | Leicht erhöhter Kontrast | ✅ Empfohlen für normale Dokumente |
| **1.5-2.0** | Mittlerer Kontrast | ✅ Gut für Text, klare Trennung |
| **2.0-2.5** | Starker Kontrast | Für verblasste Dokumente |
| **2.5-3.0** | Sehr starker Kontrast | ⚠️ Kann Details verlieren |
| **>3.0** | Extremer Kontrast | ❌ Nur schwarz/weiß, Details gehen verloren |

### Visuelle Effekte

contrast = 0.5:  Text  (verwaschen, grau)
contrast = 1.0:  Text  (original)
contrast = 1.5:  Text  (klarer, definierter)
contrast = 2.0:  Text  (sehr klar, starke Trennung)
contrast = 3.0:  Text  (extrem, fast binär)

### Empfohlene Kombinationen für verschiedene Dokumententypen

#### Normale, saubere Dokumente

sharpen = 1.3
contrast = 1.3

-> Leichte Verbesserung, kein Risiko

#### Standard-Scans

sharpen = 1.5
contrast = 1.5

-> Beste Balance

#### Unscharfe oder verblasste Scans

sharpen = 2.0
contrast = 2.0

-> Starke Verbesserung, geringes Artefakt-Risiko

#### Sehr schlechte Scans

sharpen = 2.5
contrast = 2.5

Maximum empfohlen, danach wird's problematisch

#### Extreme Rettung (nur wenn nötig)

sharpen = 3.0
contrast = 3.0

❌ Artefakte wahrscheinlich, nur als letzter Ausweg

### Was passiert bei extremen Werten?

#### Zu viel Sharpening (>3.0)

**Probleme:**
- **Halos** um Buchstaben (weiße/schwarze Ränder)
- **Rauschen-Verstärkung** (körniges Aussehen)
- **Artefakte** an Kanten
- **Überschärfung** (unnatürlich)

**Beispiel:**

Normal:     Text
sharpen=5:  T͟e͟x͟t͟  (mit "Glühen" um Buchstaben)

TODO: Screenshot

### Zu viel Contrast (>3.0)

**Probleme:**
- **Detail-Verlust** (alles wird schwarz oder weiß)
- **Keine Graustufen** mehr (vor Threshold)
- **Harte Kanten** ohne Übergänge
- **Informationsverlust**

**Beispiel:**

Normal:       Graue Schattierung um Text
contrast=5:   Nur noch Schwarz/Weiß, keine Schattierung

TODO: Screenshot

###  Interaktion mit Threshold
Wichtig: Contrast wirkt sich auf den Threshold aus!

Beispiele:

Szenario 1: Niedriger Contrast

contrast = 1.0
threshold = 150

→ Pixel bei 140 bleiben grau → werden schwarz
→ Pixel bei 140 bleiben grau → werden schwarz


Szenario 2: Hoher Contrast

contrast = 2.0
threshold = 150

→ Pixel bei 140 werden zu ~100 → bleiben schwarz
→ Pixel bei 160 werden zu ~200 → werden weiß

Fazit: Höherer Contrast macht den Threshold effektiv "aggressiver"

Szenario 2: Hoher Contrast
contrast = 2.0
threshold = 150
→ Pixel bei 140 werden zu ~100 → bleiben schwarz
→ Pixel bei 160 werden zu ~200 → werden weiß
Fazit: Höherer Contrast macht den Threshold effektiv "aggressiver"

### Summary of Recommended Ranges

|Parameter|Minimum|Recommendation|Maximum(safe)|Maximum(risky)|
|---------|-------|--------------|--------------|--------------|
|Sharpen  |0.0 (blur)    |1.3-2.0          |2.5           |3.0+          |
|Contrast |0.0 (gray)    |1.3-2.0           |2.5           |3.0+          |
