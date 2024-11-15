document.addEventListener("DOMContentLoaded", () => {  
    const sections = document.querySelectorAll('.section');  
    window.addEventListener('scroll', () => {  
        sections.forEach(section => {  
            const sectionPosition = section.getBoundingClientRect().top;  
            const screenPosition = window.innerHeight / 1.5;  
            if (sectionPosition < screenPosition) {  
                section.classList.add('visible');  
            }  
        });  
    });  
});  