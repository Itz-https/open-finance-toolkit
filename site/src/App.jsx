import { Component, useState } from 'react';
import Aurora from './reactbits/Aurora.jsx';
import BlurText from './reactbits/BlurText.jsx';
import ShinyText from './reactbits/ShinyText.jsx';
import SpotlightCard from './reactbits/SpotlightCard.jsx';
import CountUp from './reactbits/CountUp.jsx';
import FadeContent from './reactbits/FadeContent.jsx';
import { DEMO_URL, INSTALL_COMMAND, PYPI, REPO } from './config.js';

/* ---------- small helpers ---------- */

// If the browser cannot do WebGL, the page still works without the glow.
class Safe extends Component {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

function CopyButton({ text, label = 'Copy' }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard blocked: the command is still visible to select */
    }
  };
  return (
    <button type="button" className="copy-btn" onClick={copy} aria-label={`${label}: ${text}`}>
      {copied ? 'Copied ✓' : label}
    </button>
  );
}

const Icon = ({ children }) => (
  <svg
    className="icon"
    viewBox="0 0 24 24"
    width="22"
    height="22"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    {children}
  </svg>
);

/* ---------- content ---------- */

const FEATURES = [
  {
    title: 'Reads messy statements',
    text: 'Separate debit and credit columns, one signed amount, odd headers, Indian date formats. You get one clean table every time.',
    icon: <><path d="M6 3h8l4 4v14H6z" /><path d="M14 3v4h4M9 12h6M9 16h6" /></>,
  },
  {
    title: 'Categorises transactions',
    text: 'Simple keyword rules you can read, change and extend. No black box, no account, no training data.',
    icon: <><path d="M3 12l9-9h8v8l-9 9z" /><circle cx="15.5" cy="8.5" r="1.2" /></>,
  },
  {
    title: 'Flags duplicates',
    text: 'Marks likely repeat transactions so you can decide. It never deletes anything behind your back.',
    icon: <><rect x="8" y="8" width="12" height="12" rx="2" /><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" /></>,
  },
  {
    title: 'Income, expenses, savings',
    text: 'Totals and savings rate in a single call, calculated the same way for every bank.',
    icon: <><path d="M4 20V10M10 20V4M16 20v-8M22 20H2" /></>,
  },
  {
    title: 'Monthly and yearly summaries',
    text: 'Group by month or year and get a ready-to-plot table, including the savings rate for each period.',
    icon: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" /></>,
  },
  {
    title: 'HDFC PDF statements',
    badge: 'Experimental',
    text: 'Optional add-on that reads text-based HDFC statement PDFs. Checked against one real statement so far.',
    icon: <><path d="M6 3h8l4 4v14H6z" /><path d="M14 3v4h4" /><path d="M9 15h6M9 18h4" /></>,
  },
];

const STEPS = [
  { n: '1', title: 'Load', code: 'load_transactions("statement.csv")', text: 'Any supported layout. The columns are detected for you.' },
  { n: '2', title: 'Categorise', code: 'categorize(transactions)', text: 'Fills in a category for each row using readable rules.' },
  { n: '3', title: 'Summarise', code: 'summarize(transactions, by="month")', text: 'Income, expenses and savings per month or year.' },
];

const BANKS = [
  { name: 'Standard', detail: 'Date, Type, Category, Amount', status: 'Verified', tone: 'good' },
  { name: 'Generic debit / credit', detail: 'Separate Debit and Credit columns', status: 'Works on test data', tone: 'info' },
  { name: 'Generic signed amount', detail: 'One signed Amount column', status: 'Works on test data', tone: 'info' },
  { name: 'HDFC Bank (PDF)', detail: 'Text-based statement PDFs', status: 'Experimental', tone: 'warn' },
  { name: 'HDFC Bank (CSV)', detail: 'Named layout', status: 'Unverified', tone: 'muted' },
  { name: 'State Bank of India', detail: 'Named layout', status: 'Unverified', tone: 'muted' },
  { name: 'ICICI Bank', detail: 'Named layout', status: 'Unverified', tone: 'muted' },
  { name: 'Axis Bank', detail: 'Named layout', status: 'Unverified', tone: 'muted' },
];

