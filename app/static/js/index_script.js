// ===================== NAVIGATION ENTRE LES SECTIONS =========================

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
            a.addEventListener("click", function()
            {
                
                showSection(this);
                if(window.innerWidth < 1200)
                {
                    asideSectionTogglerBtn();
                }
                
            })
        }
    }
    // Update la section visible 
    function showSection(element)
    {
        for(let i=0; i<totalSection; i++)// PARCOURS DES .DROPDOWNS
        {
            //=============UPDATE DE LA BARRE DE NAV================
            dropCol = dropList[i].querySelector("span")
            //on désactive les elemnts span : têtes de colonnes
            dropCol.classList.remove("active");
            
            navList = dropList[i].querySelectorAll("li")
            totalNavList = navList.length
            for(let j=0; j<totalNavList; j++) // PARCOURS DES ITEMS DU DROPDOWN (li)
            {
                navElem = navList[j].querySelector("a") //le <a> de chaque <li> de la droplist
                navElem.classList.remove("active");
                if(navElem.getAttribute('href').split("#")[1] == element.getAttribute("href").split("#")[1])
                {
                    dropCol.classList.add("active");
                    navElem.classList.add("active");
                    
                    // mettre à jour le title pour le nom de l'onglet
                    document.title = navElem.textContent
                }
            }

            //=============UPDATE DES SECTIONS (utilise les class .active de la barre de nav)================
            allSection[i].classList.remove("active");
            allSection[i].classList.add("hidden");
        }
        // active les sections qui ont comme class le href du element = le href du a de la navbar
        const target = element.getAttribute("href").split("#")[1];
        document.querySelector("#" + target).classList.add("active")
        document.querySelector("#" + target).classList.remove("hidden")
    }
   
    
    // Utilisation Navbar
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
// ===================== ACTIVER / MASQUER LES SECTIONS DEPUIS UN BOUTON =========================
    
    document.querySelector(".get-map").addEventListener("click", function()
        {
            showSection(this);
        })


// ===================== FICHIERS GPX LOCAUX ET STRAVA: MESSAGE DE STATUS & STOCKAGE FILENAME DANS FORM =========================

// Variable pour stocker le nom du fichier sélectionné
let selectedFilename = '';

// Listener sur parent pour avoir accès à tous les fichiers
const filelistContainers = document.querySelectorAll('.files-list')

filelistContainers.forEach(file =>{
    file.addEventListener('click', function(event){
    event.preventDefault();
        console.log("list found")
        if (event.target.classList.contains('file-link')) {
            // Empêche le lien d'ouvrir une nouvelle page
            selectedFilename = event.target.getAttribute('data-filename');  // Stocke le nom du fichier
            selectedId = event.target.id;  // Stocke l'ID du fichier (pour les routes strava)

            document.getElementById('filestatus').textContent = selectedFilename + " selected";  // Affiche le nom du fichier sélectionné
            document.getElementById('filestatuspic').src = checkIconUrl;

            document.getElementById('selectedFilename').value = selectedFilename;
            if (file.id  == "strava-files-list" ){
                document.getElementById('fileSource').value = "strava";
                document.getElementById('fileId').value = selectedId;
            }else{
                document.getElementById('fileSource').value = "server";
            }
        }
    });
});

// ===================== IMPORT FICHIERS GPX UTILISATEUR : MESSAGE DE STATUS =========================
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
        document.getElementById('filestatuspic').src = "{{ url_for('static', filename='images/check.png') }}";
    } else {
        document.getElementById('filestatus').textContent = "Aucun fichier sélectionné";
        document.getElementById('filestatuspic').src = "";  // Réinitialiser l'image si aucun fichier
    }
});

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


