# IT-Girls - študentski projekt umetna inteligenca v avtonomni vožnji 2022/23
- tema: Adaptivni tempomat in razpoznavanje znakov omejitve hitrosti

Koraki za zagon:

-	Odpremo Anaconda cmd

-	Utipkamo: conda activate myenv

-	Premaknemo se s pomočjo ukaza cd v direktorij v katerem se nahaja naša python skripta za glavno vozlišče

-	Utipkamo v cmd: CarlaUE4 (za zagon Carla simulatorja)

-	Utipkamo: python generate_traffic.py (ali python3 generate_traffic.py) za zagon prometa v izbranoj mapi mesta

-	Utipkamo: python master_car.py (ali python3 master_car.py) za zagon skripte z glavnim vozliščem in detekcijo znakov in objektov

-	S pomočno tipk: ←↑→↓ se peljemo skozi mesto in opazujemo kako algoritem zaznava znake in objekte


Projekt smo začeli z inštalacijo Carla simulatorja in vseh ostalih potrebnih orodij. Uporabili smo že obstoječo skripto generate_traffic.py z minimalnimi spremembami za generiranje prometa na izbrani mapi Carla mesta (Town02) v simulatorju. Potem smo z večjimi spremembami uporabili skripto manual_control.py, in s pomočjo nje naredili našo skripto za ustvarjanje glavnega vozlišča z željenimi senzorji in zagon simulacije master_car.py, tako da ustreza našim potrebam in  zahtevam naše naloge.


V skripti master_car.py smo ustvarili željene senzorje: RGB camera, Depth camera,Lidar in Obstacle detector. Potem smo naredile eno kratko simulacijo z Carla vozilom ki se samo pelje skozi mesto z opcijo ’autopilot’. Uspelo nam je zajeti, obdelati in shraniti podatke iz obeh kamer v .hdf5 datoteko, prav tako kot trenutno hitrost, stanje bremze, gasa in volana. Potem smo iz podatkov ki so bili shranjeni v .hdf5 fajlu naredili .mp4 videoposnetek, na kateri smo dodali izpis stanj telemetrije. Za boljši pregled in analizo, naredili smo tudi funkcijo ki po izvedbi simulacije izriše grafe zajetih telemetrijskih podatkov. Simulacijo za zajem in prikaz podatkov  lahko zaženemo z klicom main.py iz HDF5file direktorija. Skripta masterworld.py se obnaša kot klijent, ki se poveže na Carla simulator in ustvari glavno vozlišče s senzorji, hdf5file.py pa uporabljamo za dejansko shranjevanje in branje podatkov. 
 
  
 ![image](https://user-images.githubusercontent.com/77195829/176135136-2a43d35d-7a28-4e67-a179-16c9943e9f03.png)

 
V tem trenutku imamo še uspešno implementirano realnočasovno zaznavanje in razpoznavanje prometnih znakov omejitve hitrosti s pomočjo YOLOv4 nevronske mreže in objektov kot so avtomobili z YOLOv5 nevronsko mrežo. Edina težava, ki jo pri tem imamo je počasno predvajanje (do 15 fps) kar nam do sedaj ni uspelo popraviti, ampak bomo  v prihodnjem času.
 

 


 
Uspele smo tudi implementirati prilagajanje hitrosti glede na prometne znake omejitve hitrosti, kar bomo tudi demonstrirale z videoposnetkom. 
Implementirali smo tudi Kalmanov filter in PID kontroler na simulaciji kretanja vozila za tarčo ki spreminja svojo hitrost (simulacija ni povezana s Carlo). Naša implementacija precej dobro deluje in vzdržuje razdaljo do tarče z vrednostjo napake manjšo kot ±10% od željene razdalje. Naslednji korak pri tem je integracija z projektom in delovanje na našem glavnem vozlišču, s čemer bomo končali z izdelavo adaptivnega tempomata.
Še en iziv, ki ga bomo imeli pri izdelavi adaptivnega tempomata bo določanje tarče. Med zaznanimi vozili pred nami bodo tudi avta iz nasprotne smeri, katerih hitrost in razdalja ne bi smela vplivati na našo vožnjo in hitrost, tako da bomo morali fiksirati zaznan avto pred nami in konstantno računati razdaljo do njega. 

skupina IT girls
Anja Kuzev,
Ana Tashevska
in Milica Masić
