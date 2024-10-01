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
                removeBackSection();
                //on désactive les autres boutons
                for (let h=0; h<totalDropList; h++)
                {
                    navList = dropList[h].querySelectorAll("li")
                    totalNavList = navList.length

                    for(let j=0; j<totalNavList; j++)
                        {
                            if(navList[j].querySelector("a").classList.contains("active"))
                            {
                                // addBackSection(j);
                                // allSection[j].classList.add("back-section");
                            }
                            navList[j].querySelector("a").classList.remove("active");
                            
                            dropList[h].querySelector("span").classList.remove("active");
                            
                        }
                }
                
                
                
                // on active ce bouton de column
                dropList[k].querySelector("span").classList.add("active");
                // on active ce bouton de section
                this.classList.add("active")
                showSection(this);
                if(window.innerWidth < 1200)
                {
                    asideSectionTogglerBtn();
                }

                // mettre à jour le title pour le nom de l'onglet
                document.title = this.textContent
            })

        }
      }
      
      function removeBackSection()
      {

        for(let i=0; i<totalSection; i++)
        {
            allSection[i].classList.remove("back-section");
            
        }   
      }
      function addBackSection(num)
      {
        allSection[num].classList.add("back-section");
        
      }
      function showSection(element)
      {
          for(let i=0; i<totalSection; i++)
          {
              allSection[i].classList.remove("active");
              allSection[i].classList.add("hidden");

          }
          const target = element.getAttribute("href").split("#")[1];
          document.querySelector("#" + target).classList.add("active")
          document.querySelector("#" + target).classList.remove("hidden")
      }
      function updateNav(element)
      {
          for(let i=0; i<totalNavList; i++)
          {
              navList[i].querySelector("a").classList.remove("active");
              const target = element.getAttribute("href").split("#")[1];
              if(target === navList[i].querySelector("a").getAttribute("href").split("#")[1])
              {
                navList[i].querySelector("a").classList.add("active");
              }
          }
      }
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