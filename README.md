# EDIFICAExpanded

Modifica del programma originale "Edifica" (https://github.com/JoddyJordan/EDIFICA-Code)

Cambiamenti apportati:

- Fix compatibilità con Windows

- Aggiunta del modulo BaseGoalExpander per espandere il goal iniziale con i sinonimi, iponimi e iperonimi dei termini

- Implementazione del BaseGoalExpander nel BaseGoalBuilder

## Istruzioni per l'uso:

### EdificaMain:

- Impostare il goal nel file apposito "goal"

- Runnare EdificaMain


### GuiApp:

Se si vuole runnare Edifica con interfaccia grafica, si consiglia di farlo su Linux, dato che alcune finestre non verranno mostrate correttamente

- Runnare GuiApp
- Selezionare "Welcome"
- Selezionare "Ontology" e caricare "knowledge_base"
- Una volta visualizzato il grafo (possibile solo su Linux) chiudere la finestra e caricare "tipicality_base"
- Una volta caricate le tipicalità cambiare finestra in goals e caricare il file "goal"
- Per finire, una volta visualizzato il grafo del goal (possibile solo su Linux), passare alla finestra "Reasoning" dove verrà mostrato il risultato. 


