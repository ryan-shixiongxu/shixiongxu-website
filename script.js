const tabs = [...document.querySelectorAll('nav a')];
function route() {
  const hash = location.hash.replace('#', '');
  const page = ['home', 'cv', 'research'].includes(hash) ? hash : 'home';
  document.querySelectorAll('.page').forEach(el => { el.hidden = el.id !== page; });
  tabs.forEach(link => {
    const active = link.dataset.page === page;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  document.title = `${page === 'home' ? 'Home' : page === 'cv' ? 'CV' : 'Research'} | Shixiong Xu`;
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', route);
route();
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
