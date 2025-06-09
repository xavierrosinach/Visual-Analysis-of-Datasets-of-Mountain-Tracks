# Agraïments

# Resum

# 1. Introducció

## 1.1. Motivació

Al llarg dels anys, el senderisme ha anat guanyant popularitat a Catalunya gràcies als meravellosos paisatges del país. Aquest creixement ha anat de la mà del creixement d’aplicacions que permeten a la gent registrar i compartir les seves rutes, fent que els usuaris puguin trobar i seguir camins fàcilment. Avui en dia, comunitats de caminadors i altres esportistes, utilitzen aquestes aplicacions per tal de poder realitzar excursions d’una forma més segura i eficient.

Tot i això, aplicacions així únicament mostren informació sobre una ruta en concret. És a dir, un usuari registra una ruta, la penja amb altra informació com ara el títol o dificultat percebuda, i els altres usuaris poden utilitzar-la i veure com ha estat registrada anteriorment. Un inconvenient que es pot observar és que no tenim informació sobre tots els camins de la zona: quins han estat més transitats, quins s’acostumen a fer més de pujada o baixada, quins són inaccessibles, entre altres. 

Així doncs, neix la motivació de fer un estudi dels camins de tres zones populars del senderisme a Catalunya: el Matagalls, el Canigó, i la Vall Ferrera. Es vol, mitjançant una aplicació web interactiva, que l’usuari pugui respondre a preguntes que es pugui fer sobre els camins d’aquestes zones. 

## 1.2. Objectius

L’objectiu del projecte és utilitzar un gran conjunt de rutes registrades de senderisme per a desenvolupar una aplicació web interactiva que permetrà als usuaris informar-se sobre els camins de tres zones muntanyoses de Catalunya. Igualment, també es voldrà que l’usuari pugui consultar les rutes individualment, i poder-les comparar amb d’altres de semblants. 

L’usuari, gràcies a aquesta aplicació, podrà dissenyar rutes personals segons la popularitat dels camins, estacionalitat, o condicions meteorològiques. Anteriorment, únicament podia seguir el camí definit per un usuari únicament.

## 1.3. Requeriments

Per tal d’assolir els objectius definits, el producte final haurà de complir uns certs requisits, tant tècnics, com funcionals, per tal d’ajudar a l’usuari tal com s’havia ideat en un principi.

Pel que fa els requeriments funcionals, es vol que l’usuari pugui explorar les rutes de cada zona de senderisme definida, i que tingui unes visualitzacions el suficientment clares i concises per tal de resoldre-li petits dubtes, o qüestions d’alta complexitat. També es vol que l’usuari pugui navegar fàcilment per l’eina dissenyada, sense errors.

Per una altra part, en el marc tècnic, es requereix utilitzar eines adequades per tal que l’anàlisi i visualització de les dades sigui correcte. Igualment, es vol assegurar que la pipeline de processat de dades, i creació de visualitzacions pugui aguantar grans volums de dades, i es pugui adaptar correctament a qualsevol entrada de dades d’una nova zona de senderisme. 

# 2. Dades

## 2.1. Font de dades

La font de les dades utilitzada per al projecte correspon a l’aplicació Wikiloc. Una interfase web on els seus usuaris poden emmagatzemar i compartir rutes a l’aire lliures gravades utilitzant GPS. A part de la informació geogràfica, els usuaris també tenen la possibilitat d’afegir altra informació, com ara la dificultat percebuda de la ruta, o punts d’interès.

Wikiloc es va crear l’any 2006, i actualment consta d’uns 15 milions d’usuaris amb unes 54 milions de rutes registrades. L’aplicació consta d’un cercador on l’usuari pot filtrar entre diverses característiques de la ruta; i en retorna aquellles més populars entre el filtratge definit. L’usuari pot guardar-se la ruta, i a posteriori utilitzar-la en dispositius GPS per al seguiment d’aquesta. 

## 2.2. Col·lecció de dades

A partir de la pàgina web de Wikiloc, l’equip de professorat del projecte han creat un codi per a l’extracció de rutes d’una zona determinada. Aquest codi filtra tot el conjunt de dades de Wikiloc per tal de trobar-ne totes aquelles rutes que s’han anat realitzant en una zona determinada.

Es treballa per tres zones: el Canigó, el Matagalls, i la Vall Ferrera. Corresponen a tres punts molt concorreguts per excursionistes a Catalunya al llarg dels anys. Per a cadascuna d’aquestes zones, el professorat ha entregat un fitxer comprimit a l’alumne que contenia totes les rutes extretes de Wikiloc en format JSON.

