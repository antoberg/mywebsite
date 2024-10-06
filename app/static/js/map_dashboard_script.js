

const ctx = document.getElementById('gc').getContext('2d');
        let chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: xData,
                datasets: [{
                    label: 'Altitude',
                    data: yData,
                    pointRadius: 0,
                    backgroundColor: 'rgba(75, 192, 192, 1)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill : true,
                    
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Cacher la légende
                    }
                },
                scales: {
                    x: 
                    { 
                        grid :{ display : false}, 
                        title: { display: true, text: 'Distance (km)' } 
                    },
                    y: 
                    { 
                        grid:{display:false},
                        title: { display: true, text: 'Altitude (m)' } 
                    }
                }
            }
        });



const ctx0 = document.getElementById('wc0').getContext('2d');
let chart0 = new Chart(ctx0, {
    type: 'line',
    data: {
        labels: xwData,
        datasets: [{
            label: 'Précip',
            data: rainData,
            pointRadius: 0,
            backgroundColor: 'rgba(75, 192, 192, 1)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            fill : true,
            
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false // Cacher la légende
            }
        },
        scales: {
            x: 
            { 
                grid :{ display : false}, 
                title: { display: true, text: 'Distance (km)' } 
            },
            y: 
            { 
                beginAtZero: true,
                grid:{display:false},
                title: { display: true, text: 'Précipitations (mm)' } 
            }
        }
    }
});

const ctx1 = document.getElementById('wc1').getContext('2d');
let chart1 = new Chart(ctx1, {
    type: 'line',
    data: {
        labels: xwData,
        datasets: [{
            label: 'Vent',
            data: windData,
            pointRadius: 0,
            backgroundColor: 'rgba(75, 192, 192, 1)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            fill : true,
            
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false // Cacher la légende
            }
        },
        scales: {
            x: 
            { 
                grid :{ display : false}, 
                title: { display: true, text: 'Distance (km)' } 
            },
            y: 
            { 
                beginAtZero: true,
                grid:{display:false},
                title: { display: true, text: 'Vitesse (km/h)' } 
            }
        }
    }
});

const ctx2 = document.getElementById('wc2').getContext('2d');
let chart2 = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: xwData,
        datasets: [{
            label: 'Température',
            data: tempData,
            pointRadius: 0,
            backgroundColor: 'rgba(75, 192, 192, 1)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            fill : true,
            
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false // Cacher la légende
            }
        },
        scales: {
            x: 
            { 
                grid :{ display : false}, 
                title: { display: true, text: 'Distance (km)' } 
            },
            y: 
            { 
                beginAtZero: true,
                grid:{display:false},
                title: { display: true, text: 'Température (°C)' } 
            }
        }
    }
});


        


