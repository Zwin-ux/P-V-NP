import { CheckVsFind } from './components/CheckVsFind';
import { SearchSpace } from './components/SearchSpace';
import { Reductions } from './components/Reductions';

function App() {
  return (
    <>
      <div className="grain"></div>
      <header className="nav">
        <div className="nav-inner">
          <div className="brand">
            <div>
              <div className="brand-title">Theorem Proving Practice</div>
              <div className="brand-sub">Interactive Learning System</div>
            </div>
          </div>
          <div className="nav-actions">
            <a href="https://www.bonelli.dev/" target="_blank" rel="noopener noreferrer" className="chip ghost">Made by Bonelli.dev</a>
          </div>
        </div>
      </header>

      <main>
        <section id="entry" className="section hero">
          <div className="hero-bg"></div>
          <div className="section-inner hero-grid">
            <div>
              <p className="eyebrow reveal">Interactive Learning</p>
              <h1 className="hero-title reveal"><span className="title-sweep">Is checking as easy as finding?</span></h1>
              <p className="hero-copy reveal">Move from verification to search, ride the reductions conveyor, and try compact interactives.</p>
              <div className="hero-actions reveal">
                <a href="#verify-search" className="btn primary">Start Practice</a>
                <a href="#orientation" className="btn ghost">Orientation strip</a>
              </div>
            </div>
            <div className="hero-ribbon">
              <span className="hero-chip reveal">Verification</span>
              <span className="hero-chip reveal">Search</span>
              <span className="hero-chip reveal">Reductions</span>
              <span className="hero-chip reveal">Scaling</span>
            </div>
          </div>
        </section>

        <CheckVsFind />
        <SearchSpace />
        <Reductions />

      </main>

      <footer className="footer">
        <div className="footer-inner">
          <div>Motion honors reduced-motion preferences.</div>
          <div className="muted">Crafted by <a href="https://www.bonelli.dev/" className="brand-link" target="_blank" rel="noopener noreferrer">Bonelli.dev</a>.</div>
        </div>
      </footer>
    </>
  );
}

export default App;