Cada fitxer JSON conté informació rellevant de la ruta: l’identificador, l’usuari, dificultat percebuda, data…, i també conté les coordenades que el GPS ha anat adquirint, igual que els punts d’interés que l’usuari hagi pogut registrar. 

## 2.3. Processat de dades

Donats els tres fitxers comprimits - un per cada zona - que contenen tots els fitxers JSON, l’alumne ha creat una pipeline per tal de preparar les dades per a la seva visualització. Així doncs, s’ha preparat un codi que, per a cada zona, un cop executat, s’obtenen totes les taules de dades necessàries per a poder crear les visualitzacions a posteriori. 

El processat de les dades consta de tres parts - tenint en compte que cadascuna l’apliquem per a cada zona. La primera part es basa en una preparació de l’entorn de carpetes i altres fitxers que a posteriori s’utilitzaran per al processat. Es fa la lectura del fitxer comprimit, i se n’extreuen tots els fitxers en format JSON a una carpeta, que considerarem la carpeta d’entrada del codi. Apart, també es genera la xarxa de camins registrats a Open Street Map de la zona definida - a posteriori s’explica per a que es necessita. L’alumne, gràcies a aquesta primera part, pot obtenir una estructura clara i concisa per a començar a processar rutes a continuació. 

La carpeta de dades conté tant les dades d’entrada, com totes les dades de sortida. Per tal de garantir-ne la seva seguretat, aquestes es troben el local al dispositiu de l’alumne. L’estructura d’aquesta carpeta queda definida per una carpeta inicial per a cadascuna de les zones, i una carpeta on es troben els tres fitxers comprimits inicials. La següent imatge mostra un esquema de l’estructura de la carpeta de dades: 

Degut a que volem fer un estudi d’aquelles rutes més concorregudes, necessitem saber per quins camins ha passat cada usuari a l’hora d’enregistrar amb el seu GPS. La segona part del processat s’assegura de realitzar aquesta conversió. Utilitzem la llibreria anomenada Fast Map Matching; aquesta, gràcies a la xarxa de camins trobada anteriorment, donada una llista amb els punts de coordenades ordenades per on ha passat la ruta, la normalitza buscant els possibles camins per on ha passat. Per a cada ruta, ara, sabem per a quins camins exactes ha passat l’usuari - abans únicament teníem punts de GPS que no corresponien a cap camí en concret, i no podíem agrupar grups de rutes per camins on havien coincidit. En aquest apartat s’ha aplicat un filtrat de rutes per tal d’evitar aquelles que contenen errors. 

El tercer i últim pas per al processat de les dades, es basa en un codi que, donades aquelles rutes normalitzades anteriorment, en dissenya diversos fitxers de sortida que utilitzarem per tal de dissenyar les visualitzacions. En aquesta part, també s’han descartat algunes dades d’entrada per tal de garantir un conjunt de dades més normalitzat. Al següent apartat parlarem sobre les dades que el processat ha obtingut com a sortida, i de la seva utilització.

## 2.4. Dades utilitzades

Les dades que s’han utilitzat per tal de dissenyar les visualitzacions les podem dividir en tres apartats. Per una part trobem una taula amb la informació general per a totes les rutes de la zona; per una altra part, trobem una taula per a cada ruta de la zona, amb informació sobre els punts de coordenades; i finalment, trobarem diverses taules amb informació sobre els camins de cada zona.

La primera taula correspon a un conjunt de dades general per a la zona sencera. En aquesta, cada ruta registrada conté una fila amb la seva informació: identificador, títol, identificador d'usuari, dificultat percebuda, entre altres. També hi afegim mètriques de la ruta, com ara la distància, el ritme mitjà, o el temps total. La data de registre també es troba, juntament amb altra informació temporal com ara el mes, l’any, dia de la setmana, o estació meteorològica. També s’ha afegit informació meteorològica, amb temperatures màximes i mínimes del dia, i la condició meteorològica d’aquest. També trobarem informació sobre el punt d’inici i punt de final de la ruta, als quals s’hi ha aplicat un procés d’agrupació per tal de trobar 10 zones d’inici i 10 zones de final de ruta diferenciades. Amb aquesta informació podrem fer un estudi general de la zona amb tendències en diverses àrees, com ara estacionarietat, o popularitat de rutes segons mètriques. 

