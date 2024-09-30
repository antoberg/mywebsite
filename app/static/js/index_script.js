document.addEventListener('DOMContentLoaded', function() {
    // Sélectionne tous les liens du menu
    const menuLinks = document.querySelectorAll('.navbar a, .navbar .dropdown-content a');

    // Sélectionne toutes les sections
    const sections = document.querySelectorAll('.main-content section');

    
    // Ajoute un événement 'click' à chaque lien du menu
    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // on vérifie qu'il y a un # cad qu'on sélectionne une section
            if (this.getAttribute('href').startsWith('#')){
                e.preventDefault(); // Empêche le comportement par défaut du lien
            
                // Récupère l'ID de la section cible
                const targetId = this.getAttribute('href').substring(1); // Supprime le '#' du href
                
                // Désactive toutes les sections
                sections.forEach(section => {
                    section.classList.remove('active');
                });
    
                // Active la section cible
                const targetSection = document.getElementById(targetId);
                targetSection.classList.add('active');
            }
           
        });
    });
});
