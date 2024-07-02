# progetto
 Progetto Basi di Dati
  Progettare e implementare una piattaforma di social networking con funzionalitá pubblicitarie integrate,
 consentendo alle aziende di promuovere i propri prodotti e servizi a un pubblico mirato. La piattaforma
 dovrebbe soddisfare sia gli utenti regolari che gli inserzionisti, con il sistema che tiene traccia degli annunci
 sui quali ogni utente clicca. Ecco le principali caratteristiche:
 • Gestione utenti: Implementare funzionalitá di autenticazione e autorizzazione degli utenti regolari
 e degli inserzionisti. Gli utenti dovrebbero poter registrarsi, accedere e gestire i propri profili. Gli
 inserzionisti dovrebbero avere funzionalitá aggiuntive per gestire le proprie campagne pubblicitarie.
 • Gestione delle amicizie: Consentire agli utenti di connettersi tra loro, inviare richieste di amicizia e
 gestire la propria lista di amici. Gli utenti regolari dovrebbero poter interagire con i post (compresi i
 commenti) e i contenuti dei propri amici all’interno della piattaforma.
 • Condivisione dei Contenuti: Consentire agli utenti di creare e condividere (ad amici o al pubblico) vari
 tipi di contenuti come testo, foto e video. Gli utenti dovrebbero poter mettere ”mi piace” e commentare
 i contenuti postati dai propri amici e da altri utenti nella rete.
 • Gestione degli annunci: Fornire agli inserzionisti la possibilitá di creare e gestire campagne pubblicitarie
 all’interno della piattaforma. Gli inserzionisti dovrebbero poter definire criteri di targeting (in base
 alle caratteristiche dell’utente), durata e monitorare le performance dei loro annunci.
 • Gestiona avanzata annunci (Opzionale per gruppi inferiori a tre): implementare la possibilitá di im
postare un budget per una particolare campagna (ogni click ricevuto costa). Impostare anche una
 prioritá agli annunci, annunci con prioritá piú elevata avranno piú probabilitá di venire visualizzati.
 OPzionalmente, implementare un semplice sistema di raccomandazione delle inserzioni (i.e. per definire
 quale inserzione mostrare in base al comportamento dell’utente e alle sue amicizie).
 
 # 3 Requisiti del Progetto
 Il progetto richiede come minimo lo svolgimento dei seguenti punti:
 1. Progettazione concettuale e logica dello schema della base di dati su cui si appogger`a all’applicazione,
 opportunamente commentata e documentata secondo la notazione introdotta nel Modulo 1 del corso.
 2. Creazione di un database, anche artificiale, tramite l’utilizzo di uno specifico DBMS. La creazione delle
 tabelle e l’inserimento dei dati pu`o essere effettuato anche con uno script esterno al progetto.
 3. Implementazione di un front-end minimale basato su HTML e CSS. E’ possibile utilizzare framework
 CSS esistenti come W3.CSS, Bootstrap o altri. E’ inoltre possibile fare uso di JavaScript per migliorare
 l’esperienza utente, ma non é richiesto e non influirá sulla valutazione finale.
 4. Implementazione di un back-end basato su Flask e SQLAlchemy (o Flask-SQLAlchemy).
 Per migliorare il progetto e la relativa valutazione ` e raccomandato gestire anche i seguenti aspetti:
 1. Integritá dei dati: definizione di vincoli, trigger, transazioni per garantire l’integrit`a dei dati gestiti
 dall’applicazione.
 2. Sicurezza: definizione di opportuni ruoli e politiche di autorizzazione, oltre che di ulteriori meccanismi
 atti a migliorare il livello di sicurezza dell’applicazione (es. difese contro XSS e SQL injection).
 3. Performance: definizione di indici o viste materializzate sulla base delle query pi` u frequenti previste.
 4. Astrazione dal DBMS sottostante: uso di Expression Language o ORM per astrarre dal dialetto SQL.
 E’ possibile focalizzarsi solo su un sottoinsieme di questi aspetti, ma i progetti eccellenti cercheranno di
 coprirli tutti ad un qualche livello di dettaglio. E’ meglio approfondire adeguatamente solo alcuni di questi
 aspetti piuttosto che coprirli tutti in modo insoddisfacente.

 # 4 Documentazione
 Il progetto deve essere corredato da una relazione in formato PDF opportunamente strutturata, che discuta
 nel dettaglio le principali scelte progettuali ed implementative. La documentazione deve anche chiarire (in
 appendice) il contributo al progetto di ciascun componente del gruppo. Viene raccomandata la seguente
 struttura per la relazione:
 1. Introduzione: descrizione ad alto livello dell’applicazione e struttura del documento.
 2. Funzionalitá principali: una descrizione delle principali funzionalitá fornite dall’applicazione, che aiuti
 a comprendere come avete declinato lo spunto di partenza relativo al tema scelto per il progetto.
 3. Progettazione concettuale e logica della basi di dati, opportunamente spiegate e motivate. La presen
tazione deve seguire la notazione grafica introdotta nel Modulo 1 del corso.
 4. Query principali: una descrizione di una selezione delle query pi`u interessanti che sono state imple
mentate all’interno dell’applicazione, utilizzando una sintassi SQL opportuna.
 5. Principali scelte progettuali: politiche di integrit`a e come sono state garantite in pratica (es. trigger),
 definizione di ruoli e politiche di autorizzazione, uso di indici, ecc. Tutte le principali scelte progettuali
 devono essere opportunamente commentate e motivate.
 6. Ulteriori informazioni: scelte tecnologiche specifiche (es. librerie usate) e qualsiasi altra informazione
 sia necessaria per apprezzare il progetto.
 7. Contributo al progetto (appendice): una spiegazione di come i diversi membri del gruppo hanno
 contribuito al design ed allo sviluppo.
 Il codice del progetto deve essere inoltre opportunamente strutturato e commentato per favorirne la manuten
zione e la leggibilitá