La següent taula a continuació mostra les columnes que té el conjunt de dades esmentat. Amb una petita explicació de la columna, i un exemple de cadascuna. 

*taula*

El segon tipus de dada utilitzat correspon a una taula per a cada ruta. En aquesta, cada punt de coordenades registrat correspon a una fila de la taula. Inicialment, ja teníem algunes d’aquestes dades - els punts de longitud i latitud, l’elevació i el temps (timestamp) en el qual s’havia registrat cada punt. Ara, el que hem fet, ha set ampliar aquesta taula de forma que podem extreure molta més informació sobre la ruta: com ara la distància entre dos punts, la diferència de temps, la velocitat i ritme, entre altres. Apart, el que també s’ha fet, és, aplicant el procés de map matching, trobar el camí pel qual ha passat la ruta en aquell punt de coordenades. 

La taula a continuació mostra les columnes d’aquests conjunts de dades - un per a cada ruta registrada. Igual que abans, s’explicarà cada columna, i es mostrarà un exemple.

*taula*

Aquesta taula s’ha dividit en tres sub-taules més per a cada ruta. Per una part trobem la divisió per quilòmetres, on es pot veure informació com ara la velocitat mitjana per a cada quilòmetre, el desnivell acumulat, el temps, etc. També trobem una divisió de la ruta per zones on la velocitat ha anat canviant; és a dir, s’ha agrupat aquells trams amb velocitats semblants, i se n’ha buscat la seva velocitat mitjana. També, per a cada eix de la xarxa de camins, s’ha buscat aquesta informació. D’aquesta forma, es podrà observar informació diferent per a una única ruta. 

La primera taula correspon a una divisió de tots els eixos per on ha passat l’d'usuari. Recordem que quan parlem d’eixos, parlem d’una part del camí registrada a la xarxa de la zona. D’aquesta forma podrem observar relacions entre diversos camins, per comparar velocitats, temps totals, etc.

*taula*

El segon conjunt de dades parcial correspon a la informació sobre cada quilòmetre recorregut en la ruta. D’aquesta forma podrem mostrar informació dividida en trams de quilometratge. Si la ruta és de, per exemple, 10 quilòmetres, aquest conjunt de dades tindrà 10 files. 

*taula*

La tercera, i última divisió de les coordenades de la ruta es basa en una agrupació d’aquelles zones on s’han detectat ritmes semblants. Per a cadascuna d’aquestes zones, trobem informació com ara el ritme mitjà, temps, o distància; entre altres.

*taula*

Finalment, trobem informació sobre els eixos de la xarxa de camins de cada zona. Per a cadascun dels eixos, n’hem buscat les rutes que hi passen, i hi hem anotat la velocitat mitjana per la qual s’hi ha passat. D’aquesta forma, per a cada eix sabrem mètriques com ara la popularitat i el ritme mitjà. Aquest procés s’ha fet més d’un cop, ja que s’han filtrar les rutes, de forma que, segons uns barems, podrem veure la xarxa de camins pintada d’una forma o d’una altra - per exemple, s’han mirat les rutes registrades per un any en concret, i únicament s’han afegit aquestes al comptatge de rutes. 

S’han filtrat les rutes per:

* Any (year)
* Mes (month)
* Estació (season)
* Condició meteorològica (weather_condition)
* Distància (7 grups):
    * Inferior a 5 km
    * De 5 a 10 km
    * De 10 a 15 km
    * De 15 a 20 km
    * De 20 a 25 km
    * De 25 a 30 km
    * Superior a 30 km
* Temps (7 grups):
    * Inferior a 60 minuts
    * De 60 a 120 minuts
    * De 120 a 180 minuts
    * De 180 a 240 minuts
    * De 240 a 300 minuts
    * De 300 a 360 minuts
    * Superior a 360 minuts
* Ritme mitjà (4 grups):
    * Inferior a 20 min/km
    * De 20 a 40 min/km
    * De 40 a 60 min/km
    * Superior a 60 min/km
* Elevació (5 grups)
    * Inferior a 500 metres
    * Entre 500 i 1000 metres
    * Entre 1000 i 1500 metres
    * Entre 1500 i 2000 metres
    * Superior a 2000 metres

Aquests conjunts de dades tenen la següent estructura:

*taula*