const CONTRIBUTE = [
  {
    title: 'Verify a bank layout',
    text: 'Export one statement, keep only the header row, and tell us the column names. No transactions or personal details needed.',
    cta: 'Request or verify a bank',
    href: `${REPO}/issues/new?template=bank_format_request.yml`,
  },
  {
    title: 'Add a bank or category',
    text: 'Adding a bank is one small entry plus one test. The guide walks you through it step by step.',
    cta: 'Read the guide',
    href: `${REPO}/blob/main/docs/adding-a-bank-format.md`,
  },
  {
    title: 'Report a bug',
    text: 'A statement that does not load, or totals that look wrong? Open an issue and we will look into it.',
    cta: 'Open an issue',
    href: `${REPO}/issues/new/choose`,
  },
];

const SPOT = 'rgba(124, 131, 255, 0.55)';

/* ---------- sections ---------- */

function Nav() {
  return (
    <header className="nav">
      <a className="brand" href="#top" aria-label="Open Finance Toolkit, home">
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#0B0F19" strokeWidth="3" strokeLinecap="round">
            <path d="M5 19v-6M10 19V8M15 19v-4M20 19V4" />
          </svg>
        </span>
        <span>Open Finance Toolkit</span>
      </a>
      <nav className="nav-links" aria-label="Main">
        <a href="#features">Features</a>
        <a href="#how">How it works</a>
        <a href="#banks">Banks</a>
        <a href="#contribute">Contribute</a>
      </nav>
      <a className="btn btn-ghost nav-cta" href={REPO} target="_blank" rel="noreferrer">
        GitHub
      </a>
    </header>
  );
}

function CodeCard() {
  return (
    <div className="code-card" role="img" aria-label="Python example loading a statement and printing totals">
      <div className="code-bar" aria-hidden="true">
        <i /><i /><i />
        <span>quickstart.py</span>
      </div>
      <pre className="code" aria-hidden="true">
        <span className="k">from</span> open_finance_toolkit <span className="k">import</span> (
{'\n'}    load_transactions, categorize, totals
{'\n'})
{'\n\n'}
        <span className="c"># any supported bank layout</span>
{'\n'}tx = <span className="f">load_transactions</span>(<span className="s">"statement.csv"</span>)
{'\n'}tx = <span className="f">categorize</span>(tx)
{'\n\n'}
        <span className="f">print</span>(<span className="f">totals</span>(tx))
      </pre>
      <div className="out" aria-hidden="true">
        <div><span>Income</span><b className="pos">85,312.00</b></div>
        <div><span>Expenses</span><b className="neg">32,567.50</b></div>
        <div><span>Savings</span><b>52,744.50</b></div>
        <div><span>Savings rate</span><b>61.8%</b></div>
      </div>
      <p className="code-note">Example output from the fictional statement included in the repository.</p>
    </div>
  );
}

function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero-bg" aria-hidden="true">
        <Safe>
          <Aurora
            colorStops={['#7C83FF', '#2DD4BF', '#7C83FF']}
            amplitude={0.9}
            blend={0.7}
            speed={0.6}
            height={0.5}
            glow={0.6}
            mouseInteraction={false}
          />
        </Safe>
        <div className="hero-fade" />
      </div>

      <div className="wrap hero-grid">
        <div className="hero-copy">
          <a className="pill" href={`${REPO}/blob/main/CHANGELOG.md`} target="_blank" rel="noreferrer">
            <ShinyText text="New in v0.2: read HDFC statement PDFs" color="#B7BDFF" shineColor="#FFFFFF" speed={3} />
          </a>
          <div role="heading" aria-level={1} className="hero-title">
            <BlurText text="Turn messy bank statements into clean data." delay={90} stepDuration={0.45} trigger="load" />
          </div>
          <p className="lead">
            A free Python library that reads statements from Indian banks, categorises every transaction and
            works out your income, expenses and savings. It runs on your computer, with no accounts and no
            network calls.
          </p>

          <div className="install" role="group" aria-label="Install command">
            <code>
              <span className="prompt" aria-hidden="true">$</span> {INSTALL_COMMAND}
            </code>
            <CopyButton text={INSTALL_COMMAND} label="Copy" />
          </div>

          <div className="cta-row">
            <a className="btn btn-primary" href="#how">See how it works</a>
            <a className="btn btn-ghost" href={REPO} target="_blank" rel="noreferrer">View on GitHub</a>
          </div>
        </div>

        <div className="hero-art">
          <CodeCard />
        </div>
      </div>
    </section>
  );
}

