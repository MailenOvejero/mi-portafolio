document.addEventListener("DOMContentLoaded", () => {
  // Efecto de escritura en subtítulo
  const texto = "Developer Full Stack ";
  const typedText = document.getElementById("typed-text");

  
  if (typedText) {
    let i = 0;

    function escribir() {
      if (i < texto.length) {
        typedText.textContent += texto.charAt(i);
        i++;
        setTimeout(escribir, 100);
      }
    }

    escribir();
  }
});



function setProgress(circle, percent) {
    const radius = circle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    circle.style.strokeDasharray = circumference;
    circle.style.strokeDashoffset = circumference - (percent / 100) * circumference;
}

const porcentajes = [58, 68, 85, 80, 95, 65, 100, 100, 65, 100];
const circles = document.querySelectorAll(".circle-progress");


const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            const index = Array.from(circles).indexOf(entry.target);
            setProgress(entry.target, porcentajes[index]);
            observer.unobserve(entry.target); // evita que se repitaA
        }
    });
}, { threshold: 0.5 }); 


circles.forEach(circle => {
    observer.observe(circle);
});



// animo las seciones cuando hgo scrll
const sections = document.querySelectorAll("section.contenido");

const sectionObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("active");
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.2 });


sections.forEach(sec => {
    sec.classList.add("reveal");
    sectionObserver.observe(sec);
});



function openModal(img) {
  const modal = document.getElementById("modal");
  const modalImg = document.getElementById("modal-img");
  const caption = document.getElementById("modal-caption");

  if (modal && modalImg && caption) { // <-- prote si no xiste
    modal.style.display = "block";
    modalImg.src = img.src;
    caption.innerHTML = img.alt;
  }
}

function closeModal() {
  const modal = document.getElementById("modal");
  if (modal) modal.style.display = "none"; 
}