Cal recordar que aquestes dades es troben de forma independent per a cada zona definida; amb una estructura de carpetes igual per a cadascuna, amb els mateixos noms de documents, únicament canvia el nom de la zona, i l’identificador de la ruta. Amb totes aquestes dades transformades, ja es podran començar a crear les visualitzacions que puguin respondre totes les preguntes que l’usuari es pugui fer sobre les tres zones d’entrada de dades. 

# 3. Tecnologies

El següent apartat ens serà útil per a comentar les tecnologies que s’han utilitzat per tal de crear el producte final. Cal tenir en compte que s’han dut a terme dos processos principals en el projecte. 

El primer procés es basa en el tractat de dades, on donades les dades d’entrada, s’han transformat amb aquelles que es necessiten per tal de crear les visualitzacions. La segona part del projecte es basa en crear les visualitzacions, i una aplicació interactiva per tal que l’usuari pugui interactuar amb aquestes. 

Tot el codi per al projecte ha estat codificat utilitzant el llenguatge Python. Això és degut al gran rang de llibreries creades que es poden utilitzar en aquest llenguatge per a processar grans volums de dades i visualitzar-les. A continuació s’esmentaran les llibreries que s’han utilitzat majoritàriament, com s’han utilitzat, i perquè. 

## 3.1. Tecnologies per a les dades

Com ja s’ha esmentat, la primera part del projecte s’ha basat en tractar les dades d’entrada per tal d’obtenir les necessàries per començar a generar les visualitzacions del producte final. 

Entres les llibreries utilitzades, es destaca Pandas per a la creació i emmagatzematge de conjunts de dades; i per a la normalització de les rutes a camins de la xarxa d’Open Street Map, s’ha utilitzat una llibreria anomenada Fast Map Matching. 

També s’han utilitzat altres llibreries com ara os, per a navegar entre les carpetes o crear-ne; zipfile, per a descomprimir carpetes; shutil, o numpy, entre altres. Tot i això, no es considera necessari haver-les de comentar degut a la poca influència que tenen en el processat.

### 3.1.1. Pandas

Pandas és una llibreria de Python que s’utilitza per treballar amb conjunts de dades. Conté funcions per a analitzar, netejar, explorar, i manipular dades. La seva popularitat es deu ja que és una eina per al tractat i l’anàlisis de dades molt versàtil i proporciona un rendiment molt eficient. Amb Pandas, es poden tractar grans volums de dades que poden provenir de diversos tipus de fitxers d’entrada; i aquestes, un cop tractades, es poden guardar, també, en un gran rang de tipus de fitxers. 

En el cas del projecte, Pandas s’ha utilitzat bàsicament per a poder estructurar les dades d’entrada (tot i que, al ser fitxers JSON s’han hagut de llegir utilitzant la llibreria json), i poder anar fent tractaments per tal d’obtenir els conjunts de dades finals. 

La llibreria no s’ha utilitzat fins a la segona part del codi (extracció d’informació de cada fitxer d’entrada). En aquesta, a mesura que s’anaven tractant els fitxers d’entrada, es guardava informació sobre aquests a conjunts de dades, o bé de fitxers correctament tractats, o bé de fitxers on hi hagués hagut algun error. Pandas, en aquest cas, ha permès que la informació es pogués anar guardant d’una forma eficient. També s’ha utilitzat per a comprovar una a una les les rutes d’entrada i aplicar-ne uns filtres determinats per a passar a la següent fase de processat.

En la tercera i darrera part del processat, Pandas ha resultat molt útil ja que bàsicament aquesta part s’ha basat en agafar les dades dels fitxers d’entrada els quals s’han pogut transformar anteriorment, i guardar-les en conjunts de dades finals. Apart d’això, ens ha ajudat a calcular altres mètriques per a cada ruta, com ara la diferència de temps entre dos punts, la velocitat i ritme (a partir de la distància i el temps), ja que hem creat columnes a partir d’altres columnes.

Així doncs, Pandas ha esdevingut una llibreria imprescindible en el projecte - com a la majoria de projectes codificats en Python relacionats amb el tractat i anàlisis de dades - per tal de poder transformar totes les dades d’entrada i poder-les obtenir tal i com es desitjaven.

### 3.1.2. Fast Map Matching

Com anteriorment s’ha dit, en la segona part del codi s’ha utilitzat la llibreria anomenada Fast Map Matching per a la normalització de les rutes a camins registrats a Open Street Map. Abreviada com a FMM, és una llibreria de codi obert que integra models de Markov ocults i precomputació. Ajuda a fer coincidir les dades de GPS amb possibles errors amb una xarxa de camins. FMM proporciona algorismes de concordança de mapes que són eficients i escalables a grans volums de dades. 