function Stats() {
  return (
    <section className="wrap stats" aria-label="At a glance">
      <FadeContent blur duration={0.8}>
        <ul>
          <li>
            <strong><CountUp to={90} duration={1.6} /></strong>
            <span>automated tests</span>
          </li>
          <li>
            <strong>1</strong>
            <span>required dependency: pandas</span>
          </li>
          <li>
            <strong>0</strong>
            <span>network calls or accounts</span>
          </li>
          <li>
            <strong>MIT</strong>
            <span>licensed, free for any use</span>
          </li>
        </ul>
      </FadeContent>
    </section>
  );
}

function Features() {
  return (
    <section className="wrap section" id="features">
      <FadeContent blur duration={0.8}>
        <p className="eyebrow">What it does</p>
        <h2>Everything between a bank export and a clear answer</h2>
        <p className="section-lead">
          Every bank formats its statements differently. The toolkit turns them all into the same five
          columns, so the code you write on top works for everyone.
        </p>
      </FadeContent>
      <div className="grid features">
        {FEATURES.map((f, i) => (
          <FadeContent key={f.title} duration={0.7} delay={i * 0.06}>
            <SpotlightCard className="card" spotlightColor={SPOT}>
              <div className="card-head">
                <span className="card-icon"><Icon>{f.icon}</Icon></span>
                {f.badge && <span className="tag tag-warn">{f.badge}</span>}
              </div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </SpotlightCard>
          </FadeContent>
        ))}
      </div>
    </section>
  );
}

function How() {
  return (
    <section className="wrap section" id="how">
      <FadeContent blur duration={0.8}>
        <p className="eyebrow">How it works</p>
        <h2>From statement to answer in three steps</h2>
      </FadeContent>
      <ol className="steps">
        {STEPS.map((s, i) => (
          <li key={s.n}>
            <FadeContent duration={0.7} delay={i * 0.1}>
              <div className="step">
                <span className="step-n" aria-hidden="true">{s.n}</span>
                <h3>{s.title}</h3>
                <code>{s.code}</code>
                <p>{s.text}</p>
              </div>
            </FadeContent>
          </li>
        ))}
      </ol>
      <FadeContent duration={0.7}>
        <p className="center-note">
          Prefer the terminal?{' '}
          <code>open-finance-toolkit summary statement.csv --by month</code>
        </p>
      </FadeContent>
    </section>
  );
}

function Banks() {
  return (
    <section className="wrap section" id="banks">
      <FadeContent blur duration={0.8}>
        <p className="eyebrow">Supported formats</p>
        <h2>Honest about what is tested</h2>
        <p className="section-lead">
          Most named bank layouts are built from commonly seen headers and have not been checked against
          real statements yet. Anything they miss usually still loads through the generic layouts.
        </p>
      </FadeContent>
      <FadeContent duration={0.7}>
        <ul className="banks">
          {BANKS.map((b) => (
            <li key={b.name}>
              <div>
                <b>{b.name}</b>
                <span>{b.detail}</span>
              </div>
              <span className={`tag tag-${b.tone}`}>{b.status}</span>
            </li>
          ))}
        </ul>
      </FadeContent>
      <FadeContent duration={0.7}>
        <div className="callout">
          <div>
            <h3>Have a bank statement?</h3>
            <p>
              A single header row is enough to turn an unverified layout into a verified one. It takes about
              five minutes and needs no transactions or personal details.
            </p>
          </div>
          <a className="btn btn-primary" href={`${REPO}/issues/new?template=bank_format_request.yml`} target="_blank" rel="noreferrer">
            Help verify a bank
          </a>
        </div>
      </FadeContent>
    </section>
  );
}

