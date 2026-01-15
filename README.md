# Verteilte Systeme
Kleine Python Scripts, welche im Rahmen des Moduls "Verteilte Systeme" entstanden sind.

# nist_time.py
  - Umsetzung des RFC 868 Time Protocol
  - Kommunikation über UDP
  - Umrechnung des Zeitstempels in in lesbares Datum

  - ## Nutzung
    ```bash
    python nist_time.py <SERVER>
    python nist_time.py time.nist.gov

# downloader.py 
  - Download von Dateinen über HTTP
  - Blockweiser Download mit frei wählbarer Blöckgröße
  - Unterstützung von "resume" nach Abbruch
  - Nutzung von HTTP Range Request

  - ## Nutzung
     ```bash
    python downloader.py <BLOCKSIZE> <URL>
    python downloader.py 1M http://example.com/file.bin
   