*Explicar a l’annex com funciona el map matching utilitzant models de Markov.*

La utilització en el projecte de la llibreria s’ha basat en donar-li com a entrada les dades de coordenades de cadascuna de les rutes juntament amb la xarxa de camins extreta d’Open Street Map (utilitzant la llibreria osmnx). La llibreria, amb aquesta entrada, processa les dades i retorna també un conjunt de coordenades transformades (punt que correspon a algun camí registrat), i un identificador de l’eix per on s’ha passat. D’aquestes dades s’ha utilitzat majoritàriament la informació dels eixos per on ha passat cada ruta, ja que d’aquesta forma podem realitzar un estudi dels camins més concorreguts.

Per a dur a terme aquest procés de transformació, la llibreria necessita configurar un model el qual precisa de la xarxa de camins de la zona i de tres paràmetres: el paràmetre k, que correspon al nombre de candidats que, donada una coordenada d’entrada es busquen per a trobar-ne un punt adient; el paràmetre r, que correspon al radi de cerca pel qual s’han buscat aquests punts transformats; i finalment, el paràmetre gps_error, que correspon al error que l’algorisme li permet com a màxim a les dades del GPS. També es pot configurar el model amb altres paràmetres com ara la velocitat màxima, però no ens interessa en el nostre cas. 

A l’hora de crear el model per a cada ruta s’han utilitzat tres valors inicials. Pel que fa el radi i l’error del GPS s’ha utilitzat 0.001 (sistema d’unitats en graus), que corresponen, aproximadament, a 100 metres. Pel que fa el valor de k, aquest s’ha inicialitzat amb 2 per a cada ruta, i s’incrementa fins a 4 en el cas de que no es pugui trobar un camí normalitzat.

Podem concloure, doncs, que amb la llibreria de Fast Map Matching, s’han pogut obtenir tots els camins registrats a la xarxa oberta de mapes pels quals ha passat cada ruta; i amb aquests camins, es podrà crear unes visualitzacions útils per a que l’usuari pugui investigar les rutes més concorregudes de cada zona.

## 3.2. Tecnologies per a l'aplicació web

Un cop les dades ja han estat processades, s’ha començat amb la codificació de les visualitzacions, i de l’aplicació final per tal que l’usuari tingui una interfase on pugui veure totes aquestes visualitzacions. 

Les visualitzacions que s’han creat es poden dividir en dos grups; per una part trobem les visualitzacions no espacials, que mostren informació general sobre cada zona, mostrant tendències temporals, de dificultat percebuda, etc. Aquestes visualitzacions s’han creat utilitzant la llibreria Altair. 

Per una altra part, trobem les visualitzacions espacials, que, utilitzant unes coordenades, pinten sobre un mapa informació. En el nostre cas s’han dibuixat els eixos de cada zona amb la seva informació corresponent, i també la ruta concreta per a cada ruta. S’ha utilitzat la llibreria Folium per a dur a terme aquest procés. 

Finalment, totes aquestes visualitzacions s’han integrat en una única aplicació web la qual s’ha codificat utilitzant Streamlit. A continuació esmentarem com funciona cadascuna de les tres llibreries esmentades.

### 3.2.1. Altair

Altair és una llibreria utilitzada per a crear visualitzacions a Python. És de naturalesa declarativa, i es basa en les gramàtiques de visualització Vega i Vega-Lite. És una opció molt útil degut a que les visualitzacions es poden crear a partir de conjunts de dades creats amb Pandas, i que presenta unes possibilitats remotes per a que el codificador pugui crear interaccions dins d’una única visualització, o entre diferents gràfiques.

Com ja s’ha esmentat, en el projecte Altair s’ha utilitzat per a crear visualitzacions a partir del conjunt de dades que conté informació sobre totes les rutes. Amb la llibreria s’han pogut crear visualitzacions que mostren informació sobre tendències, com per exemple, l’evolució del nombre total de rutes registrades al llarg dels anys, o diagrames de dispersió comparant dues variables quantitatives per a poder veure distribucions en cada zona. 

El següent exemple correspon a un gràfic de barres creat amb Altair que mostra el nombre total de rutes registrades cada any en la zona de El Matagalls. També podem veure-hi al costat el codi que s’ha utilitzat, i es pot apreciar la facilitat en la codificació d’aquest.

