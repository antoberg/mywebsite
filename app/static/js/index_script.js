// ===================== afficher le toggler (trouver une alternative ?) =========================

const nav = document.querySelector(".navbar"),
    dropList = nav.querySelectorAll(".dropdown") 
    totalDropList = dropList.length,
    allSection = document.querySelectorAll(".section"),
    totalSection = allSection.length;
    //   on parcours les dropdons (columns)
    for(let k=0; k<totalDropList; k++)
    {
        navList = dropList[k].querySelectorAll("li")
        totalNavList = navList.length
        // on parcours les li dans le dropdown
        for(let i=0; i<totalNavList; i++)
        {
            const a = navList[i].querySelector("a");
            a.addEventListener("click", function(event)
            {
                if(window.innerWidth < 1200)
                {
                    asideSectionTogglerBtn(); //affiche le toggler si la fenetre est petite
                }
                
            })
        }
    }
   
    // SIDE BAR
    const navTogglerBtn = document.querySelector(".nav-toggler"),
        aside = document.querySelector(".navbar");
        navTogglerBtn.addEventListener("click", () => 
        {
            asideSectionTogglerBtn();
        })
        function asideSectionTogglerBtn()
        {
            aside.classList.toggle("open");
            navTogglerBtn.classList.toggle("open");
            for(let i=0; i<totalSection; i++ )
            {
                allSection[i].classList.toggle("open");
            }
        }


// ===================== FICHIERS GPX LOCAUX ET STRAVA: MESSAGE DE STATUS & STOCKAGE FILENAME DANS FORM =========================

// Variable pour stocker le nom du fichier sélectionné
let selectedFilename = '';

// Listener sur parent pour avoir accès à tous les fichiers
const filelistContainers = document.querySelectorAll('.files-list')

filelistContainers.forEach(file =>{
    file.addEventListener('click', function(event){
    
    event.preventDefault();
    
    if (event.target.classList.contains('file-link')) {
        // Empêche le lien d'ouvrir une nouvelle page
        selectedFilename = event.target.textContent;  // Stocke le nom du fichier
          // Stocke l'ID du fichier (pour les routes strava)
        document.getElementById('filestatus').textContent = "Parcours sélectionné : "+selectedFilename.split('.')[0];  // Affiche le nom du fichier sélectionné
        document.getElementById('filestatuspic').src = checkIconUrl;
        document.getElementById('selectedFilename').value = selectedFilename;

        if (file.id  == "strava-files-list" ){
            selectedId = event.target.id;
            document.getElementById('fileSource').value = "strava";
            document.getElementById('fileId').value = selectedId; //-> id route strava pour permettre le téléchargement du bon gpx dans flask
        }else{
            selectedId = event.target.getAttribute('data-filename')
            document.getElementById('fileSource').value = "server";
            document.getElementById('fileId').value = selectedId;
            
        }
        }
    });
});

// ===================== ENTREES USER - MESSAGE DE STATUS =========================
let file = '';

// récupérer nom fichier importé
const importedFile = document.getElementById('gpxFile');

// Update message status
importedFile.addEventListener('change', function() {
    console.log("Change event triggered");
    // Récupérer le fichier sélectionné
    file = this.files[0];

    document.getElementById('fileSource').value = "import";
    
    if (file) {
        fileName = file.name;  // Récupérer le nom du fichier
        document.getElementById('filestatus').textContent = fileName + " sélectionné";
        // Modifier l'image de statut
        document.getElementById('filestatuspic').src = checkIconUrl;
    } else {
        document.getElementById('filestatus').textContent = "Aucun fichier sélectionné";
        document.getElementById('filestatuspic').src = "";  // Réinitialiser l'image si aucun fichier
    }
});

// récupérer paramètres importés
const paramsForm = document.getElementById('paramsForm');

// Update message status
paramsForm.addEventListener('change', function() {

    const currentDate = new Date();
    const timeLim = 7*24*3600*1000; //millisec

    iconUrl = cautionIconUrl

    
    
    // Récupérer le fichier sélectionné
    dateInput = document.getElementById('date').value;
    timeInput = document.getElementById('time').value;
    console.log("date",dateInput,"time",timeInput);

    if ((dateInput == '') || (timeInput == '')) {
        console.log('1 champs remplis');
        if (timeInput == ''){
            params_message = "Heure vide, la météo ne sera pas calculée"
        }else{
            params_message = "Date vide, la météo ne sera pas calculée"
        }
    }else if ((dateInput !== '') && (timeInput !== '')){
        console.log('2 champs remplis');
        const paramsDate = new Date(dateInput+'T'+timeInput+':00');
        if (paramsDate < currentDate) {
            console.log('date dans le passé');
            params_message = "Date passée"
        }else if (paramsDate - currentDate > timeLim ){
            params_message = "Date trop éloignée (limite : 7j)"
            
        }else{
            params_message = ""
            iconUrl = checkIconUrl
        }
    }
    
    document.getElementById('paramStatus').textContent = params_message;
    document.getElementById('paramStatuspic').src = iconUrl;
});

// ===================== CONNECTION A STRAVA ROUTES STRAVA  =========================
// Récupère tous les éléments avec la classe "strava-connect-btn"
var connectButtons = document.getElementsByClassName("strava-connect-btn");

// Boucle à travers chaque élément et ajoute l'event listener
for (var i = 0; i < connectButtons.length; i++) {
    connectButtons[i].addEventListener("click", function(event) {
        // event.preventDefault(); // Empêche le changement de page par défaut
        
    });
}
// ===================== IMPORT ROUTES STRAVA  =========================

// --------------- Affichage de la liste des routes depuis réponse JSON-------------

document.getElementById("load-strava-routes").addEventListener("click", function(event) {
    

    event.preventDefault(); // blocage du chgt de page par défaut quand l'user click sur load
    let loadStr = document.getElementById("loading");
    loadStr.textContent = "loading"

    fetch("/import-strava-routes", {
        method: "POST",
    })
    .then(response => response.json())  // Convertir la réponse en JSON
    .then(data => {
        
        console.log("Données reçues:", data);
        // Cibler l'élément où les fichiers doivent être affichés
        let fileList = document.getElementById("strava-files-list");
        fileList.innerHTML = ""; // Vider la liste actuelle
        loadStr.innerHTML = ""; //vider le texte de chargement
        
        // Pour chaque fichier dans la réponse, créer un élément <li> avec un lien
        data.forEach(file => {
            const name = file[0];  // Le premier élément du tuple est "name"
            const id = file[1];    // Le deuxième élément du tuple est "id"
            let li = document.createElement("li");
            let a = document.createElement("a");
            a.href = "#";
            a.textContent = name; 
            a.className = "file-link";
            a.dataset.filename = name; // Ajout de data-filename
            a.id = id
            console.log(id)
            li.appendChild(a);
            fileList.appendChild(li); // Ajouter le nouvel <li> à la liste
        });
    })
    .catch(error => console.error("Erreur:", error));
});


