import systems from '../data/systems.json';
import mistakes from '../data/mistakes.json';
import metrics from '../data/metrics.json';

interface Doc {
  kind: string;
  title: string;
  description: string;
  url: string;
  keywords?: string;
}

const slug = (t: string) =>
  t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

const page = (title: string, description: string, url: string, kind: string): Doc => ({
  kind,
  title,
  description,
  url,
});

const documents: Doc[] = [
  page('The dashboard', 'Thirteen numbers that decide most of it — targets first, justification second.', '/', 'Dashboard'),
  page('The calculator', 'Enter your profile; the protocol computes your bands, targets and cutoffs.', '/calculator', 'Dashboard'),
  page('The twelve-week plan', 'Daily anchors, a baseline fortnight, and twelve weeks of tasks.', '/plan', 'Plan'),
  page('Tracking logs', 'Blank logs: measurements, blood panels, symptoms, hair, medications.', '/tracking', 'Tracking'),
  page('The profile sheet', 'The single input sheet that drives every filter and target.', '/profile', 'Profile'),
  page('About this protocol', 'The tagging system, the evidence grades, and the primary references.', '/about', 'About'),
  page('Common mistakes', 'The habits that quietly undo everything else — with verdicts.', '/mistakes', 'Mistakes'),
];

for (const s of systems) {
  const name = s.slug.split('-').map((w: string) => (w[0] ?? '').toUpperCase() + w.slice(1)).join(' & ');
  documents.push(page(name, s.blurb, `/systems/${s.slug}`, 'System'));
  for (const sec of s.sections) {
    const anchor = `/systems/${s.slug}#s-${slug(sec.title)}`;
    documents.push({
      kind: 'Section',
      title: sec.title,
      description: sec.intro[0] ?? name,
      url: anchor,
      keywords: name,
    });
    for (const row of sec.rows) {
      const text = row.filter(Boolean).join(' — ');
      if (!text) continue;
      documents.push({
        kind: 'Row',
        title: row[0] ?? sec.title,
        description: text.length > 180 ? text.slice(0, 177) + '…' : text,
        url: anchor,
        keywords: sec.title,
      });
    }
  }
}

for (const sec of mistakes.sections) {
  documents.push({
    kind: 'Mistakes',
    title: sec.title,
    description: sec.intro[0] ?? 'Common mistakes',
    url: `/mistakes#m-${slug(sec.title)}`,
  });
  for (const row of sec.rows) {
    const text = row.filter(Boolean).join(' — ');
    if (!text) continue;
    documents.push({
      kind: 'Verdict',
      title: row[0] ?? sec.title,
      description: text.length > 180 ? text.slice(0, 177) + '…' : text,
      url: `/mistakes#m-${slug(sec.title)}`,
      keywords: sec.title,
    });
  }
}

for (const m of metrics) {
  documents.push({
    kind: 'Metric',
    title: m.metric,
    description: `${m.target} — ${m.why}`,
    url: '/#',
    keywords: 'dashboard',
  });
}

export const GET = () =>
  new Response(JSON.stringify({ documents }), {
    headers: { 'Content-Type': 'application/json' },
  });