function Demo() {
  return (
    <section className="wrap section" id="demo">
      <FadeContent blur duration={0.8}>
        <p className="eyebrow">Try it</p>
        <h2>A ready-made dashboard</h2>
        <p className="section-lead">
          The repository includes a Streamlit dashboard built on the same ideas: upload a CSV or an HDFC PDF
          and see your income, expenses, savings and spending by category.
        </p>
      </FadeContent>
      <FadeContent duration={0.7}>
        {DEMO_URL ? (
          <div className="cta-row left">
            <a className="btn btn-primary" href={DEMO_URL} target="_blank" rel="noreferrer">Open the live dashboard</a>
            <a className="btn btn-ghost" href={`${REPO}/tree/main/examples/dashboard`} target="_blank" rel="noreferrer">See the code</a>
          </div>
        ) : (
          <div className="run-card">
            <p>Run it yourself:</p>
            <pre>{`git clone ${REPO}.git
cd open-finance-toolkit
pip install -r examples/dashboard/requirements.txt
streamlit run examples/dashboard/app.py`}</pre>
            <CopyButton
              text={`git clone ${REPO}.git\ncd open-finance-toolkit\npip install -r examples/dashboard/requirements.txt\nstreamlit run examples/dashboard/app.py`}
              label="Copy commands"
            />
          </div>
        )}
        <p className="fine">
          Use fictional data when you try a public demo. Anything you upload is processed in your session only.
        </p>
      </FadeContent>
    </section>
  );
}

function Contribute() {
  return (
    <section className="wrap section" id="contribute">
      <FadeContent blur duration={0.8}>
        <p className="eyebrow">Open source</p>
        <h2>Built in the open, and easy to help with</h2>
        <p className="section-lead">
          New to open source? You are welcome here. Every contribution below is small and has a guide.
        </p>
      </FadeContent>
      <div className="grid three">
        {CONTRIBUTE.map((c, i) => (
          <FadeContent key={c.title} duration={0.7} delay={i * 0.08}>
            <SpotlightCard className="card card-link" spotlightColor={SPOT}>
              <h3>{c.title}</h3>
              <p>{c.text}</p>
              <a className="text-link" href={c.href} target="_blank" rel="noreferrer">
                {c.cta} <span aria-hidden="true">→</span>
              </a>
            </SpotlightCard>
          </FadeContent>
        ))}
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="wrap closing">
      <FadeContent blur duration={0.9}>
        <h2>Start in one line</h2>
        <div className="install center" role="group" aria-label="Install command">
          <code>
            <span className="prompt" aria-hidden="true">$</span> {INSTALL_COMMAND}
          </code>
          <CopyButton text={INSTALL_COMMAND} label="Copy" />
        </div>
        <p className="fine">
          Python 3.9 or newer.{' '}
          <a href={PYPI} target="_blank" rel="noreferrer">View on PyPI</a>
        </p>
      </FadeContent>
    </section>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer-in">
        <p>
          © {new Date().getFullYear()} Open Finance Toolkit. MIT licensed. Not financial advice.
        </p>
        <nav aria-label="Footer">
          <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
          <a href={PYPI} target="_blank" rel="noreferrer">PyPI</a>
          <a href={`${REPO}/blob/main/CHANGELOG.md`} target="_blank" rel="noreferrer">Changelog</a>
          <a href={`${REPO}/blob/main/CONTRIBUTING.md`} target="_blank" rel="noreferrer">Contributing</a>
        </nav>
        <p className="credit">
          Motion components from{' '}
          <a href="https://reactbits.dev" target="_blank" rel="noreferrer">React Bits</a>.
        </p>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <>
      <a className="skip" href="#features">Skip to content</a>
      <Nav />
      <main>
        <Hero />
        <Stats />
        <Features />
        <How />
        <Banks />
        <Demo />
        <Contribute />
        <Closing />
      </main>
      <Footer />
    </>
  );
}
