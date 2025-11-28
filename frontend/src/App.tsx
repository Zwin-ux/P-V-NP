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
              <div className="brand-title">P vs NP Exploration Hall</div>
              <div className="brand-sub">Interactive Learning System</div>
            </div>
          </div>
          <div className="nav-actions">
            <button id="handout-toggle" className="chip ghost">Print handout</button>
          </div>
        </div>
      </header>

      <main>
        <section id="entry" className="section hero">
          <div className="hero-bg"></div>
          <div className="section-inner hero-grid">
            <div>
              <p className="eyebrow reveal">Museum Exhibit</p>
              <h1 className="hero-title reveal"><span className="title-sweep">Is checking as easy as finding?</span></h1>
              <p className="hero-copy reveal">Move from verification to search, ride the reductions conveyor, and try compact interactives built to feel like a floor exhibit.</p>
              <div className="hero-actions reveal">
                <a href="#verify-search" className="btn primary">Enter the hall</a>
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
          <div>Built for this exhibit. Motion honors reduced-motion preferences.</div>
          <div className="muted">No backends or fetch calls. Presets are baked in.</div>
        </div>
      </footer>
    </>
  );
}

export default App;