*Inserir visualització i codi*

### 3.2.2. Folium

Folium és una llibreria que permet visualitzar dades espacials que han estat manipulades a Python en un mapa interactiu Leaflet (una llibreria de codi obert JavaScript que permet la visualització de mapes interactius). Folium permet afegir punts, línies, i marcadors utilitzant un mapa de fons, el qual es defineix inicialment al crear la variable (definida per un zoom inicial, i unes coordenades centrals). 

En el projecte, Folium s’ha utilitzat per a crear dos tipus de visualitzacions. Per una part, utilitzant els conjunts de dades sobre els eixos, s’ha dibuixat la xarxa de camins amb un color per a cada camí, segons la informació que pretenen mostrar. Per una altra part, també s’han creat visualitzacions per a cada ruta de cada zona, amb informació com ara els marcadors, o els punts d’inici i/o final. 

El següent exemple correspon a la ruta *rutaID* de la zona de El Matagalls. Podem veure la codificació també, i es pot observar com, de manera simple, es pot crear el mapa.

*Inserir visualització i codi*

### 3.2.3. Streamlit

Streamlit és una llibreria de codi obert que permet construir i compartir ràpidament aplicacions web de machine learning i ciència de dades. És una eina fàcil d’aprendre i d’utilitzar, sempre que es vulguin mostrar dades i recollir paràmetres necessaris per al modelat. Streamlit permet crear una aplicació amb un aspecte sorprenent amb poques línies de codi.

La utilització en el projecte d’aquesta llibreria ha estat bàsicament per a la creació de l’aplicació final per a que l’d'usuari pugui navegar entre la informació inicial i les visualitzacions creades i pugui extreure les seves conclusions. Bàsicament s’utilitza Streamlit ja que és una llibreria molt fàcil d’utilitzar, i amb molta documentació per a poder utilitzar, i també permet que incloure visualitzacions creades amb les llibreries esmentades anteriorment. 

# 4. Desenvolupament de l'aplicació

El següent apartat es basa en argumentar sobre el desenvolupament de l’aplicació final per a l'usuari. Anteriorment ja hem explicat l’estructura de dades que s’utilitza, i també les principals llibreries i tecnologies per a crear el codi. Ara toca esmentar el per què i el disseny de cadascuna de les visualitzacions, i les diferents interaccions que es pretenen mostrar a l’aplicació final. 

## 4.1. Preguntes a respondre

Abans de començar a crear les visualitzacions, s’han hagut de definir unes possibles preguntes que l’usuari es pot arribar a fer sobre cada zona. Inicialment se'n ’han definit moltes. Tot i això, s’ha dut a terme un procés de selecció. A continuació mostrarem aquelles que es considerem que poden interessar més a l’usuari:

Sobre la distribució espacial i geogràfica:

1. Quines zones d’inici i final de ruta són més habituals?
2. Quins són els segments de rutes més concorreguts?
3. Segons la dificultat, s’eviten alguns trams?
4. Canvia l’utilització d’alguns camins al llarg del temps?
5. Es poden identificar espais on la gent ha parat molt degut a un punt d'interès?

Sobre característiques i rendiment de les rutes:

1. Podem correlar la dificultat percebuda amb les diferents variables quantitatives (desnivell, distància, temps, ritme…)?
2. Quina és la distància / desnivell / temps més comú per a cada zona?

Sobre aspectes temporals i meteorològics:

1. En quines èpoques de l’any s’han registrat més rutes?
2. Quina ha estat l’evolució de rutes al llarg del temps?
3. Quina relació hi ha entre les condicions meteorològiques i el total de rutes registrades?

Aquestes són les preguntes que, juntament amb d’altres, ajudaran a dissenyar les diferents visualitzacions per a l’usuari final. Cal esmentar que únicament són una forma de guia per a poder crear les visualitzacions, i que en cap moment es preté que l’usuari es tanqui a les respostes a aquestes, i en pugui extreure les seves pròpies conclusions.

## 4.2. Disseny de visualitzacions

### 4.2.1. Visualitzacions espacials

### 4.2.2. Visualitzacions no-espacials

## 4.3. Interaccions amb l'usuari

# 5. Resultat

## 5.1. Anàlisis

# 6. Conclusions

## 6.1. Objectius assolits

## 6.2. Treball futur

# Bibliografia

# Annex
