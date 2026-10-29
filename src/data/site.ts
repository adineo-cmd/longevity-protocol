export const site = {
  name: 'The Longevity Protocol',
  shortName: 'Longevity Protocol',
  url: 'https://longevity-protocol.example.com',
  tagline: 'One body, kept in working order.',
  description:
    'An evidence-graded operating manual for one body: biomarkers, hair, skin, sleep, nutrition and presence — every row carries its evidence grade and its source.',
  lastReviewed: 'October 2026',
  nav: [
    { href: '/systems/appearance', label: 'Appearance' },
    { href: '/systems/body-nutrition', label: 'Body & Nutrition' },
    { href: '/systems/sleep-recovery', label: 'Sleep' },
    { href: '/systems/longevity-health', label: 'Longevity' },
    { href: '/systems/presence-style', label: 'Presence' },
    { href: '/mistakes', label: 'Mistakes' },
    { href: '/plan', label: 'Plan' },
    { href: '/about', label: 'About' },
  ],
  footerNav: [
    { href: '/profile', label: 'Profile sheet' },
    { href: '/tracking', label: 'Tracking logs' },
    { href: '/plan', label: 'Twelve-week plan' },
    { href: '/about', label: 'Grades & references' },
  ],
  disclaimer:
    'Educational reference, not medical advice. Nothing here diagnoses or treats anything. Rows graded Rx are prescription-only: start, dose and stop belong to a clinician.',
};

export const gradeLegend = [
  { grade: 'A', label: 'multiple RCTs or a meta-analysis' },
  { grade: 'B', label: 'at least one RCT or a strong physiological case' },
  { grade: 'C', label: 'observational, mechanistic or expert consensus' },
  { grade: 'Rx', label: 'prescription-only — a clinician decides' },
];
