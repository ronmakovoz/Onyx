import { PageHeader, SectionTitle } from "../components/UI";

const sources = ["Sales playbooks", "Call recordings", "Product decks", "LMS courses", "Salesforce", "HubSpot", "Zoom", "Custom content"];
const intelligence = ["Generate scenarios", "Build AI personas", "Define scoring", "Personalize feedback"];
const outcomes = [
  ["AI Role Plays", "Realistic 1:1, group, and chat conversations", "#ff7452"],
  ["Courses", "Content, quizzes, and practice in one path", "#ffc928"],
  ["AI Coaching", "Objective scores and personalized feedback", "#6c4df6"],
  ["Insights", "Progress, trends, and knowledge gaps", "#00a98f"],
  ["Deal Coach", "Guidance for live opportunities and next steps", "#2c8cff"],
  ["Global Scale", "30+ languages on any browser or device", "#b886ff"],
] as const;

export default function IntegrationPage() {
  return (
    <div>
      <PageHeader title="How Second Nature Connects" subtitle="Bring existing content and systems into one AI-powered practice, coaching, and insights loop" />
      <section className="card architecture">
        <div className="architecture-column sources"><span>01 · CONNECT</span><h2>Content &amp; systems</h2><p>Use the material and workflows your revenue teams already trust.</p><div>{sources.map((source) => <b key={source}>{source}</b>)}</div></div>
        <div className="flow-arrow"><span>CONTEXT</span><i>→</i></div>
        <div className="architecture-column graph"><span>02 · CREATE</span><h2>Second Nature AI</h2><p>Turn source material into realistic practice and objective evaluation.</p><div>{intelligence.map((item, index) => <b key={item}><i>{index + 1}</i>{item}</b>)}</div><em>Scenario generator · AI personas · Analysis</em></div>
        <div className="flow-arrow"><span>IMPACT</span><i>→</i></div>
        <div className="architecture-column outcomes"><span>03 · PRACTICE &amp; IMPROVE</span><h2>Readiness outcomes</h2><p>Scale practice, prove skill, and focus managers where they matter most.</p><div>{outcomes.map(([name, description, color]) => <article key={name} style={{ borderLeftColor: color }}><strong>{name}</strong><small>{description}</small></article>)}</div></div>
      </section>

      <SectionTitle meta="the operating model">Four steps to value</SectionTitle>
      <section className="steps-grid"><article><span>01</span><h3>Bring your content</h3><p>Upload playbooks, decks, recordings, or course material and connect the systems already in use.</p></article><article><span>02</span><h3>Generate practice</h3><p>Build personas, scenarios, evaluation topics, and full role-play courses in minutes.</p></article><article><span>03</span><h3>Practice &amp; coach</h3><p>Give every learner 24/7 private practice with immediate objective feedback in 30+ languages.</p></article><article><span>04</span><h3>Measure &amp; improve</h3><p>Track progress, certification, performance trends, and knowledge gaps from manager dashboards.</p></article></section>
      <p className="source-note">Platform mapping reflects current public Second Nature product positioning. Dashboard metrics and customer records are synthetic.</p>
    </div>
  );
}
