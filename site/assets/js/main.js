// Mobile nav
const toggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.nav-links');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });
}

// Header shadow on scroll
const header = document.querySelector('.site-header');
if (header) {
  window.addEventListener('scroll', () => {
    header.style.boxShadow = window.scrollY > 8 ? '0 4px 24px rgba(0,0,0,0.4)' : 'none';
  }, { passive: true });
}

// Fade-in cards on scroll
if ('IntersectionObserver' in window) {
  const cards = document.querySelectorAll('.card');
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });
  cards.forEach((c, i) => {
    c.style.opacity = '0';
    c.style.transform = 'translateY(20px)';
    c.style.transition = `opacity 0.45s ease ${(i % 3) * 0.08}s, transform 0.45s ease ${(i % 3) * 0.08}s`;
    obs.observe(c);
  });
}
