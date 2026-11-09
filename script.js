
const tabs = [...document.querySelectorAll('nav a')];

function route() {
  const hash = window.location.hash.replace('#', '');
  const page = ['home', 'cv', 'research'].includes(hash)
    ? hash
    : 'home';

  document.querySelectorAll('.page').forEach(el => {
    el.hidden = el.id !== page;
  });

  tabs.forEach(a => {
    const active = a.dataset.page === page;
    a.classList.toggle('active', active);

    if (active) {
      a.setAttribute('aria-current', 'page');
    } else {
      a.removeAttribute('aria-current');
    }
  });

  document.title =
    `${page === 'home' ? 'Home' : page === 'cv' ? 'CV' : 'Research'} | Shixiong Xu`;

  window.scrollTo(0, 0);
}

window.addEventListener('hashchange', route);
route();

const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
